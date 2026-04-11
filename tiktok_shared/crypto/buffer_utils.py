"""
Buffer utility functions
Converted from: src/shared/tiktok-signer/buffer-utils.ts
"""

import struct
import base64
import os
from typing import Union


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex string to bytes"""
    return bytes.fromhex(hex_str)


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string"""
    return data.hex()


def string_to_bytes(s: str) -> bytes:
    """Convert string to bytes (UTF-8)"""
    return s.encode('utf-8')


def ascii_to_bytes(s: str) -> bytes:
    """Convert ASCII string to bytes"""
    return s.encode('ascii')


def bytes_to_string(data: bytes) -> str:
    """Convert bytes to string (UTF-8)"""
    return data.decode('utf-8')


def alloc_bytes(size: int) -> bytearray:
    """Allocate a new byte array with zeros"""
    return bytearray(size)


def read_bigint64_le(data: bytes, offset: int = 0) -> int:
    """Read 64-bit unsigned integer (little-endian) from bytes"""
    return struct.unpack_from('<Q', data, offset)[0]


def write_bigint64_le(value: int, offset: int = 0) -> bytes:
    """Write 64-bit unsigned integer (little-endian) to bytes"""
    return struct.pack('<Q', value)


def write_bigint64_le_to(data: bytearray, value: int, offset: int = 0) -> None:
    """Write 64-bit unsigned integer to existing byte array"""
    struct.pack_into('<Q', data, offset, value)


def concat_bytes(*arrays: bytes) -> bytes:
    """Concatenate multiple byte arrays"""
    return b''.join(arrays)


def fill_bytes(data: bytearray, value: int, start: int = 0, end: int = None) -> None:
    """Fill byte array with a value"""
    if end is None:
        end = len(data)
    for i in range(start, end):
        data[i] = value


def bytes_to_base64(data: bytes) -> str:
    """Convert bytes to base64 string"""
    return base64.b64encode(data).decode('ascii')


def base64_to_bytes(b64: str) -> bytes:
    """Convert base64 string to bytes"""
    return base64.b64decode(b64)


def random_bytes(size: int) -> bytes:
    """Generate random bytes"""
    return os.urandom(size)
