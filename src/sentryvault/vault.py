import json
import os
import glob # Added for robust share file cleanup
from .crypto import Cryptify
from .sharding import Sharding # Import Sharding

class PasswordVault:
    def __init__(self, passphrase, vault_path="vault.enc", sharding_config=None):
        self.passphrase = passphrase
        self.vault_path = vault_path  # Base name for shares if sharding_config is present
        self.sharding_config = sharding_config
        self.crypt = Cryptify(passphrase) 

        vault_is_new = False
        if self.sharding_config:
            # For a sharded vault, consider it new if the first potential share file doesn't exist.
            # Assumes share files are named vault_path.s1, vault_path.s2, etc.
            first_share_path = f"{self.vault_path}.s1" # A simple heuristic
            if not os.path.exists(first_share_path):
                # More robust: check if any .s* file exists for this vault_path
                existing_share_files = glob.glob(f"{self.vault_path}.s[0-9]*")
                if not existing_share_files:
                    vault_is_new = True
        else:
            # For a non-sharded vault, it's new if the vault file doesn't exist.
            if not os.path.exists(self.vault_path):
                vault_is_new = True
        
        if vault_is_new:
            # Initialize with an empty dictionary. This will create the vault file(s).
            self._write_data({})

    def _read_data(self):
        raw_encrypted_data_with_salt = None

        if self.sharding_config:
            loaded_shares = []
            # Attempt to load all potential shares.
            for i in range(self.sharding_config['total_shares']):
                share_path = f"{self.vault_path}.s{i+1}"
                if os.path.exists(share_path):
                    try:
                        with open(share_path, "r") as f:
                            share_string = json.load(f) 
                        loaded_shares.append(share_string)
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Warning: Could not load or decode share {share_path}: {e}")
            
            if len(loaded_shares) < self.sharding_config['threshold']:
                raise ValueError(
                    f"Not enough shares to reconstruct secret. Found {len(loaded_shares)}, "
                    f"need {self.sharding_config['threshold']} for vault '{self.vault_path}'."
                )

            try:
                encrypted_data_hex = Sharding.combine_shares(loaded_shares)
                raw_encrypted_data_with_salt = bytes.fromhex(encrypted_data_hex)
            except Exception as e:
                raise ValueError(f"Failed to combine shares or decode hex: {e}")

        else: # Non-sharded vault
            if not os.path.exists(self.vault_path):
                return {} 
            
            with open(self.vault_path, "rb") as f:
                raw_encrypted_data_with_salt = f.read()
            
            if not raw_encrypted_data_with_salt: # Vault file exists but is empty
                return {}

        if len(raw_encrypted_data_with_salt) < 16: # Salt is 16 bytes
            raise ValueError("Vault data is corrupted or too short (missing salt).")

        salt = raw_encrypted_data_with_salt[:16]
        encrypted_payload = raw_encrypted_data_with_salt[16:]

        if not encrypted_payload:
            raise ValueError("Vault data is corrupted (missing encrypted payload).")

        temp_crypt = Cryptify(self.passphrase, salt)
        try:
            decrypted_bytes = temp_crypt.cipher.decrypt(encrypted_payload)
            return json.loads(decrypted_bytes.decode())
        except Exception as e:
            raise ValueError(f"Failed to decrypt or parse vault data. Incorrect passphrase or corrupted data: {e}")


    def _write_data(self, data):
        plaintext_bytes = json.dumps(data).encode()
        
        encrypted_payload = self.crypt.cipher.encrypt(plaintext_bytes)
        full_encrypted_data_with_salt = self.crypt.salt + encrypted_payload

        if self.sharding_config:
            secret_to_split_hex = full_encrypted_data_with_salt.hex()
            
            shares = Sharding.split_secret(
                secret_to_split_hex,
                self.sharding_config['total_shares'],
                self.sharding_config['threshold']
            )

            # Robust cleanup of any existing .sN files for this vault_path
            existing_share_files = glob.glob(f"{self.vault_path}.s[0-9]*")
            for esf in existing_share_files:
                try:
                    os.remove(esf)
                except OSError as e:
                    print(f"Warning: Could not remove old share file {esf}: {e}")
            
            for i, share_string in enumerate(shares):
                share_path = f"{self.vault_path}.s{i+1}"
                with open(share_path, "w") as f:
                    json.dump(share_string, f) 
            
            if os.path.exists(self.vault_path) and os.path.isfile(self.vault_path):
                try:
                    os.remove(self.vault_path)
                except OSError as e:
                    print(f"Warning: Could not remove non-sharded vault file {self.vault_path} after sharding: {e}")
        else: # Non-sharded vault
            with open(self.vault_path, "wb") as f:
                f.write(full_encrypted_data_with_salt)
            
            # If switching to non-sharded, clean up potential old share files
            existing_share_files = glob.glob(f"{self.vault_path}.s[0-9]*")
            if existing_share_files:
                print(f"Info: Switched to non-sharded mode for {self.vault_path}. "
                      f"Found existing share files: {existing_share_files}. These are no longer used by this vault instance.")
                # Optionally, could offer to remove them or require manual cleanup.
                # For safety, not auto-deleting them here without explicit instruction.


    def add_entry(self, site, username, password):
        data = self._read_data()
        data[site] = {"username": username, "password": password}
        self._write_data(data)

    def get_entry(self, site):
        data = self._read_data()
        return data.get(site)

    def list_entries(self):
        data = self._read_data()
        if data: # Ensure data is not None or empty before calling keys()
            return list(data.keys())
        return []


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
            raw_encrypted_data_with_salt = None
            if self.sharding_config:
                loaded_shares = []
                for i in range(self.sharding_config['total_shares']):
                    share_path = f"{self.vault_path}.s{i+1}"
                    if os.path.exists(share_path):
                        try:
                            with open(share_path, "r") as f:
                                share_data = json.load(f)
                            loaded_shares.append(share_data)
                        except Exception: 
                            pass 
                
                if len(loaded_shares) < self.sharding_config['threshold']:
                    return False

                encrypted_data_hex = Sharding.combine_shares(loaded_shares)
                raw_encrypted_data_with_salt = bytes.fromhex(encrypted_data_hex)
            else: 
                if not os.path.exists(self.vault_path):
                    return False 
                with open(self.vault_path, "rb") as f:
                    raw_encrypted_data_with_salt = f.read()

            if len(raw_encrypted_data_with_salt) < 16: 
                return False

            salt = raw_encrypted_data_with_salt[:16]
            encrypted_payload = raw_encrypted_data_with_salt[16:]

            if not encrypted_payload:
                return False

            temp_crypt_for_verify = Cryptify(passphrase, salt) 
            decrypted_bytes = temp_crypt_for_verify.cipher.decrypt(encrypted_payload)
            json.loads(decrypted_bytes.decode())
            return True
        except Exception:
            return False
