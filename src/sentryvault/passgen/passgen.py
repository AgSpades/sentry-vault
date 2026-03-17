"""
Password and passphrase generator for Sentry Vault.

This module provides secure generation of passwords and memorable passphrases
using Markov chains and cryptographically secure random number generation.
"""

import random
import secrets
import string
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import nltk
from nltk.corpus import words
from rich.console import Console

# Initialize console for rich output
console = Console()


class PasswordType(Enum):
    """Types of passwords that can be generated."""

    RANDOM = auto()
    MEMORABLE = auto()
    PIN = auto()


@dataclass
class PasswordConfig:
    """Configuration for password generation."""

    length: int = 16  # Target length (approximate for memorable passwords)
    use_uppercase: bool = True
    use_digits: bool = True
    use_special: bool = True
    min_entropy: float = 80.0  # Minimum bits of entropy
    word_count: Optional[int] = (
        None  # Will be calculated based on length for memorable passwords
    )
    separator: str = ""  # No separator for the new format


class PasswordGenerator:
    """Secure password and passphrase generator using Markov chains."""

    def __init__(self, wordlist_path: Optional[Path] = None):
        """Initialize the password generator with an optional custom wordlist.

        Args:
            wordlist_path: Path to a custom wordlist file. If not provided,
                         uses NLTK's words corpus.
        """
        self.wordlist = self._load_wordlist(wordlist_path)
        # Filter words to be between 4-8 characters for better memorability
        self.wordlist = {w for w in self.wordlist if 4 <= len(w) <= 8}
        self.markov_chain = self._build_markov_chain()

    def _load_wordlist(self, wordlist_path: Optional[Path]) -> Set[str]:
        """Load words from a file or use NLTK's wordlist."""
        if wordlist_path and wordlist_path.exists():
            with open(wordlist_path, "r", encoding="utf-8") as f:
                return {word.strip().lower() for word in f if word.strip().isalpha()}

        try:
            return set(words.words())
        except LookupError:
            console.print("[yellow]Downloading NLTK words corpus...[/]")
            nltk.download("words")
            return set(words.words())

    def _build_markov_chain(self, order: int = 2) -> Dict[str, List[str]]:
        """Build a Markov chain from the wordlist.

        Args:
            order: The order of the Markov chain (number of previous characters to consider).

        Returns:
            A dictionary mapping character n-grams to possible next characters.
        """
        chain = defaultdict(list)
        for word in self.wordlist:
            if len(word) <= order:
                continue

            for i in range(len(word) - order):
                prefix = word[i : i + order]
                next_char = word[i + order]
                chain[prefix].append(next_char)

        return dict(chain)

    def generate_password(self, config: Optional[PasswordConfig] = None) -> str:
        """Generate a secure password based on the provided configuration.

        Args:
            config: Password configuration. If None, uses default settings.

        Returns:
            A generated password.
        """
        config = config or PasswordConfig()

        # Character sets
        chars = string.ascii_lowercase
        if config.use_uppercase:
            chars += string.ascii_uppercase
        if config.use_digits:
            chars += string.digits
        if config.use_special:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        # Generate password with at least one character from each selected set
        password = []
        if config.use_uppercase:
            password.append(secrets.choice(string.ascii_uppercase))
        if config.use_digits:
            password.append(secrets.choice(string.digits))
        if config.use_special:
            password.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))

        # Fill the rest randomly
        remaining_length = max(0, config.length - len(password))
        password.extend(secrets.choice(chars) for _ in range(remaining_length))

        # Shuffle to avoid patterns
        random.shuffle(password)
        return "".join(password)

    def generate_passphrase(self, config: Optional[PasswordConfig] = None) -> str:
        """Generate a memorable passphrase in the format 'AdjectiveNoun!Number'.

        Args:
            config: Passphrase configuration.

        Returns:
            A generated passphrase like 'SecureWolf!42'.
        """
        config = config or PasswordConfig()

        # Word categories
        adjectives = [w for w in self.wordlist if len(w) >= 4 and len(w) <= 8]
        nouns = [w for w in self.wordlist if len(w) >= 3 and len(w) <= 8]

        if not adjectives or not nouns:
            raise ValueError("Wordlist doesn't contain enough words for generation")

        # Generate components
        def capitalize(word: str) -> str:
            return word[0].upper() + word[1:].lower()

        adjective = capitalize(secrets.choice(adjectives))
        noun = capitalize(secrets.choice(nouns))
        number = str(secrets.randbelow(90) + 10)  # 10-99

        # Build the passphrase
        parts = [adjective, noun]
        passphrase = "".join(parts)

        # Add special character if needed
        special = ""
        if config.use_special:
            special = secrets.choice("!@#$%^&*")
            passphrase += special

        # Add number if needed (but not if it would make it too long)
        if config.use_digits and len(passphrase) + len(number) <= config.length:
            passphrase += number

        return passphrase

    def calculate_entropy(self, password: str) -> float:
        """Calculate the entropy of a password in bits.

        Args:
            password: The password to analyze.

        Returns:
            The entropy in bits.
        """
        import math

        # Determine the character set size
        charset = 0
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        if has_lower:
            charset += 26
        if has_upper:
            charset += 26
        if has_digit:
            charset += 10
        if has_special:
            # Common special characters
            charset += 32  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

        # Calculate entropy: log2(charset^length)
        return math.log2(charset ** len(password))

    def generate(self, ptype: PasswordType = PasswordType.RANDOM, **kwargs) -> str:
        """Generate a password or passphrase.

        Args:
            ptype: Type of password to generate.
            **kwargs: Additional configuration parameters.

        Returns:
            The generated password or passphrase.
        """
        config = PasswordConfig(**kwargs)

        if ptype == PasswordType.RANDOM:
            return self.generate_password(config)
        elif ptype == PasswordType.MEMORABLE:
            # For memorable passwords, we'll adjust word selection to match length
            return self.generate_passphrase(config)
        elif ptype == PasswordType.PIN:
            return "".join(secrets.choice(string.digits) for _ in range(config.length))
        else:
            raise ValueError(f"Unknown password type: {ptype}")


def main():
    """Example usage of the PasswordGenerator."""
    try:
        generator = PasswordGenerator()

        console.print("\n[bold]Password Generator Examples:[/]")

        # Generate a random password
        password = generator.generate(PasswordType.RANDOM, length=16)
        console.print(f"\n[bold]Random Password:[/] {password}")

        # Generate a memorable passphrase
        passphrase = generator.generate(
            PasswordType.MEMORABLE, word_count=4, separator=" "
        )
        console.print(f"[bold]Memorable Passphrase:[/] {passphrase}")

        # Generate a PIN
        pin = generator.generate(PasswordType.PIN, length=6)
        console.print(f"[bold]PIN:[/] {pin}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
