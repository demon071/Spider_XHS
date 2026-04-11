# TikTok Shared Library - Python

Thư viện Python để tương tác với TikTok Mobile API, được chuyển đổi từ TypeScript (`src/shared`).

## Tính năng

- ✅ **Chữ ký API TikTok Mobile**: Gorgon, Ladon, Argus
- ✅ **Mã hóa**: SM3 hash, Simon cipher, AES-CBC, MD5
- ✅ **Protocol Buffer**: Custom encoder/decoder
- ✅ **TikTok API Services**: User info, video list, video details
- ✅ **Type Safety**: Sử dụng dataclasses cho type hints

## Cài đặt

```bash
cd src_shared_py
pip install -r requirements.txt
```

## Cấu trúc Thư mục

```
src_shared_py/
├── __init__.py              # Main exports
├── constants.py             # API URLs và constants
├── types.py                 # Type definitions (dataclasses)
├── crypto/                  # Cryptographic modules
│   ├── buffer_utils.py     # Buffer operations
│   ├── crypto_utils.py     # MD5, AES-CBC, PKCS7
│   ├── sm3.py              # SM3 hash algorithm
│   ├── simon.py            # Simon cipher
│   └── protobuf.py         # Protobuf encoder/decoder
├── signer/                  # Signature generators
│   ├── gorgon.py           # X-Gorgon signature
│   ├── ladon.py            # X-Ladon signature
│   ├── argus.py            # X-Argus signature
│   └── mobile_headers.py   # Combined header generator
├── services/                # API services
│   └── tiktok_service.py   # TikTok API wrapper
└── utils/                   # Utilities
    └── tiktok_utils.py     # Response formatters
```

## Sử dụng Cơ bản

### 1. Lấy thông tin người dùng

```python
from src_shared_py.services.tiktok_service import TiktokService

# Tìm kiếm user bằng username
user = TiktokService.get_user_info("username")
print(f"User ID: {user.uid}")
print(f"Sec UID: {user.sec_uid}")
print(f"Followers: {user.follower_count}")
print(f"Videos: {user.aweme_count}")
```

### 2. Lấy danh sách video

```python
# Lấy video list của user
videos = TiktokService.get_user_aweme_list(user.sec_uid)

for aweme in videos.aweme_list:
    print(f"Video ID: {aweme.id}")
    print(f"Description: {aweme.description}")
    print(f"Views: {aweme.stats.views}")
    print(f"Likes: {aweme.stats.likes}")
    
    if aweme.type == "VIDEO":
        print(f"Video URL: {aweme.video.mp4_uri}")
    elif aweme.type == "PHOTO":
        print(f"Images: {len(aweme.images_uri)}")
    print("-" * 50)
```

### 3. Phân trang (Pagination)

```python
# Lấy trang đầu tiên
page1 = TiktokService.get_user_aweme_list(user.sec_uid)

# Kiểm tra có thêm video không
if page1.pagination.has_more:
    # Lấy trang tiếp theo
    page2 = TiktokService.get_user_aweme_list(
        user.sec_uid,
        max_cursor=page1.pagination.max_cursor,
        cursor=page1.pagination.cursor
    )
```

### 4. Lấy chi tiết video

```python
# Lấy thông tin chi tiết của 1 video
video_detail = TiktokService.get_aweme_details("7123456789012345678")
print(f"Title: {video_detail.description}")
print(f"Created: {video_detail.created_at}")
print(f"Type: {video_detail.type}")
```

### 5. Sử dụng với Cookies (cho private accounts)

```python
# Thêm cookies để truy cập private accounts
cookies = "sessionid=xxx; tt_webid=yyy; ..."

videos = TiktokService.get_user_aweme_list(
    sec_uid=user.sec_uid,
    cookie=cookies
)
```

## Sử dụng Nâng cao

### Tạo Signature Headers Riêng lẻ

```python
from src_shared_py.signer.mobile_headers import (
    create_mobile_headers_signature,
    get_base_mobile_params
)

# Lấy base parameters
params = get_base_mobile_params()

# Tạo query string
from urllib.parse import urlencode
query_string = urlencode(params)

# Generate signatures
headers = create_mobile_headers_signature(
    query_params=query_string,
    body_payload=None,  # Optional POST body
    cookies=None        # Optional cookies
)

print(headers['X-Gorgon'])
print(headers['X-Ladon'])
print(headers['X-Argus'])
```

### Sử dụng Crypto Modules Riêng

```python
from src_shared_py.crypto.sm3 import SM3
from src_shared_py.crypto.simon import simon_enc, simon_dec

# SM3 Hash
hasher = SM3()
hash_result = hasher.sm3_hash("Hello, World!")
print(hash_result.hex())

# Simon Cipher
key = [0x123456789ABCDEF0, 0xFEDCBA9876543210, 
       0x0123456789ABCDEF, 0xFEDCBA0987654321]
plaintext = [0x1234567890ABCDEF, 0xFEDCBA0987654321]
ciphertext = simon_enc(plaintext, key)
decrypted = simon_dec(ciphertext, key)
```

## Type Definitions

Tất cả types đều được định nghĩa bằng `dataclasses` trong `types.py`:

- `UserInfo`: Thông tin user
- `AwemeItem`: Video/Photo item
- `AwemeListResponse`: Response của video list
- `TiktokVideo`: Video metadata
- `TiktokAwemeItemStats`: Thống kê video
- `GorgonOptions`: Options cho Gorgon signature

## Error Handling

```python
try:
    user = TiktokService.get_user_info("invalid_username")
except Exception as e:
    print(f"Error: {e}")
    # Output: Error: User invalid_username not found
```

## So sánh với TypeScript

| TypeScript | Python |
|------------|--------|
| `interface` | `@dataclass` |
| `Uint8Array` | `bytes` / `bytearray` |
| `BigInt` | `int` (với proper masking) |
| `Buffer` | `bytes` |
| `crypto.randomBytes()` | `os.urandom()` |
| `axios` | `requests` |

## Lưu ý Quan trọng

⚠️ **Signature Accuracy**: Các thuật toán mã hóa (SM3, Simon, Gorgon) phải chính xác 100%. Bất kỳ sai lệch nào cũng sẽ khiến TikTok API từ chối request.

⚠️ **API Changes**: TikTok có thể thay đổi signature requirements bất kỳ lúc nào. Monitor và update thường xuyên.

⚠️ **Rate Limiting**: Sử dụng delays hợp lý giữa các requests để tránh bị rate limit.

## Ví dụ Hoàn chỉnh

Xem file `examples/basic_usage.py` để có ví dụ đầy đủ.

## Dependencies

- `pycryptodome>=3.19.0`: AES encryption, MD5 hashing
- `requests>=2.31.0`: HTTP requests
- `urllib3>=2.0.0`: URL encoding

## License

Tương tự như project gốc.

## Credits

Được chuyển đổi từ TypeScript implementation trong `src/shared`.
