"""
Cryptographic utility functions
Converted from: src/shared/tiktok-signer/crypto-utils.ts
"""

import hashlib
from typing import Union
from Crypto.Cipher import AES
from .buffer_utils import hex_to_bytes


def md5_hex(data: Union[str, bytes]) -> str:
    """Compute MD5 hash and return as hex string"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.md5(data).hexdigest()


def md5_bytes(data: Union[str, bytes]) -> bytes:
    """Compute MD5 hash and return as bytes"""
    return hex_to_bytes(md5_hex(data))


def aes_cbc_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    """
    AES-CBC encryption
    
    Args:
        data: Data to encrypt (should already be padded)
        key: 16-byte encryption key
        iv: 16-byte initialization vector
    
    Returns:
        Encrypted data
    """
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(data)


def aes_cbc_decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    """
    AES-CBC decryption
    
    Args:
        data: Encrypted data
        key: 16-byte decryption key
        iv: 16-byte initialization vector
    
    Returns:
        Decrypted data (may include padding)
    """
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(data)


def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    """
    Apply PKCS7 padding
    
    Args:
        data: Data to pad
        block_size: Block size (default 16 for AES)
    
    Returns:
        Padded data
    """
    pad_len = block_size - (len(data) % block_size)
    padding = bytes([pad_len] * pad_len)
    return data + padding


def pkcs7_unpad(data: bytes) -> bytes:
    """
    Remove PKCS7 padding
    
    Args:
        data: Padded data
    
    Returns:
        Unpadded data
    """
    if not data:
        return data
    pad_len = data[-1]
    return data[:-pad_len]


def pkcs7_padding_data_length(buffer: bytes, buffer_size: int, modulus: int) -> int:
    """
    Return unpadded data length, or 0 if padding invalid
    Converted from: src/shared/tiktok-signer/pkcs7_padding.ts
    """
    if buffer_size % modulus != 0 or buffer_size < modulus:
        return 0
    
    padding_value = buffer[buffer_size - 1]
    
    if padding_value < 1 or padding_value > modulus:
        return 0
    
    if buffer_size < padding_value + 1:
        return 0
    
    count = 1
    buffer_size -= 1
    
    for i in range(count, padding_value):
        buffer_size -= 1
        if buffer[buffer_size] != padding_value:
            return 0
    
    return buffer_size


def padding_size(size: int, block: int = 16) -> int:
    """Return padded size to nearest block size"""
    mod = size % block
    if mod > 0:
        return size + (block - mod)
    return size
