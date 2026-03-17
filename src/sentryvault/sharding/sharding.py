import pyshamir
import json


class Sharding:
    @staticmethod
    def split_secret(secret, total_shares, threshold):
        """
        Split a secret into shares using Shamir's Secret Sharing.

        Args:
            secret (str): The secret to split.
            total_shares (int): Total number of shares to generate.
            threshold (int): Minimum number of shares required to reconstruct the secret.

        Returns:
            list: A list of shares (as strings).
        """
        # Convert string to bytes for pyshamir
        secret_bytes = secret.encode("utf-8")

        # pyshamir.split(secret, parts, threshold) - note parameter order
        share_bytes = pyshamir.split(secret_bytes, total_shares, threshold)

        # Convert bytearray shares to base64-encoded strings for JSON compatibility
        import base64

        shares = [base64.b64encode(share).decode("ascii") for share in share_bytes]
        return shares

    @staticmethod
    def combine_shares(shares):
        """
        Combine shares to reconstruct the secret.

        Args:
            shares (list): A list of shares (as strings).

        Returns:
            str: The reconstructed secret.
        """
        # Convert base64 strings back to bytearray
        import base64

        share_bytes = [
            bytearray(base64.b64decode(share.encode("ascii"))) for share in shares
        ]

        # Combine using pyshamir
        secret_bytes = pyshamir.combine(share_bytes)

        # Convert bytes back to string
        secret = secret_bytes.decode("utf-8")
        return secret

    @staticmethod
    def save_shares_to_file(shares, file_path):
        """
        Save shares to a file in JSON format.

        Args:
            shares (list): A list of shares.
            file_path (str): Path to the file where shares will be saved.
        """
        with open(file_path, "w") as f:
            json.dump(shares, f)

    @staticmethod
    def load_shares_from_file(file_path):
        """
        Load shares from a file in JSON format.

        Args:
            file_path (str): Path to the file containing shares.

        Returns:
            list: A list of shares.
        """
        with open(file_path, "r") as f:
            shares = json.load(f)
        return shares
