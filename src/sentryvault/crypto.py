# src/sentryvault/cryptify.py
from cryptography.fernet import Fernet
from argon2.low_level import hash_secret_raw, Type
import base64
import os

class Cryptify:
    def __init__(self, passphrase, salt=None):
        self.passphrase = passphrase  # 🔧 Needed for decrypt_file
        self.salt = salt or os.urandom(16)
        self.key = self._derive_key(passphrase, self.salt)
        self.cipher = Fernet(self.key)

    def _derive_key(self, passphrase, salt):
        raw_key = hash_secret_raw(
            secret=passphrase.encode(),
            salt=salt,
            time_cost=3,
            memory_cost=512000,
            parallelism=8,
            hash_len=32,
            type=Type.ID
        )
        return base64.urlsafe_b64encode(raw_key)

    def encrypt(self, text):
        return self.cipher.encrypt(text.encode())

    def decrypt(self, ciphertext):
        return self.cipher.decrypt(ciphertext).decode()

    def encrypt_file(self, input_path, output_path):
        with open(input_path, "rb") as f:
            plaintext = f.read()
        ciphertext = self.cipher.encrypt(plaintext)

        # Save: [salt (16 bytes)] + [ciphertext]
        with open(output_path, "wb") as f:
            f.write(self.salt + ciphertext)

    def decrypt_file(self, input_path, output_path):
        with open(input_path, "rb") as f:
            data = f.read()
        salt = data[:16]
        ciphertext = data[16:]

        temp = Cryptify(self.passphrase, salt)
        plaintext = temp.cipher.decrypt(ciphertext)

        with open(output_path, "wb") as f:
            f.write(plaintext)
