from argon2 import PasswordHasher
import os
from cryptography.fernet import Fernet

class Encryption:
    def __init__(self):
        self.ph = PasswordHasher()

    def hash_password(self, password):
        return self.ph.hash(password)

    def verify_password(self, hash, password):
        try:
            self.ph.verify(hash, password)
            return True
        except:
            return False
    
