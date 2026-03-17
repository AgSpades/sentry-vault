import itertools

import pytest

from sentryvault.sharding import Sharding


def test_split_and_combine_secret_threshold_subsets():
    """Secret can be reconstructed from any threshold-sized subset of shares."""
    secret = "hello world secret test 123!"
    total_shares = 5
    threshold = 3

    shares = Sharding.split_secret(secret, total_shares, threshold)

    assert len(shares) == total_shares
    assert all(isinstance(share, str) for share in shares)

    # Validate multiple subsets, not just the first N shares.
    for subset in itertools.combinations(shares, threshold):
        assert Sharding.combine_shares(list(subset)) == secret


def test_hex_data_splitting_roundtrip():
    """Hex payloads (like vault encrypted bytes) are preserved through sharding."""
    original_data = b"encrypted vault data with salt and payload"
    hex_secret = original_data.hex()

    shares = Sharding.split_secret(hex_secret, 5, 3)
    recovered_hex = Sharding.combine_shares(shares[:3])

    assert bytes.fromhex(recovered_hex) == original_data


def test_save_and_load_shares(tmp_path):
    """Shares can be persisted and loaded back without corruption."""
    secret = "test secret for file operations"
    shares = Sharding.split_secret(secret, 5, 3)
    shares_file = tmp_path / "shares.json"

    Sharding.save_shares_to_file(shares, str(shares_file))
    loaded_shares = Sharding.load_shares_from_file(str(shares_file))

    assert shares_file.exists()
    assert loaded_shares == shares
    assert Sharding.combine_shares(loaded_shares[:3]) == secret


def test_insufficient_shares_raises():
    """Reconstruction should fail when fewer than threshold shares are provided."""
    secret = "secret that needs enough shares"
    shares = Sharding.split_secret(secret, 5, 4)

    with pytest.raises(Exception):
        Sharding.combine_shares(shares[:3])
