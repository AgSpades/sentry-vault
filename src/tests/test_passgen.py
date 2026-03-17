import re
from pathlib import Path

from sentryvault.passgen import PasswordGenerator, PasswordType


def _make_wordlist(tmp_path: Path) -> Path:
    words = [
        "secure",
        "silver",
        "rocket",
        "planet",
        "forest",
        "lunar",
        "cipher",
        "ocean",
        "ember",
        "vector",
    ]
    wordlist_path = tmp_path / "words.txt"
    wordlist_path.write_text("\n".join(words), encoding="utf-8")
    return wordlist_path


def test_generate_random_password_meets_constraints(tmp_path: Path):
    generator = PasswordGenerator(wordlist_path=_make_wordlist(tmp_path))

    password = generator.generate(PasswordType.RANDOM, length=16)

    assert len(password) == 16
    assert any(ch.isupper() for ch in password)
    assert any(ch.isdigit() for ch in password)
    assert any(not ch.isalnum() for ch in password)


def test_generate_memorable_password_format(tmp_path: Path):
    generator = PasswordGenerator(wordlist_path=_make_wordlist(tmp_path))

    password = generator.generate(
        PasswordType.MEMORABLE, length=20, use_special=True, use_digits=True
    )

    assert password[0].isupper()
    assert any(not ch.isalnum() for ch in password)
    assert re.search(r"\d", password)


def test_generate_pin_is_digits_only(tmp_path: Path):
    generator = PasswordGenerator(wordlist_path=_make_wordlist(tmp_path))

    pin = generator.generate(PasswordType.PIN, length=6)

    assert len(pin) == 6
    assert pin.isdigit()


def test_entropy_is_positive(tmp_path: Path):
    generator = PasswordGenerator(wordlist_path=_make_wordlist(tmp_path))

    entropy = generator.calculate_entropy("Abc123!xyz")

    assert entropy > 0
