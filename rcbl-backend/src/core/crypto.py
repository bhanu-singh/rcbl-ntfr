"""AES-256-GCM symmetric encryption for storing OAuth tokens and secrets.

Usage:
    ciphertext = encrypt_secret("my-plain-text-token")
    plain = decrypt_secret(ciphertext)
"""

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.config import settings

_KEY_BYTES = 32  # AES-256


def _derive_key() -> bytes:
    """Derive a 32-byte key from SECRET_KEY (padded/truncated)."""
    raw = settings.SECRET_KEY.encode()
    return (raw * (_KEY_BYTES // len(raw) + 1))[:_KEY_BYTES]


def encrypt_secret(plaintext: str) -> str:
    """Encrypt plaintext and return a base64url-encoded `nonce:ciphertext`."""
    key = _derive_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce recommended for GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    combined = nonce + ciphertext
    return base64.urlsafe_b64encode(combined).decode()


def decrypt_secret(encoded: str) -> str:
    """Decrypt a value produced by encrypt_secret."""
    key = _derive_key()
    aesgcm = AESGCM(key)
    combined = base64.urlsafe_b64decode(encoded.encode())
    nonce, ciphertext = combined[:12], combined[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
