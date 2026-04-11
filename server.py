# encoding: utf-8
"""
XHS + TikTok Request Params Server
- XHS: Nhận cookies_str, api, data, method → trả về headers và data đã ký.
- TikTok: Lấy thông tin user, danh sách video, chi tiết video.
"""
from dataclasses import asdict
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from urllib.parse import urlencode

from xhs_utils.xhs_util import generate_request_params
from tiktok_shared.services.tiktok_service import TiktokService
from tiktok_shared.signer.mobile_headers import create_mobile_headers_signature, get_base_mobile_params

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="XHS + TikTok API",
    description=(
        "**XHS**: Truyền vào `cookies_str`, `api`, `data`, `method` "
        "→ nhận lại `headers` và `data` đã ký (x-s, x-t, x-s-common…).\n\n"
        "**TikTok**: Lấy thông tin user, danh sách video, chi tiết video qua TikTok Mobile API."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================================================
# XHS – Request / Response schema
# ===========================================================================
class GenerateParamsRequest(BaseModel):
    cookies_str: str  # Cookie string đầy đủ của bạn
    api: str          # Đường dẫn API, ví dụ: /api/sns/web/v1/user/otherinfo?target_user_id=xxx
    data: Any = ""    # Body data (dict hoặc chuỗi rỗng). Mặc định rỗng (cho GET)
    method: str = "POST"  # POST hoặc GET


# ===========================================================================
# XHS – Endpoint
# ===========================================================================
@app.post(
    "/xhs/generate_params",
    tags=["XHS"],
    summary="Tạo headers + data đã ký cho XHS",
    response_description="headers và data đã được ký bằng x-s/x-t/x-s-common",
)
def xhs_generate_params(req: GenerateParamsRequest):
    """
    Gọi `generate_request_params(cookies_str, api, data, method)` từ `xhs_util.py`
    và trả về **headers** + **data** (đã được JSON-encode và ký).

    - **cookies_str**: cookie string lấy từ trình duyệt  
    - **api**: path + query string, ví dụ `/api/sns/web/v1/user/otherinfo?target_user_id=abc`  
    - **data**: body dict (với POST) hoặc để trống `""` (với GET)  
    - **method**: `POST` hoặc `GET` (mặc định `POST`)
    """
    try:
        headers, cookies, data = generate_request_params(
            req.cookies_str, req.api, req.data, req.method
        )
        return {
            "success": True,
            "headers": headers,
            "cookies": cookies,
            "data": data,
        }
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Lỗi cookies_str: thiếu trường {e}. Hãy kiểm tra lại cookie string.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================================================================
# TikTok – Request / Response schema
# ===========================================================================
class TiktokUserInfoRequest(BaseModel):
    username: str  # TikTok username (unique_id), ví dụ: "charlidamelio"


class TiktokUserVideosRequest(BaseModel):
    sec_uid: str          # User's secure UID
    max_cursor: str = "0" # Cursor phân trang – max cursor
    cursor: str = "0"     # Cursor phân trang – current
    cookie: str = ""      # Cookie TikTok (tuỳ chọn)


class TiktokVideoDetailRequest(BaseModel):
    aweme_id: str   # ID video TikTok
    cookie: str = ""  # Cookie TikTok (tuỳ chọn)


class TiktokSignHeadersRequest(BaseModel):
    extra_params: dict = {}        # Params bổ sung merge vào base_mobile_params (tuỳ chọn)
    cookie: str = ""               # Cookie TikTok (tuỳ chọn, đặt vào header Cookie + ký)
    body_payload: str = ""         # Body string (POST); để trống nếu là GET
    use_static_device: bool = False  # True: dùng device tĩnh (như get_aweme_details), False: random device


# ===========================================================================
# TikTok – Endpoints
# ===========================================================================
@app.post(
    "/tiktok/sign_headers",
    tags=["TikTok"],
    summary="Tạo signed headers cho TikTok Mobile API",
    response_description="headers đã ký (X-Gorgon, X-Khronos, X-Argus, X-Ladon, ...) + params đã dùng",
)
def tiktok_sign_headers(req: TiktokSignHeadersRequest):
    """
    Tạo bộ headers đã ký cho TikTok Mobile API theo cùng cơ chế
    mà `get_user_aweme_list` / `get_aweme_details` sử dụng nội bộ.

    - **extra_params**: dict các params bổ sung (sẽ merge vào `base_mobile_params`)  
    - **cookie**: cookie string TikTok (tuỳ chọn)  
    - **body_payload**: body string nếu là POST request (tuỳ chọn)

    Trả về:
    - **params**: toàn bộ params đã dùng để ký (base + extra)
    - **query_string**: query string tương ứng
    - **headers**: headers đầy đủ bao gồm X-Gorgon, X-Khronos, X-Argus, X-Ladon, x-ss-stub, ...
    """
    try:
        # Merge base mobile params với extra_params từ request
        base_params = get_base_mobile_params(use_static_device=req.use_static_device)
        params = {**base_params, **req.extra_params}

        # Tạo query string để ký
        query_string = urlencode(params)

        # Tạo chữ ký
        signature_headers = create_mobile_headers_signature(
            query_params=query_string,
            body_payload=req.body_payload if req.body_payload else None,
            cookies=req.cookie if req.cookie else None,
        )

        # Xây headers trả về (giống pattern trong tiktok_service.py)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-tt-ttnet-origin-host": "api22-normal-c-alisg.tiktokv.com",
            "Host": "aggr22-normal-alisg.tiktokv.com",
        }
        if req.cookie:
            headers["Cookie"] = req.cookie
        for k, v in signature_headers.items():
            if v:
                headers[k] = v

        return {
            "success": True,
            "params": params,
            "query_string": query_string,
            "headers": headers,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/tiktok/user_info",
    tags=["TikTok"],
    summary="Lấy thông tin user TikTok theo username",
    response_description="UserInfo: uid, unique_id, sec_uid, follower_count, ...",
)
def tiktok_get_user_info(req: TiktokUserInfoRequest):
    """
    Tìm kiếm user trên TikTok theo `username` (unique_id) và trả về thông tin cơ bản.

    - **username**: unique_id của tài khoản TikTok, ví dụ `charlidamelio`

    Trả về:  
    `uid`, `unique_id`, `sec_uid`, `aweme_count`, `follower_count`, `following_count`, `avatar_uri`
    """
    try:
        user_info = TiktokService.get_user_info(req.username)
        return {"success": True, "data": asdict(user_info)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/tiktok/user_videos",
    tags=["TikTok"],
    summary="Lấy danh sách video của user TikTok",
    response_description="Danh sách AwemeItem + thông tin phân trang",
)
def tiktok_get_user_videos(req: TiktokUserVideosRequest):
    """
    Lấy danh sách video (aweme list) của một user theo `sec_uid`.

    - **sec_uid**: Secure UID của user (lấy từ `/tiktok/user_info`)  
    - **cursor**: Con trỏ trang hiện tại (mặc định `"0"`)  
    - **max_cursor**: Max cursor (mặc định `"0"`)  
    - **cookie**: Cookie TikTok nếu cần xác thực (tuỳ chọn)

    Trả về danh sách video + `pagination` (cursor, max_cursor, has_more).
    """
    try:
        result = TiktokService.get_user_aweme_list(
            sec_uid=req.sec_uid,
            max_cursor=req.max_cursor,
            cursor=req.cursor,
            cookie=req.cookie,
        )
        return {
            "success": True,
            "data": {
                "aweme_list": [asdict(item) for item in result.aweme_list],
                "pagination": asdict(result.pagination),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/tiktok/video_detail",
    tags=["TikTok"],
    summary="Lấy chi tiết một video TikTok theo aweme_id",
    response_description="AwemeItem với đầy đủ thông tin video/ảnh",
)
def tiktok_get_video_detail(req: TiktokVideoDetailRequest):
    """
    Lấy thông tin chi tiết của một video/photo TikTok theo `aweme_id`.

    - **aweme_id**: ID của video/post TikTok  
    - **cookie**: Cookie TikTok nếu cần xác thực (tuỳ chọn)

    Trả về: `id`, `url`, `description`, `type` (VIDEO/PHOTO), `stats`, `video`, `images_uri`, `music_uri`
    """
    try:
        aweme = TiktokService.get_aweme_details(req.aweme_id, req.cookie)
        return {"success": True, "data": asdict(aweme)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================================================================
# Health check
# ===========================================================================
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "XHS + TikTok API is running",
        "endpoints": {
            "xhs": ["/xhs/generate_params"],
            "tiktok": [
                "/tiktok/user_info",
                "/tiktok/user_videos",
                "/tiktok/video_detail",
            ],
        },
    }


# ===========================================================================
# Entry point (chạy trực tiếp không qua Docker)
# ===========================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=False)
