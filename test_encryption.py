from src.core.encryption import Encryption as sentry

def test_encrypt_decrypt():
    enc = sentry()
    password = "password"
    hash = enc.hash_password(password)
    if enc.verify_password(hash, password):
        print("Password is correct")
    else:
        print("Password is incorrect")

test_encrypt_decrypt()