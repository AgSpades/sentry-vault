from cryptography.fernet import Fernet
from argon2.low_level import hash_secret_raw, Type
import base64
import os

class Cryptify:
    def __init__(self, passphrase, salt=None):
        self.salt = salt or os.urandom(16)  # Use provided salt or generate a new one
        self.key = self._derive_key(passphrase, self.salt)
        self.cipher = Fernet(self.key)

    def _derive_key(self, passphrase, salt):
        # Secure key derivation using Argon2id
        raw_key = hash_secret_raw(
            secret=passphrase.encode(),
            salt=salt,
            time_cost=3,        # 3 iterations
            memory_cost=512000, # 512MB RAM usage
            parallelism=8,
            hash_len=32,
            type=Type.ID         # Use Argon2id
        )
        return base64.urlsafe_b64encode(raw_key)  # Fernet requires base64-encoded key

    def encrypt(self, text):
        return self.cipher.encrypt(text.encode())

    def decrypt(self, ciphertext):
        return self.cipher.decrypt(ciphertext).decode()
