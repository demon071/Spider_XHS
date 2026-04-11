"""
Type definitions for TikTok API
Converted from: src/shared/types/ and src/shared/interfaces/
"""

from dataclasses import dataclass, field
from typing import Optional, List, Literal


@dataclass
class GorgonOptions:
    """Options for Gorgon signature generation"""
    params: str
    unix: int
    body_payload: Optional[str] = None
    cookies: Optional[str] = None


@dataclass
class GetAwemeListCursor:
    """Pagination cursor for aweme list"""
    cursor: str
    max_cursor: str


@dataclass
class TiktokVideo:
    """TikTok video information"""
    cover_uri: str
    mp4_uri: str


@dataclass
class TiktokAwemeItemStats:
    """Statistics for a TikTok aweme item"""
    likes: int
    comments: int
    shares: int
    views: int
    collects: int


@dataclass
class AwemeItem:
    """TikTok aweme (video/photo) item"""
    id: str
    url: str
    description: str
    created_at: int
    type: Literal["PHOTO", "VIDEO"]
    stats: TiktokAwemeItemStats
    video: Optional[TiktokVideo] = None
    images_uri: List[str] = field(default_factory=list)
    music_uri: Optional[str] = None


@dataclass
class AwemeListPagination(GetAwemeListCursor):
    """Pagination info for aweme list"""
    has_more: bool


@dataclass
class AwemeListResponse:
    """Response for getting aweme list"""
    aweme_list: List[AwemeItem]
    pagination: AwemeListPagination


@dataclass
class UserInfo:
    """TikTok user information"""
    uid: str
    unique_id: str
    sec_uid: str
    aweme_count: int
    follower_count: int
    following_count: int
    avatar_uri: str


@dataclass
class TiktokCredentials:
    """TikTok credentials"""
    cookie: str
