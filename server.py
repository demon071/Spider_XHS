# encoding: utf-8
"""
XHS Request Params Server
Nhận cookies_str, api, data, method → trả về headers và data đã ký.
Tương đương gọi trực tiếp:
    headers, data = generate_headers(a1, api, data, method)   # xhs_util.py L93
"""
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from xhs_utils.xhs_util import generate_request_params

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="XHS Request Params API",
    description=(
        "Truyền vào `cookies_str`, `api`, `data`, `method` "
        "→ nhận lại `headers` và `data` đã ký (x-s, x-t, x-s-common…) "
        "để tự gọi XHS API."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response schema
# ---------------------------------------------------------------------------
class GenerateParamsRequest(BaseModel):
    cookies_str: str  # Cookie string đầy đủ của bạn
    api: str          # Đường dẫn API, ví dụ: /api/sns/web/v1/user/otherinfo?target_user_id=xxx
    data: Any = ""    # Body data (dict hoặc chuỗi rỗng). Mặc định rỗng (cho GET)
    method: str = "POST"  # POST hoặc GET


# ---------------------------------------------------------------------------
# Endpoint duy nhất
# ---------------------------------------------------------------------------
@app.post(
    "/generate_params",
    summary="Tạo headers + data đã ký cho XHS",
    response_description="headers và data đã được ký bằng x-s/x-t/x-s-common",
)
def generate_params(req: GenerateParamsRequest):
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
        # Thường xảy ra khi cookies_str thiếu trường a1
        raise HTTPException(
            status_code=400,
            detail=f"Lỗi cookies_str: thiếu trường {e}. Hãy kiểm tra lại cookie string.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "XHS Request Params API is running"}


# ---------------------------------------------------------------------------
# Entry point (chạy trực tiếp không qua Docker)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=False)
