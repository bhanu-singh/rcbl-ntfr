"""Invoice upload + OCR router.

All endpoints require JWT authentication. The DB session passed to service
functions is tenant-scoped (RLS context variable set via get_tenant_db).
"""

import asyncio
import json
import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_arq_pool, get_current_user, get_tenant_db
from src.core.tenant import require_company_id
from src.modules.auth.models import User
from src.modules.invoices import service
from src.modules.invoices.schemas import (
    AcceptItemRequest,
    AcceptItemResponse,
    BulkUploadResponse,
    SingleUploadResponse,
    UploadBatchDetailResponse,
    UploadBatchResponse,
    UploadItemResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


# ── Upload ─────────────────────────────────────────────────────────────────────


@router.post(
    "/upload",
    response_model=SingleUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a single PDF for OCR processing",
)
async def upload_single(
    file: Annotated[UploadFile, File(description="PDF or image file, max 20 MB")],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
    arq_pool=Depends(get_arq_pool),
) -> SingleUploadResponse:
    company_id = require_company_id()
    structlog.contextvars.bind_contextvars(company_id=str(company_id), user_id=str(current_user.id))
    return await service.upload_single(db, company_id, current_user.id, file, arq_pool)


@router.post(
    "/upload/bulk",
    response_model=BulkUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload multiple PDFs for batch OCR processing",
)
async def upload_bulk(
    files: Annotated[list[UploadFile], File(description="Multiple PDF or image files, each max 20 MB")],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
    arq_pool=Depends(get_arq_pool),
) -> BulkUploadResponse:
    company_id = require_company_id()
    structlog.contextvars.bind_contextvars(company_id=str(company_id), user_id=str(current_user.id))
    return await service.upload_bulk(db, company_id, current_user.id, files, arq_pool)


# ── Batches ────────────────────────────────────────────────────────────────────


@router.get(
    "/upload/batches",
    response_model=list[UploadBatchResponse],
    summary="List upload batches (paginated)",
)
async def list_batches(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
) -> list[UploadBatchResponse]:
    company_id = require_company_id()
    batches = await service.list_batches(db, company_id, offset=offset, limit=limit)
    return [UploadBatchResponse.model_validate(b) for b in batches]


@router.get(
    "/upload/batches/{batch_id}",
    response_model=UploadBatchDetailResponse,
    summary="Get batch detail with all items",
)
async def get_batch(
    batch_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
) -> UploadBatchDetailResponse:
    company_id = require_company_id()
    batch = await service.get_batch(db, batch_id, company_id, with_items=True)
    return UploadBatchDetailResponse.model_validate(batch)


# ── Items ──────────────────────────────────────────────────────────────────────


@router.get(
    "/upload/items/{item_id}",
    response_model=UploadItemResponse,
    summary="Get single item detail including OCR extracted data",
)
async def get_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
) -> UploadItemResponse:
    company_id = require_company_id()
    item = await service.get_item(db, item_id, company_id)
    return UploadItemResponse.model_validate(item)


@router.patch(
    "/upload/items/{item_id}/accept",
    response_model=AcceptItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Accept OCR result and create an Invoice record",
)
async def accept_item(
    item_id: uuid.UUID,
    payload: AcceptItemRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
) -> AcceptItemResponse:
    company_id = require_company_id()
    return await service.accept_item(db, item_id, company_id, payload)


@router.patch(
    "/upload/items/{item_id}/reject",
    response_model=UploadItemResponse,
    summary="Reject an OCR-processed item",
)
async def reject_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
) -> UploadItemResponse:
    company_id = require_company_id()
    return await service.reject_item(db, item_id, company_id)


# ── SSE Progress Stream ────────────────────────────────────────────────────────


@router.get(
    "/upload/batches/{batch_id}/progress",
    summary="Real-time batch progress via Server-Sent Events",
    response_class=StreamingResponse,
)
async def batch_progress(
    batch_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
) -> StreamingResponse:
    """
    SSE endpoint that polls the batch until completed/failed.
    Each event contains the current batch counters and any changed items.
    Client connects once and receives updates as OCR jobs complete.
    """
    company_id = require_company_id()

    async def event_generator():
        from src.modules.invoices import repository
        from src.modules.invoices.models import BatchStatus

        terminal_statuses = {BatchStatus.completed.value, BatchStatus.failed.value}
        prev_processed = -1

        for _ in range(300):  # poll up to ~5 minutes (300 x 1s)
            batch = await repository.get_batch_by_id(
                db, batch_id, company_id, with_items=True
            )
            if batch is None:
                yield _sse_event({"error": "batch not found"}, event="error")
                return

            if batch.processed_files != prev_processed:
                prev_processed = batch.processed_files

                payload = {
                    "batch_id": str(batch_id),
                    "status": batch.status,
                    "total_files": batch.total_files,
                    "processed_files": batch.processed_files,
                    "successful_files": batch.successful_files,
                    "failed_files": batch.failed_files,
                    "items": [
                        {
                            "item_id": str(item.id),
                            "file_name": item.file_name,
                            "status": item.status,
                            "confidence": float(item.ocr_confidence_score)
                            if item.ocr_confidence_score is not None
                            else None,
                        }
                        for item in (batch.items or [])
                    ],
                }
                yield _sse_event(payload, event="progress")

            if batch.status in terminal_statuses:
                yield _sse_event({"status": batch.status}, event="done")
                return

            await asyncio.sleep(1)

        yield _sse_event({"reason": "timeout"}, event="timeout")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering
        },
    )


def _sse_event(data: dict, event: str = "message") -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
