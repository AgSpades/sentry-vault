from pathlib import Path

from sentryvault.vault import PasswordVault


def test_non_sharded_vault_roundtrip_and_parent_dir_creation(tmp_path: Path):
    vault_path = tmp_path / "nested" / "config" / "vault.enc"

    vault = PasswordVault("pw-123", vault_path=str(vault_path))
    vault.add_entry("example.com", "alice", "s3cr3t")

    assert vault_path.exists()
    assert vault.get_entry("example.com") == {
        "username": "alice",
        "password": "s3cr3t",
    }
    assert vault.list_entries() == ["example.com"]

    assert vault.delete_entry("example.com") is True
    assert vault.get_entry("example.com") is None


def test_verify_passphrase(tmp_path: Path):
    vault_path = tmp_path / "vault.enc"
    vault = PasswordVault("right-pass", vault_path=str(vault_path))
    vault.add_entry("example.com", "bob", "pw")

    assert vault.verify_passphrase("right-pass") is True
    assert vault.verify_passphrase("wrong-pass") is False


def test_sharded_vault_creates_shares_and_recovers(tmp_path: Path):
    vault_base = tmp_path / "vault-sharded.enc"
    config = {"total_shares": 3, "threshold": 2}

    vault = PasswordVault("share-pass", vault_path=str(vault_base), sharding_config=config)
    vault.add_entry("service.io", "carol", "pass-999")

    share_paths = [tmp_path / f"vault-sharded.enc.s{i}" for i in range(1, 4)]
    for share_path in share_paths:
        assert share_path.exists()

    recovered = PasswordVault("share-pass", vault_path=str(vault_base), sharding_config=config)
    assert recovered.get_entry("service.io") == {
        "username": "carol",
        "password": "pass-999",
    }
