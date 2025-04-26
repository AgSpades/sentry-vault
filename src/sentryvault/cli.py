import click
from getpass import getpass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from cryptography.fernet import InvalidToken  
from .crypto import Cryptify
from .vault import PasswordVault
import time

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
    
    # Set up the progress bar
    with Progress() as progress:
        task = progress.add_task("[cyan]Encrypting file...", total=100)
        
        # Perform encryption with a simulated progress
        crypt.encrypt_file(input_file, output_file)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.05)  # Simulate encryption time

    console.print(f"[green][+] Encrypted[/green] {input_file} ➜ {output_file}")

@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def decrypt(input_file, output_file):
    """🔓 Decrypt a file using the same passphrase."""
    passphrase = getpass("Enter passphrase: ")
    with open(input_file, "rb") as f:
        salt = f.read()[:16]
    
    # Set up a spinner for the decryption process
    with console.status("[bold green]Decrypting file...") as status:
        try:
            crypt = Cryptify(passphrase, salt)
            crypt.decrypt_file(input_file, output_file)
            console.print(f"[green][+] Decrypted[/green] {input_file} ➜ {output_file}")
        except InvalidToken:
            console.print("[red]❌ Invalid passphrase or corrupted file.[/red]")

# -----------------------------
# Password Vault Subcommands
# -----------------------------

def get_passphrase():
    return getpass("Enter your vault passphrase: ")

@main.command()
@click.argument("site")
@click.argument("username")
def add(site, username):
    """➕ Add or update a password entry."""
    try:
        password = click.prompt("Enter password", hide_input=True, confirmation_prompt=True)
        vault = PasswordVault(get_passphrase())
        vault.add_entry(site, username, password)
        console.print(f"[cyan]🔐 Added[/cyan] entry for [bold]{site}[/bold]")
    except InvalidToken:
        console.print("[red]❌ Incorrect passphrase.[/red]")

@main.command()
@click.argument("site")
@click.option("--show", is_flag=True, help="Display password in plaintext.")
def get(site, show):
    """🔍 Retrieve login info for a site."""
    try:
        vault = PasswordVault(get_passphrase())
        entry = vault.get_entry(site)
        if entry:
            table = Table(title=f"🔑 Entry: {site}", show_header=True, header_style="bold magenta")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Username", entry["username"])
            table.add_row("Password", entry["password"] if show else "•" * 10)
            console.print(table)
        else:
            console.print(f"[red]❌ Entry not found for[/red] {site}")
    except InvalidToken:
        console.print("[red]❌ Incorrect passphrase.[/red]")

@main.command(name="list")
def list_entries():
    """📂 List all stored entry names."""
    try:
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
    except InvalidToken:
        console.print("[red]❌ Incorrect passphrase.[/red]")

@main.command()
@click.argument("site")
def delete(site):
    """🗑️ Delete a password entry."""
    try:
        vault = PasswordVault(get_passphrase())
        if vault.delete_entry(site):
            console.print(f"[red]🗑️ Deleted[/red] entry for [bold]{site}[/bold]")
        else:
            console.print(f"[red]❌ No entry found for[/red] {site}")
    except InvalidToken:
        console.print("[red]❌ Incorrect passphrase.[/red]")

@main.command()
def change_passphrase():
    """🔑 Change your vault passphrase securely."""
    old_passphrase = getpass("Enter current passphrase: ")
    new_passphrase = getpass("Enter new passphrase: ")
    confirm_passphrase = getpass("Confirm new passphrase: ")
    if new_passphrase != confirm_passphrase:
        console.print("[red]❌ Passphrases do not match.[/red]")
        return
    try:
        vault = PasswordVault(old_passphrase)
        vault.change_passphrase(new_passphrase)
        console.print("[green]🔑 Passphrase updated successfully.[/green]")
    except InvalidToken:
        console.print("[red]❌ Incorrect current passphrase.[/red]")
