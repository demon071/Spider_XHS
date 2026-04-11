"""
Gorgon Signature Generator
Converted from: src/shared/tiktok-signer/gorgon.ts

Generates X-Gorgon, X-Khronos, and x-ss-req-ticket headers for TikTok API requests.
"""

from typing import Dict, Optional
from ..crypto.crypto_utils import md5_hex


class Gorgon:
    """Gorgon signature generator for TikTok API"""
    
    def __init__(self, params: str, unix: int, body_payload: Optional[str] = None,
                 cookies: Optional[str] = None):
        """
        Initialize Gorgon signature generator
        
        Args:
            params: Query parameters string
            unix: Unix timestamp (seconds)
            body_payload: Optional request body
            cookies: Optional cookies string
        """
        self.unix = unix
        self.params = params
        self.body_payload = body_payload
        self.cookies = cookies
    
    def _hash(self, data: str) -> str:
        """Compute MD5 hash"""
        return md5_hex(data)
    
    def _get_base_string(self) -> str:
        """Build base string for encryption"""
        base = self._hash(self.params)
        base += self._hash(self.body_payload) if self.body_payload else '0' * 32
        base += self._hash(self.cookies) if self.cookies else '0' * 32
        return base
    
    def get_value(self) -> Dict[str, str]:
        """
        Generate Gorgon signature headers
        
        Returns:
            Dictionary with X-Gorgon, X-Khronos, x-ss-req-ticket
        """
        return self._encrypt(self._get_base_string())
    
    def _encrypt(self, data: str) -> Dict[str, str]:
        """
        Encrypt data to generate Gorgon signature
        
        Args:
            data: 96-character hex string (3 MD5 hashes concatenated)
        
        Returns:
            Dictionary with signature headers
        """
        LEN = 0x14  # 20 bytes
        
        key = [
            0xDF, 0x77, 0xB9, 0x40, 0xB9, 0x9B, 0x84, 0x83, 0xD1, 0xB9,
            0xCB, 0xD1, 0xF7, 0xC2, 0xB9, 0x85, 0xC3, 0xD0, 0xFB, 0xC3
        ]
        
        param_list = []
        
        # Get first 12 bytes from 96 hex characters (48 bytes)
        for i in range(0, 12, 4):
            temp = data[8 * i:8 * (i + 1)]  # 8 hex chars = 4 bytes
            for j in range(4):
                value = int(temp[j * 2:(j + 1) * 2], 16)
                param_list.append(value)
        
        # Append fixed values
        param_list.extend([0x00, 0x06, 0x0B, 0x1C])
        
        # Append timestamp (4 bytes)
        ts = self.unix & 0xFFFFFFFF
        param_list.append((ts & 0xFF000000) >> 24)
        param_list.append((ts & 0x00FF0000) >> 16)
        param_list.append((ts & 0x0000FF00) >> 8)
        param_list.append((ts & 0x000000FF) >> 0)
        
        # XOR param_list with key
        eor_list = [param_list[i] ^ key[i] for i in range(LEN)]
        
        # Main encryption loop
        for i in range(LEN):
            C = self._reverse(eor_list[i])
            D = eor_list[(i + 1) % LEN]
            E = C ^ D
            F = self._rbit(E)
            H = (F ^ 0xFFFFFFFF ^ LEN) & 0xFF
            eor_list[i] = H
        
        # Convert to hex string
        result = ''.join(self._to_hex(p) for p in eor_list)
        
        return {
            'x-ss-req-ticket': str(self.unix * 1000),
            'X-Khronos': str(self.unix),
            'X-Gorgon': '0404b0d30000' + result
        }
    
    def _reverse(self, num: int) -> int:
        """Reverse hex digits: e.g. A4 => 4A"""
        hex_str = self._to_hex(num)
        return int(hex_str[1] + hex_str[0], 16)
    
    def _to_hex(self, num: int) -> str:
        """Convert number to 2-byte hex string"""
        return format(num, '02x')
    
    def _rbit(self, num: int) -> int:
        """Reverse bits of byte"""
        bin_str = format(num, '08b')
        rev = bin_str[::-1]
        return int(rev, 2)
