"""Tests for OCR background job processing.

These tests verify the arq job logic.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── OCR Job Unit Tests ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ocr_job_item_not_found_returns_early() -> None:
    """OCR job should return early when item is not found."""
    from src.modules.invoices.jobs import process_ocr
    
    # Create mock repository that returns None
    mock_repo = MagicMock()
    mock_repo.get_item_by_id = AsyncMock(return_value=None)
    
    mock_db = AsyncMock()
    
    # Patch at the source module level where imports happen
    with (
        patch("src.modules.invoices.repository.get_item_by_id", mock_repo.get_item_by_id),
        patch("src.db.session.async_session_factory") as mock_factory,
    ):
        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_db)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)
        mock_factory.return_value = mock_session_cm
        
        # Should not raise, just return early
        await process_ocr({}, str(uuid.uuid4()), str(uuid.uuid4()))
        
        # Verify get_item_by_id was called
        mock_repo.get_item_by_id.assert_called_once()


@pytest.mark.asyncio
async def test_ocr_job_handles_exception_gracefully() -> None:
    """OCR job should catch exceptions and mark item as failed."""
    from src.modules.invoices.jobs import process_ocr
    
    mock_item = MagicMock()
    mock_item.id = uuid.uuid4()
    mock_item.file_name = "test.pdf"
    mock_item.file_url = "invoices/test.pdf"
    mock_item.batch_id = uuid.uuid4()
    
    mock_repo = MagicMock()
    mock_repo.get_item_by_id = AsyncMock(return_value=mock_item)
    mock_repo.update_item_status = AsyncMock()
    mock_repo.update_item_failed = AsyncMock()
    mock_repo.increment_batch_counters = AsyncMock()
    
    mock_s3 = MagicMock()
    mock_s3.download_file = AsyncMock(side_effect=Exception("S3 error"))
    
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    
    # Patch at source modules where imports happen inside process_ocr
    with (
        patch("src.modules.invoices.repository.get_item_by_id", mock_repo.get_item_by_id),
        patch("src.modules.invoices.repository.update_item_status", mock_repo.update_item_status),
        patch("src.modules.invoices.repository.update_item_failed", mock_repo.update_item_failed),
        patch("src.modules.invoices.repository.increment_batch_counters", mock_repo.increment_batch_counters),
        patch("src.clients.s3_client.download_file", mock_s3.download_file),
        patch("src.db.session.async_session_factory") as mock_factory,
    ):
        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_db)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)
        mock_factory.return_value = mock_session_cm
        
        # Should raise the exception after error handling
        with pytest.raises(Exception, match="S3 error"):
            await process_ocr({}, str(mock_item.id), str(uuid.uuid4()))
        
        # Verify error handling was called
        mock_repo.update_item_failed.assert_called_once()
