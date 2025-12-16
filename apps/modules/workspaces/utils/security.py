import base64
import secrets


def generate_token() -> str:
    """Генерация криптографически стойкого токена (32 байта -> 43 символам base64)"""

    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
