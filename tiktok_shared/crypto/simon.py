"""
Simon Cipher Implementation
Converted from: src/shared/tiktok-signer/simon.ts

Simon is a family of lightweight block ciphers designed by the NSA.
This implementation uses Simon 128/256 (128-bit blocks, 256-bit keys).
"""

from typing import List

# 64-bit mask
MASK64 = 0xFFFFFFFFFFFFFFFF


def get_bit(val: int, pos: int) -> int:
    """Get bit at position"""
    return 1 if (val & (1 << pos)) != 0 else 0


def rotate_left(v: int, n: int) -> int:
    """Rotate left for 64-bit integer"""
    return ((v << n) | (v >> (64 - n))) & MASK64


def rotate_right(v: int, n: int) -> int:
    """Rotate right for 64-bit integer"""
    return ((v >> n) | (v << (64 - n))) & MASK64


def key_expansion(key: List[int]) -> List[int]:
    """
    Expand 256-bit key to 72 round keys
    
    Args:
        key: List of 4 64-bit integers (256 bits total)
    
    Returns:
        List of 72 64-bit round keys
    """
    expanded_key = [0] * 72
    expanded_key[0] = key[0]
    expanded_key[1] = key[1]
    expanded_key[2] = key[2]
    expanded_key[3] = key[3]
    
    for i in range(4, 72):
        tmp = rotate_right(expanded_key[i - 1], 3)
        tmp = tmp ^ expanded_key[i - 3]
        tmp = tmp ^ rotate_right(tmp, 1)
        
        bit = get_bit(0x3DC94C3A046D678B, (i - 4) % 62)
        
        expanded_key[i] = ((~expanded_key[i - 4] & MASK64) ^ tmp ^ bit ^ 3) & MASK64
    
    return expanded_key


def simon_enc(pt: List[int], k: List[int], c: int = 0) -> List[int]:
    """
    Simon encryption
    
    Args:
        pt: Plaintext as list of 2 64-bit integers
        k: Key as list of 4 64-bit integers
        c: Cipher variant (0 for standard)
    
    Returns:
        Ciphertext as list of 2 64-bit integers
    """
    key = key_expansion(k)
    
    x_i = pt[0]
    x_i1 = pt[1]
    
    for i in range(72):
        tmp = x_i1
        
        if c == 1:
            f = rotate_left(x_i1, 1)
        else:
            f = rotate_left(x_i1, 1) & rotate_left(x_i1, 8)
        
        x_i1 = (x_i ^ f ^ rotate_left(x_i1, 2) ^ key[i]) & MASK64
        x_i = tmp
    
    return [x_i, x_i1]


def simon_dec(ct: List[int], k: List[int], c: int = 0) -> List[int]:
    """
    Simon decryption
    
    Args:
        ct: Ciphertext as list of 2 64-bit integers
        k: Key as list of 4 64-bit integers
        c: Cipher variant (0 for standard)
    
    Returns:
        Plaintext as list of 2 64-bit integers
    """
    key = key_expansion(k)
    
    x_i = ct[0]
    x_i1 = ct[1]
    
    for i in range(71, -1, -1):
        tmp = x_i
        
        if c == 1:
            f = rotate_left(x_i, 1)
        else:
            f = rotate_left(x_i, 1) & rotate_left(x_i, 8)
        
        x_i = (x_i1 ^ f ^ rotate_left(x_i, 2) ^ key[i]) & MASK64
        x_i1 = tmp
    
    return [x_i, x_i1]
