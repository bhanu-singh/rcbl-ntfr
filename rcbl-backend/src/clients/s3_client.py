"""Async S3 / MinIO client wrapper using aioboto3."""

import hashlib
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aioboto3
import structlog

from src.config import settings

logger = structlog.get_logger(__name__)

_session = aioboto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


@asynccontextmanager
async def _s3_resource() -> AsyncGenerator:
    async with _session.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        region_name="us-east-1",
    ) as client:
        yield client


async def upload_file(
    file_bytes: bytes,
    key: str,
    content_type: str = "application/pdf",
) -> str:
    """Upload bytes to S3 and return the object key."""
    async with _s3_resource() as s3:
        await s3.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
    logger.info("s3.uploaded", key=key, size_bytes=len(file_bytes))
    return key


async def download_file(key: str) -> bytes:
    """Download object and return raw bytes."""
    async with _s3_resource() as s3:
        response = await s3.get_object(Bucket=settings.S3_BUCKET, Key=key)
        body = await response["Body"].read()
    logger.info("s3.downloaded", key=key, size_bytes=len(body))
    return body


async def get_presigned_url(key: str, expires_in: int = 3600) -> str:
    """Generate a presigned GET URL (default 1 hour)."""
    async with _s3_resource() as s3:
        url = await s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": key},
            ExpiresIn=expires_in,
        )
    return url


async def delete_object(key: str) -> None:
    async with _s3_resource() as s3:
        await s3.delete_object(Bucket=settings.S3_BUCKET, Key=key)
    logger.info("s3.deleted", key=key)


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


async def ensure_bucket_exists() -> None:
    """Create the bucket if it doesn't exist (used at startup in dev)."""
    async with _s3_resource() as s3:
        try:
            await s3.head_bucket(Bucket=settings.S3_BUCKET)
        except Exception:
            await s3.create_bucket(Bucket=settings.S3_BUCKET)
            logger.info("s3.bucket_created", bucket=settings.S3_BUCKET)


async def head_bucket(bucket: str) -> bool:
    """Check if a bucket exists and is accessible."""
    async with _s3_resource() as s3:
        await s3.head_bucket(Bucket=bucket)
    return True
