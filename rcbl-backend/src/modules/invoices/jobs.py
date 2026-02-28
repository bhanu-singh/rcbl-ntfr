"""arq background job: OCR processing pipeline.

Called by the arq worker (src/worker.py) when a new UploadItem is enqueued.

Job flow:
  1. Load UploadItem from DB
  2. Mark status → "processing"
  3. Download file bytes from S3
  4. Call OCR client (OpenAI Vision with fallback)
  5. Update item with OCR results and set status (ready | review_pending | failed)
  6. Increment batch counters and finalise batch status when all items are done
"""

import uuid

import structlog

from src.core.observability import ocr_jobs_total

logger = structlog.get_logger(__name__)


async def process_ocr(ctx: dict, item_id: str, company_id: str) -> None:
    """
    arq job entrypoint. ctx["db_session"] is injected by WorkerSettings.startup.
    Uses a plain (non-tenant-scoped) session since the worker runs outside a request.
    """
    from src.clients import ocr_client, s3_client
    from src.config import settings
    from src.db.session import async_session_factory
    from src.modules.invoices import repository
    from src.modules.invoices.models import ItemStatus

    item_uuid = uuid.UUID(item_id)
    uuid.UUID(company_id)

    item = None  # declared here so error handler can safely reference it
    async with async_session_factory() as db:
        try:
            # ── Step 1: Load item ──────────────────────────────────────────────
            item = await repository.get_item_by_id(db, item_uuid)
            if item is None:
                logger.error("ocr.item_not_found", item_id=item_id)
                return

            logger.info("ocr.started", item_id=item_id, file_name=item.file_name)

            # ── Step 2: Mark processing ────────────────────────────────────────
            await repository.update_item_status(db, item_uuid, ItemStatus.processing)
            await db.commit()

            # ── Step 3: Download from S3 ───────────────────────────────────────
            file_bytes = await s3_client.download_file(item.file_url)

            # ── Step 4: Run OCR ────────────────────────────────────────────────
            result = await ocr_client.extract_invoice(file_bytes)

            # ── Step 5: Determine status ───────────────────────────────────────
            if result.confidence >= settings.OCR_CONFIDENCE_THRESHOLD:
                new_status = ItemStatus.ready
            else:
                new_status = ItemStatus.review_pending

            ocr_data = {
                "invoice_number": result.invoice_number,
                "amount": str(result.amount) if result.amount is not None else None,
                "currency": result.currency,
                "invoice_date": result.invoice_date,
                "due_date": result.due_date,
                "vendor_name": result.vendor_name,
                "raw_text": result.raw_text,
            }

            await repository.update_item_ocr_result(
                db,
                item_uuid,
                ocr_extracted_data=ocr_data,
                ocr_confidence_score=result.confidence,
                ocr_processing_time_ms=result.processing_ms,
                status=new_status,
            )
            await db.commit()

            # ── Step 6: Update batch counters ──────────────────────────────────
            await repository.increment_batch_counters(db, item.batch_id, success=True)
            await db.commit()

            ocr_jobs_total.labels(status="success").inc()
            logger.info(
                "ocr.completed",
                item_id=item_id,
                status=new_status.value,
                confidence=result.confidence,
                processing_ms=result.processing_ms,
            )

        except Exception as exc:
            logger.error("ocr.failed", item_id=item_id, error=str(exc), exc_info=True)
            try:
                async with async_session_factory() as err_db:
                    await repository.update_item_failed(err_db, item_uuid, error_message=str(exc))
                    if item is not None:
                        await repository.increment_batch_counters(
                            err_db, item.batch_id, success=False
                        )
                    await err_db.commit()
            except Exception as inner_exc:
                logger.error("ocr.error_handler_failed", error=str(inner_exc))

            ocr_jobs_total.labels(status="failed").inc()
            raise
