from pathlib import Path

import pytest
from cryptography.fernet import InvalidToken

from sentryvault.crypto import Cryptify


def test_encrypt_decrypt_roundtrip_text():
    crypt = Cryptify("correct horse battery staple")
    ciphertext = crypt.encrypt("secret-value")

    # Reuse the same salt with a new instance to mimic reading encrypted data later.
    recovered = Cryptify("correct horse battery staple", crypt.salt).decrypt(ciphertext)
    assert recovered == "secret-value"


def test_decrypt_with_wrong_passphrase_raises_invalid_token():
    crypt = Cryptify("right-passphrase")
    ciphertext = crypt.encrypt("top-secret")

    with pytest.raises(InvalidToken):
        Cryptify("wrong-passphrase", crypt.salt).decrypt(ciphertext)


def test_encrypt_decrypt_file_roundtrip(tmp_path: Path):
    plain_path = tmp_path / "plain.txt"
    enc_path = tmp_path / "vault.enc"
    dec_path = tmp_path / "plain.out.txt"

    plain_bytes = b"file payload for sentry vault tests"
    plain_path.write_bytes(plain_bytes)

    crypt = Cryptify("file-pass")
    crypt.encrypt_file(str(plain_path), str(enc_path))
    crypt.decrypt_file(str(enc_path), str(dec_path))

    assert dec_path.read_bytes() == plain_bytes
    assert enc_path.read_bytes()[:16] == crypt.salt
