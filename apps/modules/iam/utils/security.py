from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from ..domain import TokenType

import base64
import logging
import secrets
from datetime import timedelta
from uuid import uuid4

import jwt
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext

from config.dev import settings
from modules.shared_kernel.utils import current_datetime

from ..domain.exceptions import DecryptionError, InvalidTokenError, TokenExpiredError

# Хеширование паролей
MEMORY_COST = 100  # Размер выделяемой памяти в mb
TIME_COST = 2
PARALLELISM = 2
SALT_SIZE = 16
ROUNDS = 14  # Количество раундов для хеширования

logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    default="argon2",
    argon2__memory_cost=MEMORY_COST,
    argon2__time_cost=TIME_COST,
    argon2__parallelism=PARALLELISM,
    argon2__salt_size=SALT_SIZE,
    bcrypt__rounds=ROUNDS,
    deprecated="auto"
)


def hash_secret(secret: str) -> str:
    """Хэширует секрет (password, client_secret, etc...)"""
    return pwd_context.hash(secret)


def verify_secret(plain_secret: str, hashed_secret: str) -> bool:
    """Сверяет ожидаемый пароль с хэшем пароля"""
    return pwd_context.verify(plain_secret, hashed_secret)


def issue_token(
        token_type: "TokenType",
        payload: dict[str, Any],
        expires_in: timedelta,
) -> str:
    """Подписывает токен.

    :param token_type: Тип токен, например: ACCESS, REFRESH.
    :param payload: Дополнительные данные, которые нужно закодировать в токен.
    :param expires_in: Временной промежуток через который истекает токен.
    :return Подписанный токен.
    """
    now = current_datetime()
    expires_at = now + expires_in
    payload.update({
        "exp": expires_at.timestamp(),
        "iat": now.timestamp(),
        "token_type": token_type.value,
        "jti": str(uuid4())
    })
    return jwt.encode(
        payload=payload,
        key=settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm
    )


def decode_token(token: str) -> dict[str, Any]:
    """Декодирует токен.

    :param token: Токен, который нужно декодировать.
    :return: Словарь с информацией из токена.
    :exception InvalidTokenError: Токен не был подписан этим сервисом.
    """
    try:
        return jwt.decode(
            token,
            key=settings.jwt.secret_key,
            algorithms=[settings.jwt.algorithm],
            options={"verify_aud": False}
        )
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token expired!") from None
    except jwt.PyJWTError:
        raise InvalidTokenError("Invalid token!") from None


class StringEncryptor:
    """Шифрование и дешифрование строк используя AES - алгоритмы"""

    TAG_LENGTH = 16

    def __init__(
            self,
            encryption_key: str,
            key_length: int,
            iterations: int = 100_000,
    ) -> None:
        """
        :param encryption_key: Ключ шифрования. Если None, будет использован из env.
        :param key_length: Длина ключа в байтах (32 для AES-256).
        :param iterations: Количество итераций для PBKDF2.
        """

        self._encryption_key = encryption_key.encode("utf-8")
        self._key_length = key_length
        self._iterations = iterations

    @staticmethod
    def _generate_salt() -> bytes:
        """Генерация случайной соли"""

        return secrets.token_bytes(16)

    def _ensure_aes_key_length(self, key: bytes) -> bytes:
        """Обеспечение правильной длины ключа для AES"""

        if len(key) == self._key_length:
            return key
        return (
            key.ljust(32, b"\x00")
            if len(key) < self._key_length
            else key[:self._key_length]
        )

    def _derive_key(self, salt: bytes) -> bytes:
        """Деривация ключа (KDF, Key Derivation Function)"""

        kbf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self._key_length,
            salt=salt,
            iterations=self._iterations,
            backend=default_backend()
        )
        return kbf.derive(self._encryption_key)

    def encrypt(self, string: str, context: str | None = None) -> tuple[str, bytes, bytes]:
        """Шифрование строки с использованием AES-GCM.

        :param string: Строка, которую нужно зашифровать.
        :param context: Контекстная информация для зашиты от подмены.
        :returns: [encrypted_base64, salt, nonce]
            - зашифрованная строка в base64 формате
            - соль (не секрет)
            - одноразовое число (вектор инициализации, не секрет)
        """

        string_to_encrypt = string if context is None else f"{context}:{string}"
        string_to_encrypt = string_to_encrypt.encode("utf-8")
        salt = self._generate_salt()
        nonce = secrets.token_bytes(12)
        derived_key = self._derive_key(salt)
        aes_key = self._ensure_aes_key_length(derived_key)
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        # Шифрование строки
        ciphertext = encryptor.update(string_to_encrypt) + encryptor.finalize()
        # Объединяем ciphertext и tag
        encrypted_bytes = ciphertext + encryptor.tag  # Получение authentication tag
        # Кодирование в base64 для хранения в БД
        encrypted_base64 = base64.urlsafe_b64encode(encrypted_bytes).decode("utf-8")
        return encrypted_base64, salt, nonce

    def decrypt(
            self,
            encrypted_string: str,
            salt: bytes,
            nonce: bytes,
            expected_context: str | None = None,
    ) -> str:
        """Дешифрование строки.

        :param encrypted_string: Зашифрованная строка.
        :param salt: Соль, использованная при шифровании.
        :param nonce: Nonce, использованный при шифровании.
        :param expected_context: Ожидаемый контекст для проверки.
        :returns: Расшифрованная строка.
        """

        try:
            encrypted_string = base64.urlsafe_b64decode(encrypted_string)
            ciphertext = encrypted_string[:-self.TAG_LENGTH]
            tag = encrypted_string[-self.TAG_LENGTH:]
            # Деривация ключа
            derived_key = self._derive_key(salt)
            aes_key = self._ensure_aes_key_length(derived_key)
            # Создание cipher для AES-GCM
            cipher = Cipher(
                algorithms.AES(aes_key), modes.GCM(nonce, tag), backend=default_backend()
            )
            decryptor = cipher.decryptor()
            # Дешифрование
            decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            decrypted_text = decrypted_bytes.decode("utf-8")
            if expected_context is not None:
                if ":" not in decrypted_text:
                    raise DecryptionError("No context separator found in decrypted text")
                context, plaintext = decrypted_text.split(":", maxsplit=1)
                if context != expected_context:
                    raise DecryptionError(
                        f"Context mismatch. Expected: {expected_context}, got: {context}"
                    )
                return plaintext
        except InvalidTag as e:
            logger.critical("Decryption failed: Invalid authentication tag", exc_info=True)
            raise DecryptionError(
                "Authentication failed - data may have been tampered with"
            ) from e
        else:
            return decrypted_text


string_encryptor: Final[StringEncryptor] = StringEncryptor(
    encryption_key=settings.encryption.key,
    key_length=settings.encryption.key_length,
    iterations=settings.encryption.iterations,
)
