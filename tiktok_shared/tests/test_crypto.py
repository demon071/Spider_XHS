"""
Unit tests for cryptographic modules
Run with: pytest tests/test_crypto.py -v
"""

import pytest
from src_shared_py.crypto.sm3 import SM3
from src_shared_py.crypto.simon import simon_enc, simon_dec
from src_shared_py.crypto.buffer_utils import bytes_to_hex, hex_to_bytes
from src_shared_py.crypto.crypto_utils import md5_hex, pkcs7_pad, pkcs7_unpad
from src_shared_py.crypto.protobuf import ProtoBuf


class TestSM3:
    """Test SM3 hash algorithm"""
    
    def test_sm3_empty_string(self):
        """Test SM3 with empty string"""
        sm3 = SM3()
        result = sm3.sm3_hash("")
        assert len(result) == 32  # 256 bits = 32 bytes
    
    def test_sm3_hello_world(self):
        """Test SM3 with known input"""
        sm3 = SM3()
        result = sm3.sm3_hash("Hello, World!")
        assert len(result) == 32
        assert isinstance(result, bytes)
    
    def test_sm3_consistency(self):
        """Test SM3 produces consistent results"""
        sm3 = SM3()
        data = "test data"
        result1 = sm3.sm3_hash(data)
        result2 = sm3.sm3_hash(data)
        assert result1 == result2


class TestSimonCipher:
    """Test Simon cipher"""
    
    def test_simon_encryption_decryption(self):
        """Test Simon encrypt and decrypt"""
        key = [0x123456789ABCDEF0, 0xFEDCBA9876543210,
               0x0123456789ABCDEF, 0xFEDCBA0987654321]
        plaintext = [0x1234567890ABCDEF, 0xFEDCBA0987654321]
        
        # Encrypt
        ciphertext = simon_enc(plaintext, key)
        assert len(ciphertext) == 2
        
        # Decrypt
        decrypted = simon_dec(ciphertext, key)
        assert decrypted == plaintext
    
    def test_simon_different_plaintexts(self):
        """Test Simon with different plaintexts produce different ciphertexts"""
        key = [0x1111111111111111, 0x2222222222222222,
               0x3333333333333333, 0x4444444444444444]
        pt1 = [0x1111111111111111, 0x2222222222222222]
        pt2 = [0x3333333333333333, 0x4444444444444444]
        
        ct1 = simon_enc(pt1, key)
        ct2 = simon_enc(pt2, key)
        assert ct1 != ct2


class TestBufferUtils:
    """Test buffer utility functions"""
    
    def test_hex_conversion(self):
        """Test hex to bytes and back"""
        hex_str = "48656c6c6f"
        data = hex_to_bytes(hex_str)
        assert data == b"Hello"
        assert bytes_to_hex(data) == hex_str
    
    def test_bytes_to_hex(self):
        """Test bytes to hex conversion"""
        data = b"\x00\x01\x02\xff"
        hex_str = bytes_to_hex(data)
        assert hex_str == "000102ff"


class TestCryptoUtils:
    """Test crypto utility functions"""
    
    def test_md5_hex(self):
        """Test MD5 hex hash"""
        result = md5_hex("Hello, World!")
        assert len(result) == 32  # MD5 hex is 32 characters
        assert result == "65a8e27d8879283831b664bd8b7f0ad4"
    
    def test_pkcs7_padding(self):
        """Test PKCS7 padding and unpadding"""
        data = b"Hello"
        padded = pkcs7_pad(data, 16)
        assert len(padded) % 16 == 0
        unpadded = pkcs7_unpad(padded)
        assert unpadded == data


class TestProtobuf:
    """Test protobuf encoder/decoder"""
    
    def test_protobuf_varint(self):
        """Test protobuf varint encoding"""
        pb = ProtoBuf()
        pb.put_varint(1, 150)
        
        data = pb.to_buf()
        assert len(data) > 0
        
        # Decode
        pb2 = ProtoBuf(data)
        field = pb2.get(1)
        assert field is not None
        assert field.val == 150
    
    def test_protobuf_string(self):
        """Test protobuf string encoding"""
        pb = ProtoBuf()
        pb.put_utf8(1, "Hello")
        
        data = pb.to_buf()
        pb2 = ProtoBuf(data)
        field = pb2.get(1)
        assert field is not None
        assert field.val == b"Hello"
    
    def test_protobuf_dict(self):
        """Test protobuf from dictionary"""
        data_dict = {
            1: 100,
            2: "test",
            3: {
                1: 200,
                2: "nested"
            }
        }
        
        pb = ProtoBuf(data_dict)
        data = pb.to_buf()
        assert len(data) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
