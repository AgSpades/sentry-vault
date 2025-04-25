import click
from getpass import getpass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .crypto import Cryptify
from .vault import PasswordVault

console = Console()

@click.group()
def main():
    """🔐 SentryVault: AI-powered decentralized password manager."""
    console.print(Panel.fit("[bold green]SentryVault CLI[/bold green]\n[cyan]AI-powered decentralized password manager[/cyan]"))


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def encrypt(input_file, output_file):
    """🔒 Encrypt a file and save it to output_file."""
    passphrase = getpass("Enter passphrase: ")
    crypt = Cryptify(passphrase)
    crypt.encrypt_file(input_file, output_file)
    console.print(f"[green][+] Encrypted[/green] {input_file} ➜ {output_file}")


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def decrypt(input_file, output_file):
    """🔓 Decrypt a file using the same passphrase."""
    passphrase = getpass("Enter passphrase: ")
    with open(input_file, "rb") as f:
        salt = f.read()[:16]
    crypt = Cryptify(passphrase, salt)
    crypt.decrypt_file(input_file, output_file)
    console.print(f"[green][+] Decrypted[/green] {input_file} ➜ {output_file}")


# -----------------------------
# Password Vault Subcommands
# -----------------------------

def get_passphrase():
    return getpass("Enter your vault passphrase: ")

@main.command()
@click.argument("site")
@click.argument("username")
@click.argument("password")
def add(site, username, password):
    """➕ Add or update a password entry."""
    vault = PasswordVault(get_passphrase())
    vault.add_entry(site, username, password)
    console.print(f"[cyan]🔐 Added[/cyan] entry for [bold]{site}[/bold]")

@main.command()
@click.argument("site")
def get(site):
    """🔍 Retrieve login info for a site."""
    vault = PasswordVault(get_passphrase())
    entry = vault.get_entry(site)
    if entry:
        table = Table(title=f"🔑 Entry: {site}", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Username", entry["username"])
        table.add_row("Password", entry["password"])
        console.print(table)
    else:
        console.print(f"[red]❌ Entry not found for[/red] {site}")

@main.command(name="list")
def list_entries():
    """📂 List all stored entry names."""
    vault = PasswordVault(get_passphrase())
    keys = vault.list_entries()
    if keys:
        table = Table(title="📁 Stored Entries", show_lines=True, header_style="bold blue")
        table.add_column("Site", style="cyan")
        for key in keys:
            table.add_row(key)
        console.print(table)
    else:
        console.print("[yellow]⚠️ Vault is empty.[/yellow]")

@main.command()
@click.argument("site")
def delete(site):
    """🗑️ Delete a password entry."""
    vault = PasswordVault(get_passphrase())
    if vault.delete_entry(site):
        console.print(f"[red]🗑️ Deleted[/red] entry for [bold]{site}[/bold]")
    else:
        console.print(f"[red]❌ No entry found for[/red] {site}")
