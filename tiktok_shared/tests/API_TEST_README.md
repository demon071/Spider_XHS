# API Test - TikTok Service

## File Test Đã Tạo

### `test_api_simple.py`
File test đơn giản để verify API hoạt động với TikTok server thực.

## Cách Chạy

Từ thư mục gốc project:
```bash
python -m src_shared_py.tests.test_api_simple
```

## Những gì được Test

✅ **Test 1: Get User Info**
- Tìm kiếm user bằng username
- Verify response có đầy đủ thông tin
- Check followers, videos count

✅ **Test 2: Get Video List**  
- Lấy danh sách video của user
- Verify có video trong response
- Check stats (views, likes)

✅ **Test 3: Get Video Details**
- Lấy chi tiết của 1 video cụ thể
- Verify response có đầy đủ thông tin

## Kết Quả Test

Nếu test thành công, bạn sẽ thấy:
```
======================================================================
  🧪 TEST TIKTOK API
======================================================================

[TEST 1] Getting user info...
✅ Success! Found user: @tiktok
   - Followers: xxx,xxx
   - Videos: xxx
   - Sec UID: xxxxxxxxx...

[TEST 2] Getting video list...
✅ Success! Found 21 videos
   First video:
   - ID: xxxxxxxxx
   - Type: VIDEO
   - Views: xxx,xxx
   - Likes: xxx,xxx

[TEST 3] Getting video details...
✅ Success! Video details retrieved
   - Type: VIDEO
   - Views: xxx,xxx
   - Comments: xxx,xxx

======================================================================
  ✅ All tests completed!
======================================================================
```

## Lưu Ý

⚠️ **Rate Limiting**: Test có delay 2 giây giữa các requests để tránh rate limit

⚠️ **Network**: Cần kết nối internet để test với TikTok API thực

⚠️ **Signatures**: Test này verify rằng signatures (Gorgon, Ladon, Argus) đang hoạt động đúng

## Troubleshooting

Nếu gặp lỗi `ModuleNotFoundError`:
1. Chắc chắn đang ở thư mục gốc project
2. Chạy: `python -m src_shared_py.tests.test_api_simple`
3. Không chạy trực tiếp file

Nếu gặp lỗi API:
- Check kết nối internet
- TikTok có thể thay đổi API - cần update signatures
- Có thể bị rate limit - đợi vài phút và thử lại
