"""
TikTok Shared Library - Python Implementation
Converted from TypeScript src/shared

Main exports for the TikTok API library.
"""

from .constants import IPC_CHANNELS, TIKTOK_API_URL
from .types import (
    GorgonOptions,
    UserInfo,
    AwemeItem,
    AwemeListResponse,
    TiktokVideo,
    TiktokAwemeItemStats,
    GetAwemeListCursor,
)
from .services.tiktok_service import TiktokService
from .signer.mobile_headers import create_mobile_headers_signature, get_base_mobile_params

__version__ = "1.0.0"

__all__ = [
    "IPC_CHANNELS",
    "TIKTOK_API_URL",
    "GorgonOptions",
    "UserInfo",
    "AwemeItem",
    "AwemeListResponse",
    "TiktokVideo",
    "TiktokAwemeItemStats",
    "GetAwemeListCursor",
    "TiktokService",
    "create_mobile_headers_signature",
    "get_base_mobile_params",
]
