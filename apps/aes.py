from config.dev import settings
from modules.iam.utils.security import StringEncryptor

string_encryptor = StringEncryptor(
    encryption_key=settings.encryption.key,
    key_length=settings.encryption.key_length,
    iterations=settings.encryption.iterations,
)

apikey = "1234567890"

print(f"Исходный ключ: {apikey}")

encrypted_apikey, salt, nonce = string_encryptor.encrypt(apikey, context="hello")

print(f"Зашифрованный ключ: {encrypted_apikey}")

decrypted_apikey = string_encryptor.decrypt(
    encrypted_apikey, salt=salt, nonce=nonce, expected_context="hello"
)

print(f"Расшифрованный ключ: {decrypted_apikey}")
