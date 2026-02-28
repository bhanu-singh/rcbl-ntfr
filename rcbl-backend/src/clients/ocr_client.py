"""OCR client: OpenAI Vision as primary, structured extraction with fallback."""

import base64
import json
import time
from dataclasses import dataclass

import httpx
import structlog

from src.config import settings

logger = structlog.get_logger(__name__)

OCR_SYSTEM_PROMPT = """\
You are an invoice data extraction specialist. Extract structured data from the invoice image.
Return ONLY valid JSON with these exact fields (use null for any missing field):
{
  "invoice_number": "string or null",
  "amount": "number or null (numeric value only)",
  "currency": "3-letter ISO code or null",
  "invoice_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "vendor_name": "string or null",
  "confidence": "number between 0 and 1 representing your confidence in the extraction"
}
Do not include any explanation outside the JSON object.
"""


@dataclass
class OCRResult:
    invoice_number: str | None
    amount: float | None
    currency: str | None
    invoice_date: str | None
    due_date: str | None
    vendor_name: str | None
    raw_text: str | None
    confidence: float
    processing_ms: int


async def extract_invoice(file_bytes: bytes) -> OCRResult:
    """
    Primary: OpenAI GPT-4o Vision.
    On failure: returns a low-confidence placeholder so the item
    is routed to review_pending rather than crashing.
    """
    start = time.monotonic()
    try:
        result = await _openai_extract(file_bytes)
        result.processing_ms = int((time.monotonic() - start) * 1000)
        return result
    except Exception as exc:
        logger.warning("ocr.openai_failed", error=str(exc))
        processing_ms = int((time.monotonic() - start) * 1000)
        return OCRResult(
            invoice_number=None,
            amount=None,
            currency=None,
            invoice_date=None,
            due_date=None,
            vendor_name=None,
            raw_text=None,
            confidence=0.0,
            processing_ms=processing_ms,
        )


async def _openai_extract(file_bytes: bytes) -> OCRResult:
    b64 = base64.b64encode(file_bytes).decode()
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": OCR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:application/pdf;base64,{b64}",
                            "detail": "high",
                        },
                    }
                ],
            },
        ],
        "max_tokens": 512,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()

    data = response.json()
    raw_content = data["choices"][0]["message"]["content"]
    parsed = json.loads(raw_content)

    confidence = float(parsed.get("confidence") or 0.0)
    confidence = max(0.0, min(1.0, confidence))

    amount_raw = parsed.get("amount")
    amount = float(amount_raw) if amount_raw is not None else None

    return OCRResult(
        invoice_number=parsed.get("invoice_number"),
        amount=amount,
        currency=parsed.get("currency"),
        invoice_date=parsed.get("invoice_date"),
        due_date=parsed.get("due_date"),
        vendor_name=parsed.get("vendor_name"),
        raw_text=raw_content,
        confidence=confidence,
        processing_ms=0,  # filled by caller
    )
