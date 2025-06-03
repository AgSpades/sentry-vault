from pyseltongue import SecretSharer
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
            list: A list of shares.
        """
        shares = SecretSharer.split_secret(secret, threshold, total_shares)
        return shares

    @staticmethod
    def combine_shares(shares):
        """
        Combine shares to reconstruct the secret.

        Args:
            shares (list): A list of shares.

        Returns:
            str: The reconstructed secret.
        """
        secret = SecretSharer.recover_secret(shares)
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
