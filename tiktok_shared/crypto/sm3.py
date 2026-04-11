"""
SM3 Hash Algorithm Implementation
Converted from: src/shared/tiktok-signer/sm3.ts

SM3 is a cryptographic hash function used in China, similar to SHA-256.
Produces 256-bit (32-byte) hash output.
"""

from typing import Union, List


class SM3:
    """SM3 Hash Algorithm"""
    
    IV = [
        1937774191, 1226093241, 388252375, 3666478592,
        2842636476, 372324522, 3817729613, 2969243214
    ]
    
    TJ = [2043430169] * 16 + [2055708042] * 48
    
    def __init__(self):
        pass
    
    @staticmethod
    def _rotate_left(a: int, k: int) -> int:
        """Rotate left operation for 32-bit integer"""
        k = k & 31  # k % 32
        return ((a << k) | (a >> (32 - k))) & 0xFFFFFFFF
    
    def _FFJ(self, X: int, Y: int, Z: int, j: int) -> int:
        """Boolean function FF"""
        if 0 <= j < 16:
            return (X ^ Y ^ Z) & 0xFFFFFFFF
        else:
            return ((X & Y) | (X & Z) | (Y & Z)) & 0xFFFFFFFF
    
    def _GGJ(self, X: int, Y: int, Z: int, j: int) -> int:
        """Boolean function GG"""
        if 0 <= j < 16:
            return (X ^ Y ^ Z) & 0xFFFFFFFF
        else:
            return ((X & Y) | ((~X & 0xFFFFFFFF) & Z)) & 0xFFFFFFFF
    
    def _P_0(self, X: int) -> int:
        """Permutation P0"""
        return (X ^ self._rotate_left(X, 9) ^ self._rotate_left(X, 17)) & 0xFFFFFFFF
    
    def _P_1(self, X: int) -> int:
        """Permutation P1"""
        return (X ^ self._rotate_left(X, 15) ^ self._rotate_left(X, 23)) & 0xFFFFFFFF
    
    def _CF(self, V_i: List[int], B_i: bytes) -> List[int]:
        """Compression function"""
        # W[0..67]
        W = [0] * 68
        
        # Build W[0..15] from B_i (big-endian per 4 bytes)
        for i in range(16):
            off = i * 4
            v = ((B_i[off] << 24) |
                 (B_i[off + 1] << 16) |
                 (B_i[off + 2] << 8) |
                 B_i[off + 3]) & 0xFFFFFFFF
            W[i] = v
        
        # Expand W[16..67]
        for j in range(16, 68):
            term = (W[j - 16] ^ W[j - 9] ^ self._rotate_left(W[j - 3], 15)) & 0xFFFFFFFF
            W[j] = (self._P_1(term) ^ self._rotate_left(W[j - 13], 7) ^ W[j - 6]) & 0xFFFFFFFF
        
        # W1[0..63]
        W1 = [0] * 64
        for j in range(64):
            W1[j] = (W[j] ^ W[j + 4]) & 0xFFFFFFFF
        
        # Initialize working variables
        A, B, C, D, E, F, G, H = [x & 0xFFFFFFFF for x in V_i]
        
        # Main loop
        for j in range(64):
            rlA12 = self._rotate_left(A, 12)
            t = (rlA12 + E + self._rotate_left(self.TJ[j], j)) & 0xFFFFFFFF
            SS1 = self._rotate_left(t, 7)
            SS2 = (SS1 ^ rlA12) & 0xFFFFFFFF
            TT1 = (self._FFJ(A, B, C, j) + D + SS2 + W1[j]) & 0xFFFFFFFF
            TT2 = (self._GGJ(E, F, G, j) + H + SS1 + W[j]) & 0xFFFFFFFF
            
            D = C
            C = self._rotate_left(B, 9)
            B = A
            A = TT1 & 0xFFFFFFFF
            H = G
            G = self._rotate_left(F, 19)
            F = E
            E = self._P_0(TT2) & 0xFFFFFFFF
        
        # Return new state
        return [
            (A ^ V_i[0]) & 0xFFFFFFFF,
            (B ^ V_i[1]) & 0xFFFFFFFF,
            (C ^ V_i[2]) & 0xFFFFFFFF,
            (D ^ V_i[3]) & 0xFFFFFFFF,
            (E ^ V_i[4]) & 0xFFFFFFFF,
            (F ^ V_i[5]) & 0xFFFFFFFF,
            (G ^ V_i[6]) & 0xFFFFFFFF,
            (H ^ V_i[7]) & 0xFFFFFFFF,
        ]
    
    def sm3_hash(self, msg_input: Union[bytes, bytearray, str]) -> bytes:
        """
        Compute SM3 hash
        
        Args:
            msg_input: Input message (bytes, bytearray, or string)
        
        Returns:
            32-byte hash digest
        """
        # Normalize input to bytes
        if isinstance(msg_input, str):
            msg = msg_input.encode('utf-8')
        elif isinstance(msg_input, bytearray):
            msg = bytes(msg_input)
        else:
            msg = msg_input
        
        # Convert to mutable list
        m_arr = list(msg)
        
        len1 = len(m_arr)
        reserve1 = len1 % 64
        
        # Append 0x80
        m_arr.append(0x80)
        reserve1 += 1
        
        # Pad with 0x00 until length ≡ 56 (mod 64)
        range_end = 56
        if reserve1 > range_end:
            range_end += 64
        for i in range(reserve1, range_end):
            m_arr.append(0x00)
        
        # Append 64-bit big-endian length (bit length)
        bit_length = len1 * 8
        len_bytes = [0] * 8
        for i in range(7, -1, -1):
            len_bytes[i] = bit_length & 0xFF
            bit_length //= 256
        m_arr.extend(len_bytes)
        
        # Group into 64-byte blocks
        total_groups = len(m_arr) // 64
        B = []
        for i in range(total_groups):
            start = i * 64
            block = bytes(m_arr[start:start + 64])
            B.append(block)
        
        # Iterative compression
        V = [self.IV[:]]
        for i in range(total_groups):
            V.append(self._CF(V[i], B[i]))
        
        # Final hash value
        y = V[-1]
        
        # Convert to big-endian bytes
        res = bytearray(32)
        for i in range(8):
            v = y[i] & 0xFFFFFFFF
            res[i * 4 + 0] = (v >> 24) & 0xFF
            res[i * 4 + 1] = (v >> 16) & 0xFF
            res[i * 4 + 2] = (v >> 8) & 0xFF
            res[i * 4 + 3] = v & 0xFF
        
        return bytes(res)
