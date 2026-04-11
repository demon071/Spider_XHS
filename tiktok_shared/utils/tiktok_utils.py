"""
TikTok Utility Functions
Converted from: src/shared/utils/tiktok.util.ts

Utility functions for formatting TikTok API responses.
"""

from typing import Dict, Any, List
from ..types import (
    AwemeItem,
    TiktokAwemeItemStats,
    TiktokVideo
)


def get_highest_quality_video_uri(bit_rate_arr: List[Dict[str, Any]]) -> str:
    """
    Get highest quality video URI from bit rate array
    
    Args:
        bit_rate_arr: Array of video quality options
    
    Returns:
        URL of highest quality video
    """
    if not bit_rate_arr or len(bit_rate_arr) == 0:
        return ''
    
    highest_quality_video = None
    max_resolution = 0
    
    for item in bit_rate_arr:
        play_addr = item.get('play_addr', {})
        width = play_addr.get('width', 0)
        height = play_addr.get('height', 0)
        resolution = width * height
        
        if resolution > max_resolution:
            max_resolution = resolution
            highest_quality_video = item
    
    if not highest_quality_video:
        return ''
    
    url_list = highest_quality_video.get('play_addr', {}).get('url_list', [])
    return url_list[-1] if url_list else ''


def format_aweme_item_response(item: Dict[str, Any]) -> AwemeItem:
    """
    Format raw TikTok API response to AwemeItem
    
    Args:
        item: Raw API response dictionary
    
    Returns:
        Formatted AwemeItem object
    """
    aweme_id = item.get('aweme_id', '')
    url = item.get('share_url', '')
    description = item.get('desc', '')
    created_at = item.get('create_time', 0)
    
    # Determine type
    item_type = 'PHOTO' if item.get('image_post_info') else 'VIDEO'
    
    # Statistics
    statistics = item.get('statistics', {})
    stats = TiktokAwemeItemStats(
        likes=statistics.get('digg_count', 0),
        comments=statistics.get('comment_count', 0),
        shares=statistics.get('share_count', 0),
        views=statistics.get('play_count', 0),
        collects=statistics.get('collect_count', 0)
    )
    
    # Images (for photo posts)
    images_uri = []
    if item_type == 'PHOTO':
        image_post_info = item.get('image_post_info', {})
        images = image_post_info.get('images', [])
        images_uri = [
            img.get('display_image', {}).get('url_list', [''])[0]
            for img in images
        ]
    
    # Music
    music = item.get('music', {})
    music_uri = music.get('play_url', {}).get('url_list', [''])[0] if music else ''
    
    # Video (for video posts)
    video = None
    if item_type == 'VIDEO':
        video_data = item.get('video', {})
        cover_uri = video_data.get('origin_cover', {}).get('url_list', [''])[0]
        mp4_uri = get_highest_quality_video_uri(video_data.get('bit_rate', []))
        video = TiktokVideo(cover_uri=cover_uri, mp4_uri=mp4_uri)
    
    return AwemeItem(
        id=aweme_id,
        url=url,
        description=description,
        created_at=created_at,
        type=item_type,
        stats=stats,
        video=video,
        images_uri=images_uri,
        music_uri=music_uri
    )
