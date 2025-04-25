import click
from getpass import getpass
from .crypto import Cryptify

@click.group()
def main():
    """SentryVault: AI-powered decentralized password manager."""
    pass

@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def encrypt(input_file, output_file):
    """Encrypt a file and store it as output_file."""
    passphrase = getpass("Enter passphrase: ")
    crypt = Cryptify(passphrase)
    crypt.encrypt_file(input_file, output_file)
    click.echo(f"[+] Encrypted {input_file} ➜ {output_file}")

@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def decrypt(input_file, output_file):
    """Decrypt an encrypted file using the same passphrase."""
    passphrase = getpass("Enter passphrase: ")
    with open(input_file, "rb") as f:
        salt = f.read()[:16]
    crypt = Cryptify(passphrase, salt)
    crypt.decrypt_file(input_file, output_file)
    click.echo(f"[+] Decrypted {input_file} ➜ {output_file}")
