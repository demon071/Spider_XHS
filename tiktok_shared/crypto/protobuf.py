"""
Protocol Buffer (Protobuf) Encoder/Decoder
Converted from: src/shared/tiktok-signer/protobuf.ts

Custom protobuf implementation for encoding/decoding binary data.
"""

from typing import Dict, Any, List, Union
from enum import IntEnum


class ProtoError(Exception):
    """Protobuf error"""
    pass


class ProtoFieldType(IntEnum):
    """Protobuf field wire types"""
    VARINT = 0
    INT64 = 1
    STRING = 2
    GROUPSTART = 3
    GROUPEND = 4
    INT32 = 5
    ERROR1 = 6
    ERROR2 = 7


class ProtoField:
    """Protobuf field"""
    
    def __init__(self, idx: int, field_type: ProtoFieldType, val: Any):
        self.idx = idx
        self.type = field_type
        self.val = val
    
    def is_ascii_str(self) -> bool:
        """Check if value is ASCII string"""
        if not isinstance(self.val, bytes):
            return False
        try:
            for b in self.val:
                if b < 0x20 or b > 0x7E:
                    return False
            return True
        except:
            return False
    
    def __str__(self) -> str:
        if self.type in (ProtoFieldType.INT32, ProtoFieldType.INT64, ProtoFieldType.VARINT):
            return f"{self.idx}({self.type.name}): {self.val}"
        elif self.type == ProtoFieldType.STRING:
            if self.is_ascii_str():
                return f'{self.idx}({self.type.name}): "{self.val.decode("ascii")}"'
            return f'{self.idx}({self.type.name}): h"{self.val.hex()}"'
        else:
            return f"{self.idx}({self.type.name}): {self.val}"


class ProtoReader:
    """Protobuf binary reader"""
    
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
    
    def seek(self, pos: int):
        """Seek to position"""
        self.pos = pos
    
    def is_remain(self, length: int) -> bool:
        """Check if enough bytes remain"""
        return self.pos + length <= len(self.data)
    
    def read0(self) -> int:
        """Read single byte"""
        if not self.is_remain(1):
            raise ProtoError("read0(): Out of bounds")
        val = self.data[self.pos] & 0xFF
        self.pos += 1
        return val
    
    def read(self, length: int) -> bytes:
        """Read multiple bytes"""
        if not self.is_remain(length):
            raise ProtoError("read(): Out of bounds")
        ret = self.data[self.pos:self.pos + length]
        self.pos += length
        return ret
    
    def read_int32(self) -> int:
        """Read 32-bit little-endian integer"""
        b = self.read(4)
        return (b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24)) & 0xFFFFFFFF
    
    def read_int64(self) -> int:
        """Read 64-bit little-endian integer"""
        b = self.read(8)
        return (b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24) |
                (b[4] << 32) | (b[5] << 40) | (b[6] << 48) | (b[7] << 56))
    
    def read_varint(self) -> int:
        """Read variable-length integer"""
        vint = 0
        shift = 0
        while True:
            byte = self.read0()
            vint |= (byte & 0x7F) << shift
            if byte < 0x80:
                break
            shift += 7
        return vint & 0xFFFFFFFF
    
    def read_string(self) -> bytes:
        """Read length-delimited bytes"""
        length = self.read_varint()
        return self.read(length)
    
    def eof(self) -> bool:
        """Check if at end of data"""
        return self.pos >= len(self.data)


class ProtoWriter:
    """Protobuf binary writer"""
    
    def __init__(self):
        self.data: List[int] = []
    
    def write0(self, byte: int):
        """Write single byte"""
        self.data.append(byte & 0xFF)
    
    def write(self, data: bytes):
        """Write multiple bytes"""
        self.data.extend(data)
    
    def write_int32(self, v: int):
        """Write 32-bit little-endian integer"""
        self.write(bytes([
            v & 0xFF,
            (v >> 8) & 0xFF,
            (v >> 16) & 0xFF,
            (v >> 24) & 0xFF,
        ]))
    
    def write_int64(self, v: int):
        """Write 64-bit little-endian integer"""
        self.write(bytes([
            v & 0xFF,
            (v >> 8) & 0xFF,
            (v >> 16) & 0xFF,
            (v >> 24) & 0xFF,
            (v >> 32) & 0xFF,
            (v >> 40) & 0xFF,
            (v >> 48) & 0xFF,
            (v >> 56) & 0xFF,
        ]))
    
    def write_varint(self, v: int):
        """Write variable-length integer"""
        v = v & 0xFFFFFFFF
        while v > 0x80:
            self.write0((v & 0x7F) | 0x80)
            v >>= 7
        self.write0(v & 0x7F)
    
    def write_string(self, data: bytes):
        """Write length-delimited bytes"""
        self.write_varint(len(data))
        self.write(data)
    
    def to_bytes(self) -> bytes:
        """Convert to bytes"""
        return bytes(self.data)


class ProtoBuf:
    """Protocol Buffer message"""
    
    def __init__(self, data: Union[bytes, Dict[int, Any], None] = None):
        self.fields: List[ProtoField] = []
        
        if isinstance(data, bytes) and len(data) > 0:
            self.parse_buf(data)
        elif isinstance(data, dict):
            self.parse_dict(data)
    
    def get(self, idx: int) -> Union[ProtoField, None]:
        """Get first field with index"""
        for f in self.fields:
            if f.idx == idx:
                return f
        return None
    
    def get_list(self, idx: int) -> List[ProtoField]:
        """Get all fields with index"""
        return [f for f in self.fields if f.idx == idx]
    
    def put(self, field: ProtoField):
        """Add field"""
        self.fields.append(field)
    
    def put_int32(self, idx: int, v: int):
        """Add INT32 field"""
        self.put(ProtoField(idx, ProtoFieldType.INT32, v))
    
    def put_int64(self, idx: int, v: int):
        """Add INT64 field"""
        self.put(ProtoField(idx, ProtoFieldType.INT64, v))
    
    def put_varint(self, idx: int, v: int):
        """Add VARINT field"""
        self.put(ProtoField(idx, ProtoFieldType.VARINT, v))
    
    def put_bytes(self, idx: int, b: bytes):
        """Add bytes field"""
        self.put(ProtoField(idx, ProtoFieldType.STRING, b))
    
    def put_utf8(self, idx: int, s: str):
        """Add UTF-8 string field"""
        self.put(ProtoField(idx, ProtoFieldType.STRING, s.encode('utf-8')))
    
    def put_protobuf(self, idx: int, pb: 'ProtoBuf'):
        """Add nested protobuf field"""
        self.put(ProtoField(idx, ProtoFieldType.STRING, pb.to_buf()))
    
    def parse_buf(self, data: bytes):
        """Parse from binary data"""
        r = ProtoReader(data)
        while r.is_remain(1):
            key = r.read_varint()
            wire_type = key & 7
            idx = key >> 3
            
            if idx == 0:
                break
            
            if wire_type == ProtoFieldType.INT32:
                self.put(ProtoField(idx, wire_type, r.read_int32()))
            elif wire_type == ProtoFieldType.INT64:
                self.put(ProtoField(idx, wire_type, r.read_int64()))
            elif wire_type == ProtoFieldType.VARINT:
                self.put(ProtoField(idx, wire_type, r.read_varint()))
            elif wire_type == ProtoFieldType.STRING:
                self.put(ProtoField(idx, wire_type, r.read_string()))
            else:
                raise ProtoError(f"Unexpected field type {wire_type}")
    
    def parse_dict(self, d: Dict[int, Any]):
        """Parse from dictionary"""
        for k, v in d.items():
            if isinstance(v, int):
                self.put_varint(k, v)
            elif isinstance(v, str):
                self.put_utf8(k, v)
            elif isinstance(v, bytes):
                self.put_bytes(k, v)
            elif isinstance(v, dict):
                self.put_protobuf(k, ProtoBuf(v))
            else:
                raise ProtoError(f"Unsupported type in dict: {type(v)}")
    
    def to_buf(self) -> bytes:
        """Encode to binary data"""
        w = ProtoWriter()
        for f in self.fields:
            key = (f.idx << 3) | (f.type & 7)
            w.write_varint(key)
            
            if f.type == ProtoFieldType.INT32:
                w.write_int32(f.val)
            elif f.type == ProtoFieldType.INT64:
                w.write_int64(f.val)
            elif f.type == ProtoFieldType.VARINT:
                w.write_varint(f.val)
            elif f.type == ProtoFieldType.STRING:
                w.write_string(f.val)
            else:
                raise ProtoError("Unexpected field type")
        
        return w.to_bytes()
