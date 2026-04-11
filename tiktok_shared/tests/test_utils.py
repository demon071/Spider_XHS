"""
Test utilities and formatters
Run with: pytest tests/test_utils.py -v
"""

import pytest
from src_shared_py.utils.tiktok_utils import (
    get_highest_quality_video_uri,
    format_aweme_item_response
)


class TestTiktokUtils:
    """Test TikTok utility functions"""
    
    def test_get_highest_quality_empty(self):
        """Test with empty bit rate array"""
        result = get_highest_quality_video_uri([])
        assert result == ''
    
    def test_get_highest_quality_single(self):
        """Test with single video quality"""
        bit_rate_arr = [{
            'play_addr': {
                'width': 720,
                'height': 1280,
                'url_list': ['https://example.com/video1.mp4']
            }
        }]
        
        result = get_highest_quality_video_uri(bit_rate_arr)
        assert result == 'https://example.com/video1.mp4'
    
    def test_get_highest_quality_multiple(self):
        """Test with multiple video qualities"""
        bit_rate_arr = [
            {
                'play_addr': {
                    'width': 480,
                    'height': 640,
                    'url_list': ['https://example.com/low.mp4']
                }
            },
            {
                'play_addr': {
                    'width': 720,
                    'height': 1280,
                    'url_list': ['https://example.com/mid.mp4']
                }
            },
            {
                'play_addr': {
                    'width': 1080,
                    'height': 1920,
                    'url_list': ['https://example.com/high.mp4']
                }
            }
        ]
        
        result = get_highest_quality_video_uri(bit_rate_arr)
        assert result == 'https://example.com/high.mp4'
    
    def test_format_aweme_video(self):
        """Test formatting video aweme"""
        raw_item = {
            'aweme_id': '123456',
            'share_url': 'https://example.com/video',
            'desc': 'Test video',
            'create_time': 1234567890,
            'statistics': {
                'digg_count': 100,
                'comment_count': 10,
                'share_count': 5,
                'play_count': 1000,
                'collect_count': 20
            },
            'video': {
                'origin_cover': {
                    'url_list': ['https://example.com/cover.jpg']
                },
                'bit_rate': [{
                    'play_addr': {
                        'width': 720,
                        'height': 1280,
                        'url_list': ['https://example.com/video.mp4']
                    }
                }]
            },
            'music': {
                'play_url': {
                    'url_list': ['https://example.com/music.mp3']
                }
            }
        }
        
        result = format_aweme_item_response(raw_item)
        
        assert result.id == '123456'
        assert result.type == 'VIDEO'
        assert result.description == 'Test video'
        assert result.stats.likes == 100
        assert result.stats.views == 1000
        assert result.video is not None
        assert result.video.mp4_uri == 'https://example.com/video.mp4'
    
    def test_format_aweme_photo(self):
        """Test formatting photo aweme"""
        raw_item = {
            'aweme_id': '789012',
            'share_url': 'https://example.com/photo',
            'desc': 'Test photo',
            'create_time': 1234567890,
            'statistics': {
                'digg_count': 50,
                'comment_count': 5,
                'share_count': 2,
                'play_count': 500,
                'collect_count': 10
            },
            'image_post_info': {
                'images': [
                    {
                        'display_image': {
                            'url_list': ['https://example.com/photo1.jpg']
                        }
                    },
                    {
                        'display_image': {
                            'url_list': ['https://example.com/photo2.jpg']
                        }
                    }
                ]
            },
            'music': {
                'play_url': {
                    'url_list': ['https://example.com/music.mp3']
                }
            }
        }
        
        result = format_aweme_item_response(raw_item)
        
        assert result.id == '789012'
        assert result.type == 'PHOTO'
        assert len(result.images_uri) == 2
        assert result.video is None
        assert 'https://example.com/photo1.jpg' in result.images_uri


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
