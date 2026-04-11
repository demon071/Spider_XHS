"""
Ladon Encryption
Converted from: src/shared/tiktok-signer/ladon.ts

Ladon is a custom block cipher used for TikTok API signature generation.
"""

from typing import Optional
from ..crypto.buffer_utils import (
    read_bigint64_le,
    write_bigint64_le,
    concat_bytes,
    string_to_bytes,
    bytes_to_base64,
    random_bytes,
    alloc_bytes,
    ascii_to_bytes,
    fill_bytes,
)
from ..crypto.crypto_utils import md5_hex

# 64-bit mask
UINT64_MASK = 0xFFFFFFFFFFFFFFFF


def validate(num: int) -> int:
    """Ensure number is within 64-bit unsigned range"""
    return num & UINT64_MASK


def rotate_right(value: int, count: int) -> int:
    """Rotate right for 64-bit integer"""
    count = count % 64
    return ((value >> count) | (value << (64 - count))) & UINT64_MASK


def padding_size(size: int, block: int = 16) -> int:
    """PKCS7 padding size calculation"""
    mod = size % block
    if mod > 0:
        return size + (block - mod)
    return size


def pkcs7_pad(buf: bytearray, size: int, new_size: int):
    """Apply PKCS7 padding"""
    pad_val = new_size - size
    fill_bytes(buf, pad_val, size, new_size)


class Ladon:
    """Ladon encryption for TikTok signatures"""
    
    ROUNDS = 0x22  # 34 rounds
    
    @staticmethod
    def _build_hash_table(md5hex: str) -> bytearray:
        """
        Build hash table from MD5 hex string
        
        Args:
            md5hex: 32-character MD5 hex string
        
        Returns:
            288-byte hash table
        """
        hash_table = alloc_bytes(272 + 16)
        
        # Copy ASCII representation of MD5 hex string
        md5buf = ascii_to_bytes(md5hex)  # 32 bytes
        hash_table[0:32] = md5buf
        
        temp = []
        for i in range(4):
            temp.append(read_bigint64_le(bytes(hash_table), i * 8))
        
        buffer_b0 = temp[0]
        buffer_b8 = temp[1]
        temp = temp[2:]
        
        for i in range(Ladon.ROUNDS):
            x9 = buffer_b0
            x8 = buffer_b8
            
            x8 = validate(rotate_right(x8, 8))
            x8 = validate(x8 + x9)
            x8 = validate(x8 ^ i)
            
            temp.append(x8)
            
            x8 = validate(x8 ^ rotate_right(x9, 61))
            
            # Write to hash_table
            offset = (i + 1) * 8
            hash_table[offset:offset + 8] = write_bigint64_le(x8)
            
            buffer_b0 = x8
            buffer_b8 = temp.pop(0)
        
        return hash_table
    
    @staticmethod
    def _encrypt_ladon_input(hash_table: bytes, input_data: bytes) -> bytes:
        """
        Encrypt 16-byte block
        
        Args:
            hash_table: 288-byte hash table
            input_data: 16-byte input block
        
        Returns:
            16-byte encrypted block
        """
        data0 = read_bigint64_le(input_data, 0)
        data1 = read_bigint64_le(input_data, 8)
        
        for i in range(Ladon.ROUNDS):
            hash_val = read_bigint64_le(hash_table, i * 8)
            rot = validate((data1 >> 8) | (data1 << 56))
            
            data1 = validate(hash_val ^ (data0 + rot))
            data0 = validate(data1 ^ rotate_right(data0, 61))
        
        out = alloc_bytes(16)
        out[0:8] = write_bigint64_le(data0)
        out[8:16] = write_bigint64_le(data1)
        return bytes(out)
    
    @staticmethod
    def _encrypt_ladon(md5hex_str: str, data: bytes) -> bytes:
        """
        Encrypt data using Ladon algorithm
        
        Args:
            md5hex_str: 32-character MD5 hex string (used as key)
            data: Data to encrypt
        
        Returns:
            Encrypted data
        """
        hash_table = Ladon._build_hash_table(md5hex_str)
        
        size = len(data)
        new_size = padding_size(size)
        
        input_buf = alloc_bytes(new_size)
        input_buf[0:size] = data
        pkcs7_pad(input_buf, size, new_size)
        
        output = alloc_bytes(new_size)
        
        for i in range(new_size // 16):
            block = bytes(input_buf[i * 16:(i + 1) * 16])
            enc = Ladon._encrypt_ladon_input(hash_table, block)
            output[i * 16:(i + 1) * 16] = enc
        
        return bytes(output)
    
    @staticmethod
    def encrypt(khronos: int, license_id: int = 1611921764, aid: int = 1233,
                rand_bytes_data: Optional[bytes] = None) -> str:
        """
        Generate X-Ladon header value
        
        Args:
            khronos: Unix timestamp (seconds)
            license_id: License ID (default 1611921764)
            aid: App ID (default 1233)
            rand_bytes_data: Optional 4 random bytes (generated if not provided)
        
        Returns:
            Base64-encoded Ladon signature
        """
        if rand_bytes_data is None:
            rand_bytes_data = random_bytes(4)
        
        data = f"{khronos}-{license_id}-{aid}"
        keygen = concat_bytes(rand_bytes_data, string_to_bytes(str(aid)))
        md5hex = md5_hex(keygen)  # 32-character hex string
        
        raw = string_to_bytes(data)
        encrypted = Ladon._encrypt_ladon(md5hex, raw)
        
        output = concat_bytes(rand_bytes_data, encrypted)
        
        return bytes_to_base64(output)
