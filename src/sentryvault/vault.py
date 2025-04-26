import json
import os
from .crypto import Cryptify

class PasswordVault:
    def __init__(self, passphrase, vault_path="vault.enc"):
        self.passphrase = passphrase
        self.vault_path = vault_path
        self.crypt = Cryptify(passphrase)

        if not os.path.exists(vault_path):
            self._write_data({})  # create empty vault

    def _read_data(self):
        with open(self.vault_path, "rb") as f:
            raw = f.read()
        salt = raw[:16]
        cipher = raw[16:]

        temp = Cryptify(self.passphrase, salt)
        decrypted = temp.cipher.decrypt(cipher)
        return json.loads(decrypted.decode())

    def _write_data(self, data):
        plaintext = json.dumps(data).encode()
        encrypted = self.crypt.salt + self.crypt.cipher.encrypt(plaintext)
        with open(self.vault_path, "wb") as f:
            f.write(encrypted)

    def add_entry(self, site, username, password):
        data = self._read_data()
        data[site] = {"username": username, "password": password}
        self._write_data(data)

    def get_entry(self, site):
        data = self._read_data()
        return data.get(site)

    def list_entries(self):
        return list(self._read_data().keys())

    def delete_entry(self, site):
        data = self._read_data()
        if site in data:
            del data[site]
            self._write_data(data)
            return True
        return False
def verify_passphrase(self, passphrase: str) -> bool:
    """Verify if the given passphrase can decrypt the vault."""
    try:
        with open(self.vault_path, "rb") as f:
            salt = f.read(16)
            encrypted_data = f.read()
        temp_crypt = Cryptify(passphrase, salt)
        decrypted = temp_crypt.decrypt(encrypted_data)
        json.loads(decrypted)  # Sanity check: is it valid JSON?
        return True
    except Exception:
        return False
