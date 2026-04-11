"""
Argus Signature Generator
Converted from: src/shared/tiktok-signer/argus.ts

Generates X-Argus header for TikTok API requests using SM3, Simon cipher, and AES-CBC.
"""

import time
import random
from typing import Dict, Optional, Any
from urllib.parse import parse_qs
from ..crypto.buffer_utils import (
    hex_to_bytes,
    alloc_bytes,
    string_to_bytes,
    read_bigint64_le,
    write_bigint64_le_to,
    concat_bytes,
    ascii_to_bytes,
    bytes_to_base64,
)
from ..crypto.crypto_utils import md5_bytes, aes_cbc_encrypt, pkcs7_pad
from ..crypto.protobuf import ProtoBuf
from ..crypto.simon import simon_enc
from ..crypto.sm3 import SM3


def pkcs7_pad_bytes(buf: bytes, block_size: int = 16) -> bytes:
    """PKCS7 padding for bytes"""
    pad = block_size - (len(buf) % block_size)
    out = alloc_bytes(len(buf) + pad)
    out[0:len(buf)] = buf
    out[len(buf):] = bytes([pad] * pad)
    return bytes(out)


class Argus:
    """Argus signature generator"""
    
    # Sign key and SM3 output constants (from TypeScript)
    SIGN_KEY = hex_to_bytes(
        'ac1adaae95a7af94a5114ab3b3a97dd80050aa0a39314c40528caec95256c28c'
    )
    SM3_OUTPUT = hex_to_bytes(
        'fc78e0a9657a0c748ce51559903ccf03510e51d3cff232d71343e88a321c5304'
    )
    
    @staticmethod
    def _encrypt_enc_pb(data: bytes, length: int) -> bytes:
        """
        Encrypt protobuf data with XOR and reverse
        
        Args:
            data: Data to encrypt
            length: Length to process
        
        Returns:
            Encrypted data
        """
        arr = bytearray(data[0:length])
        xor_array = arr[0:8]
        
        for i in range(8, length):
            arr[i] = arr[i] ^ xor_array[i % 8]
        
        # Reverse bytes
        reversed_arr = bytes(arr[::-1])
        return reversed_arr
    
    @staticmethod
    def get_bodyhash(stub: Optional[str]) -> bytes:
        """
        Get body hash using SM3
        
        Args:
            stub: Optional hex string of body MD5
        
        Returns:
            First 6 bytes of SM3 hash
        """
        if not stub or len(stub) == 0:
            return SM3().sm3_hash(bytes(16))[0:6]
        
        stub_bytes = hex_to_bytes(stub)
        return SM3().sm3_hash(stub_bytes)[0:6]
    
    @staticmethod
    def get_queryhash(query: Optional[str]) -> bytes:
        """
        Get query hash using SM3
        
        Args:
            query: Optional query string
        
        Returns:
            First 6 bytes of SM3 hash
        """
        if not query or len(query) == 0:
            return SM3().sm3_hash(alloc_bytes(16))[0:6]
        
        return SM3().sm3_hash(string_to_bytes(query))[0:6]
    
    @staticmethod
    def _prepare_key_list(key: bytes) -> list:
        """
        Prepare key list for Simon cipher
        
        Args:
            key: 32-byte key
        
        Returns:
            List of 4 64-bit integers
        """
        key_list = []
        for i in range(2):
            slice_data = key[i * 16:(i + 1) * 16]
            lo = read_bigint64_le(slice_data, 0)
            hi = read_bigint64_le(slice_data, 8)
            key_list.extend([lo, hi])
        return key_list
    
    @staticmethod
    def _encrypt_blocks(protobuf: bytes, key_list: list, new_len: int) -> bytes:
        """
        Encrypt protobuf blocks using Simon cipher
        
        Args:
            protobuf: Padded protobuf data
            key_list: Simon key list
            new_len: Length of data
        
        Returns:
            Encrypted data
        """
        enc_pb = alloc_bytes(new_len)
        block_count = new_len // 16
        
        for block_idx in range(block_count):
            offset = block_idx * 16
            a = read_bigint64_le(protobuf, offset)
            b = read_bigint64_le(protobuf, offset + 8)
            pt = [a, b]
            ct = simon_enc(pt, key_list)
            write_bigint64_le_to(enc_pb, ct[0], offset)
            write_bigint64_le_to(enc_pb, ct[1], offset + 8)
        
        return bytes(enc_pb)
    
    @staticmethod
    def encrypt(xargus_bean: Dict[int, Any]) -> str:
        """
        Encrypt Argus bean to signature
        
        Args:
            xargus_bean: Dictionary with Argus parameters
        
        Returns:
            Base64-encoded signature
        """
        # Build protobuf
        pb = ProtoBuf(xargus_bean).to_buf()
        
        # Pad to AES block size
        protobuf = pkcs7_pad_bytes(pb, 16)
        new_len = len(protobuf)
        
        # Prepare key and encrypt with Simon
        key = Argus.SM3_OUTPUT[0:32]
        key_list = Argus._prepare_key_list(key)
        enc_pb = Argus._encrypt_blocks(protobuf, key_list, new_len)
        
        # Add header and encrypt
        header = bytes([0xF2, 0xF7, 0xFC, 0xFF, 0xF2, 0xF7, 0xFC, 0xFF])
        b_buffer = concat_bytes(header, enc_pb)
        b_buffer = Argus._encrypt_enc_pb(b_buffer, new_len + 8)
        b_buffer = concat_bytes(
            bytes([0xA6, 0x6E, 0xAD, 0x9F, 0x77, 0x01, 0xD0, 0x0C, 0x18]),
            b_buffer,
            ascii_to_bytes('ao')
        )
        
        # AES-CBC encryption
        key_md5 = md5_bytes(Argus.SIGN_KEY[0:16])
        iv_md5 = md5_bytes(Argus.SIGN_KEY[16:])
        
        to_encrypt = pkcs7_pad(b_buffer, 16)
        encrypted = aes_cbc_encrypt(to_encrypt, key_md5, iv_md5)
        
        out = concat_bytes(bytes([0xF2, 0x81]), encrypted)
        return bytes_to_base64(out)
    
    @staticmethod
    def _parse_app_version(version_name: str) -> int:
        """
        Parse app version string to integer
        
        Args:
            version_name: Version string like "41.4.5"
        
        Returns:
            Parsed version as integer
        """
        parts = version_name.split('.')
        p0 = int(parts[0]) if len(parts) > 0 else 0
        p1 = int(parts[1]) if len(parts) > 1 else 0
        p2 = int(parts[2]) if len(parts) > 2 else 0
        
        hex_str = (
            format(p2 * 4, 'x') +
            format(p1 * 16, 'x') +
            format(p0 * 4, 'x') +
            '00'
        ).zfill(8)
        
        num = int(hex_str, 16)
        return (num << 1) & 0xFFFFFFFF
    
    @staticmethod
    def get_sign(
        query_params: str = '',
        x_ss_stub: Optional[str] = None,
        timestamp: Optional[int] = None,
        aid: int = 1233,
        license_id: int = 1611921764,
        platform: int = 0,
        sec_device_id: str = '',
        sdk_version: str = 'v05.00.03-ov-android',
        sdk_version_int: int = 167773760
    ) -> str:
        """
        Generate X-Argus signature
        
        Args:
            query_params: Query string
            x_ss_stub: Optional body MD5 stub
            timestamp: Unix timestamp (auto-generated if None)
            aid: App ID
            license_id: License ID
            platform: Platform (0 for Android)
            sec_device_id: Secure device ID
            sdk_version: SDK version string
            sdk_version_int: SDK version as integer
        
        Returns:
            Base64-encoded X-Argus signature
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        # Parse query string
        params = parse_qs(query_params)
        
        def get_first(k: str) -> str:
            v = params.get(k, [''])
            if isinstance(v, list):
                return str(v[0]) if v else ''
            return str(v)
        
        app_version_constant = Argus._parse_app_version(get_first('version_name'))
        
        # Build xargus_bean
        xargus_bean = {
            1: 0x20200929 * 2,
            2: 2,
            3: random.randint(0, 0x7FFFFFFF),
            4: str(aid),
            5: get_first('device_id'),
            6: str(license_id),
            7: get_first('version_name'),
            8: sdk_version,
            9: sdk_version_int,
            10: bytes(8),  # Empty 8 bytes
            11: 'android',
            12: timestamp * 2,
            13: Argus.get_bodyhash(x_ss_stub),
            14: Argus.get_queryhash(query_params),
            15: {
                1: 85,
                2: 85,
                3: 85,
                5: 85,
                6: 170,
                7: timestamp * 2 - 310
            },
            16: sec_device_id,
            20: 'none',
            21: 738,
            23: {
                1: get_first('device_type'),
                2: 0,
                3: 'googleplay',
                4: app_version_constant
            },
            25: 2
        }
        
        return Argus.encrypt(xargus_bean)
