import pytest
import json
import tempfile
import os
from sentryvault.sharding import Sharding


class TestSharding:
    def test_split_and_combine_secret(self):
        """Test basic secret splitting and combining functionality."""
        secret = "hello world secret test 123!"
        total_shares = 5
        threshold = 3
        
        # Split the secret
        shares = Sharding.split_secret(secret, total_shares, threshold)
        
        # Verify we get the expected number of shares
        assert len(shares) == total_shares
        
        # Verify each share is a string (to match secretsharing format)
        for share in shares:
            assert isinstance(share, str)
        
        # Test combining with minimum required shares
        recovered_secret = Sharding.combine_shares(shares[:threshold])
        assert recovered_secret == secret
        
        # Test combining with more than minimum shares
        recovered_secret2 = Sharding.combine_shares(shares[:threshold+1])
        assert recovered_secret2 == secret
        
        # Test combining with all shares
        recovered_secret3 = Sharding.combine_shares(shares)
        assert recovered_secret3 == secret

    def test_hex_data_splitting(self):
        """Test splitting hex-encoded data (as used by vault)."""
        # Simulate encrypted vault data as hex string
        original_data = b"encrypted vault data with salt and payload"
        hex_secret = original_data.hex()
        
        shares = Sharding.split_secret(hex_secret, 5, 3)
        recovered_hex = Sharding.combine_shares(shares[:3])
        recovered_data = bytes.fromhex(recovered_hex)
        
        assert recovered_data == original_data

    def test_save_and_load_shares(self):
        """Test saving shares to file and loading them back."""
        secret = "test secret for file operations"
        shares = Sharding.split_secret(secret, 5, 3)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            # Save shares to file
            Sharding.save_shares_to_file(shares, temp_path)
            
            # Verify file exists and contains data
            assert os.path.exists(temp_path)
            
            # Load shares from file
            loaded_shares = Sharding.load_shares_from_file(temp_path)
            
            # Verify loaded shares match original
            assert loaded_shares == shares
            
            # Verify secret can be recovered from loaded shares
            recovered_secret = Sharding.combine_shares(loaded_shares[:3])
            assert recovered_secret == secret
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_insufficient_shares(self):
        """Test that insufficient shares cannot recover the secret."""
        secret = "secret that needs enough shares"
        shares = Sharding.split_secret(secret, 5, 4)  # Need 4 shares minimum
        
        # This should fail or return incorrect result with only 3 shares
        # The specific behavior depends on the library implementation
        with pytest.raises(Exception):
            Sharding.combine_shares(shares[:3])