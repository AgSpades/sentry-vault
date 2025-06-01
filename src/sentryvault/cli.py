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
import os # Added for vault_path default handling
from pathlib import Path
from typing import Optional
from .passgen import PasswordGenerator, PasswordType

console = Console()

# --- Helper for Sharding Configuration ---
def _create_sharding_config(total_shares, threshold):
    if total_shares is not None and threshold is not None:
        if not isinstance(total_shares, int) or not isinstance(threshold, int):
            console.print("[red]❌ Total shares and threshold must be integers.[/red]")
            return None, True
        if threshold < 2:
            console.print("[red]❌ Threshold must be at least 2 for Shamir's Secret Sharing.[/red]")
            return None, True
        if total_shares < threshold:
            console.print("[red]❌ Total shares must be greater than or equal to the threshold.[/red]")
            return None, True
        return {"total_shares": total_shares, "threshold": threshold}, False
    elif total_shares is not None or threshold is not None:
        console.print("[red]❌ Both --total-shares and --threshold must be provided together for sharding, or neither for a non-sharded vault.[/red]")
        return None, True
    return None, False # No sharding config, no error

# --- Common Click options for vault commands ---
def vault_options(func):
    func = click.option('--vault-path', default=os.path.join(os.getcwd(), "vault.enc"), help="Path to the vault file or base name for shares.", show_default=True, type=click.Path())(func)
    func = click.option('--total-shares', type=int, help="Total number of shares for sharding (requires --threshold).")(func)
    func = click.option('--threshold', type=int, help="Minimum shares needed to reconstruct (requires --total-shares).")(func)
    return func

@click.group()
def main():
    """🔐 SentryVault: Quantum resistant decentralized password manager."""
    console.print(Panel.fit("[bold green]SentryVault CLI[/bold green]\n[cyan]Quantum resistant decentralized password manager[/cyan]"))

@main.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument("output_file", type=click.Path(dir_okay=False, resolve_path=True))
def encrypt(input_file, output_file):
    """🔒 Encrypt a file and save it to output_file."""
    passphrase = getpass("Enter passphrase: ")
    if not passphrase:
        console.print("[red]❌ Passphrase cannot be empty.[/red]")
        return
    crypt = Cryptify(passphrase)
    
    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Encrypting file...", total=100)
        try:
            crypt.encrypt_file(input_file, output_file)
            # Simulate progress if encryption is very fast
            for _ in range(100):
                if progress.tasks[task].completed >= 100:
                    break
                progress.update(task, advance=1)
                time.sleep(0.01) # Shorter sleep
            progress.update(task, completed=100) # Ensure it completes
        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Encryption failed: {e}[/red]")
            return

    console.print(f"[green][+] Encrypted[/green] {input_file} ➜ {output_file}")

@main.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument("output_file", type=click.Path(dir_okay=False, resolve_path=True))
def decrypt(input_file, output_file):
    """🔓 Decrypt a file using the same passphrase."""
    passphrase = getpass("Enter passphrase: ")
    if not passphrase:
        console.print("[red]❌ Passphrase cannot be empty.[/red]")
        return
        
    salt = None
    try:
        with open(input_file, "rb") as f:
            salt = f.read(16) # Read only the first 16 bytes for salt
        if len(salt) < 16:
            console.print("[red]❌ Input file is too short to contain a valid salt.[/red]")
            return
    except IOError as e:
        console.print(f"[red]❌ Could not read input file {input_file}: {e}[/red]")
        return
    
    with console.status("[bold green]Decrypting file...") as status:
        try:
            crypt = Cryptify(passphrase, salt)
            crypt.decrypt_file(input_file, output_file)
            status.stop()
            console.print(f"[green][+] Decrypted[/green] {input_file} ➜ {output_file}")
        except InvalidToken:
            status.stop()
            console.print("[red]❌ Invalid passphrase or corrupted file.[/red]")
        except Exception as e:
            status.stop()
            console.print(f"[red]❌ Decryption failed: {e}[/red]")

# -----------------------------
# Password Vault Subcommands
# -----------------------------

def get_vault_passphrase():
    passphrase = getpass("Enter your vault passphrase: ")
    if not passphrase:
        console.print("[red]❌ Passphrase cannot be empty.[/red]")
        return None
    return passphrase

@main.command()
@vault_options
@click.argument("site")
@click.argument("username")
def add(site, username, vault_path, total_shares, threshold):
    """➕ Add or update a password entry."""
    password = click.prompt("Enter password for site", hide_input=True, confirmation_prompt="Confirm password for site")
    if not password:
        console.print("[red]❌ Password cannot be empty.[/red]")
        return

    sharding_config, err = _create_sharding_config(total_shares, threshold)
    if err:
        return

    passphrase = get_vault_passphrase()
    if not passphrase:
        return

    try:
        vault = PasswordVault(passphrase, vault_path=vault_path, sharding_config=sharding_config)
        vault.add_entry(site, username, password)
        mode = "sharded" if sharding_config else "non-sharded"
        console.print(f"[cyan]🔐 Added[/cyan] entry for [bold]{site}[/bold] to {mode} vault '{os.path.basename(vault_path)}'.")
    except InvalidToken:
        console.print("[red]❌ Incorrect passphrase or corrupted vault.[/red]")
    except ValueError as e:
        console.print(f"[red]❌ Vault operation error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ An unexpected error occurred: {e}[/red]")

@main.command()
@vault_options
@click.argument("site")
@click.option("--show", is_flag=True, help="Display password in plaintext.")
def get(site, vault_path, total_shares, threshold, show):
    """🔍 Retrieve login info for a site."""
    sharding_config, err = _create_sharding_config(total_shares, threshold)
    if err:
        return

    passphrase = get_vault_passphrase()
    if not passphrase:
        return

    try:
        vault = PasswordVault(passphrase, vault_path=vault_path, sharding_config=sharding_config)
        entry = vault.get_entry(site)
        if entry:
            table = Table(title=f"🔑 Entry: {site} (from '{os.path.basename(vault_path)}')", show_header=True, header_style="bold magenta")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Username", entry["username"])
            table.add_row("Password", entry["password"] if show else "•" * len(entry["password"]))
            console.print(table)
        else:
            console.print(f"[red]❌ Entry not found for[/red] {site} in vault '{os.path.basename(vault_path)}'.")
    except InvalidToken:
        console.print("[red]❌ Incorrect passphrase or corrupted vault.[/red]")
    except ValueError as e:
        console.print(f"[red]❌ Vault operation error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ An unexpected error occurred: {e}[/red]")

@main.command(name="list")
@vault_options
def list_entries(vault_path, total_shares, threshold):
    """📂 List all stored entry names."""
    sharding_config, err = _create_sharding_config(total_shares, threshold)
    if err:
        return

    passphrase = get_vault_passphrase()
    if not passphrase:
        return

    try:
        vault = PasswordVault(passphrase, vault_path=vault_path, sharding_config=sharding_config)
        keys = vault.list_entries()
        mode = "sharded" if sharding_config else "non-sharded"
        title = f"📁 Stored Entries in {mode} vault '{os.path.basename(vault_path)}'"
        if keys:
            table = Table(title=title, show_lines=True, header_style="bold blue")
            table.add_column("Site", style="cyan")
            for key_name in keys: # Renamed key to key_name to avoid conflict with PasswordVault.key
                table.add_row(key_name)
            console.print(table)
        else:
            console.print(f"[yellow]⚠️ Vault '{os.path.basename(vault_path)}' is empty or no entries found.[/yellow]")
    except InvalidToken:
        console.print("[red]❌ Incorrect passphrase or corrupted vault.[/red]")
    except ValueError as e:
        console.print(f"[red]❌ Vault operation error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ An unexpected error occurred: {e}[/red]")

@main.command()
@vault_options
@click.argument("site")
def delete(site, vault_path, total_shares, threshold):
    """🗑️ Delete a password entry."""
    sharding_config, err = _create_sharding_config(total_shares, threshold)
    if err:
        return

    passphrase = get_vault_passphrase()
    if not passphrase:
        return
        
    confirm = click.confirm(f"Are you sure you want to delete the entry for '{site}' from vault '{os.path.basename(vault_path)}'?", abort=True)

    try:
        vault = PasswordVault(passphrase, vault_path=vault_path, sharding_config=sharding_config)
        if vault.delete_entry(site):
            mode = "sharded" if sharding_config else "non-sharded"
            console.print(f"[red]🗑️ Deleted[/red] entry for [bold]{site}[/bold] from {mode} vault '{os.path.basename(vault_path)}'.")
        else:
            console.print(f"[red]❌ No entry found for[/red] {site} in vault '{os.path.basename(vault_path)}'.")
    except InvalidToken:
        console.print("[red]❌ Incorrect passphrase or corrupted vault.[/red]")
    except ValueError as e:
        console.print(f"[red]❌ Vault operation error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ An unexpected error occurred: {e}[/red]")

@main.command()
@vault_options
def change_passphrase(vault_path, total_shares, threshold):
    """🔑 Change your vault passphrase securely."""
    console.print(f"Attempting to change passphrase for vault: '{os.path.basename(vault_path)}'")
    old_passphrase = getpass("Enter current vault passphrase: ")
    if not old_passphrase:
        console.print("[red]❌ Current passphrase cannot be empty.[/red]")
        return

    new_passphrase = getpass("Enter new vault passphrase: ")
    if not new_passphrase:
        console.print("[red]❌ New passphrase cannot be empty.[/red]")
        return
        
    confirm_passphrase = getpass("Confirm new vault passphrase: ")
    if new_passphrase != confirm_passphrase:
        console.print("[red]❌ New passphrases do not match.[/red]")
        return
    
    if old_passphrase == new_passphrase:
        console.print("[yellow]⚠️ New passphrase is the same as the old passphrase. No change made.[/yellow]")
        return

    sharding_config, err = _create_sharding_config(total_shares, threshold)
    if err:
        return

    try:
        # Initialize with old passphrase to read data
        vault = PasswordVault(old_passphrase, vault_path=vault_path, sharding_config=sharding_config)
        all_data = vault._read_data() # Decrypts with old passphrase

        # Re-initialize the vault's crypto components with the new passphrase
        # This will use a new salt by default when Cryptify is re-initialized
        vault.passphrase = new_passphrase
        vault.crypt = Cryptify(new_passphrase) 
        
        vault._write_data(all_data) # Encrypts with new passphrase/salt and writes (sharded or not)

        mode = "sharded" if sharding_config else "non-sharded"
        console.print(f"[green]🔑 Passphrase updated successfully for {mode} vault '{os.path.basename(vault_path)}'.[/green]")
        if sharding_config:
            console.print(f"[green]   Sharding Config: Total Shares: {sharding_config['total_shares']}, Threshold: {sharding_config['threshold']}[/green]")

    except InvalidToken:
        console.print("[red]❌ Incorrect current passphrase or corrupted vault. Passphrase not changed.[/red]")
    except ValueError as e:
        console.print(f"[red]❌ Vault operation error during passphrase change: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ An unexpected error occurred during passphrase change: {e}[/red]")

@main.command()
@click.option('--type', '-t', type=click.Choice(['random', 'memorable', 'pin'], case_sensitive=False),
              default='random', help='Type of password to generate')
@click.option('--length', '-l', type=int, default=16, help='Exact length for random passwords or PINs')
@click.option('--r-length', type=int, help='Rough target length for memorable passwords (e.g., 16 for "SecureWolf!42")')
@click.option('--no-upper', is_flag=True, help='Exclude uppercase letters')
@click.option('--no-digits', is_flag=True, help='Exclude digits')
@click.option('--no-special', is_flag=True, help='Exclude special characters')
@click.option('--wordlist', type=click.Path(exists=True, dir_okay=False, path_type=Path), 
              help='Path to custom wordlist file')
@click.option('--copy', '-c', is_flag=True, help='Copy password to clipboard')
def generate_password(type, length, r_length, no_upper, no_digits, no_special, wordlist, copy):
    """🔐 Generate a secure password or passphrase."""
    try:
        # Map type to PasswordType enum
        ptype = {
            'random': PasswordType.RANDOM,
            'memorable': PasswordType.MEMORABLE,
            'pin': PasswordType.PIN
        }[type.lower()]
        
        # Create password generator with optional wordlist
        generator = PasswordGenerator(wordlist_path=wordlist)
        
        # For memorable passwords, use r_length if provided, otherwise default to 16
        target_length = r_length if ptype == PasswordType.MEMORABLE and r_length is not None else length
        
        # Generate the password
        password = generator.generate(
            ptype=ptype,
            length=target_length,
            use_uppercase=not no_upper,
            use_digits=not no_digits,
            use_special=not no_special
        )
        
        # Display the password
        console.print("\n[bold green]Generated Password:[/]")
        console.print(f"[bold cyan]{password}[/]")
        
        # Copy to clipboard if requested
        if copy:
            try:
                import pyperclip
                pyperclip.copy(password)
                console.print("[green]✓ Password copied to clipboard![/]")
            except ImportError:
                console.print("[yellow]⚠ Install 'pyperclip' for clipboard support: pip install pyperclip[/]")
        
        # Calculate and display entropy
        entropy = generator.calculate_entropy(password)
        console.print(f"[dim]Entropy: {entropy:.2f} bits[/]")
        
        # Add to clipboard history if available
        if copy and 'pyperclip' in globals():
            try:
                from rich.clipboard import Clipboard
                clipboard = Clipboard()
                clipboard.store(password)
            except ImportError:
                pass
                
    except Exception as e:
        console.print(f"[red]❌ Error generating password: {e}[/]")
        return 1
    
    return 0


if __name__ == '__main__':
    main()
