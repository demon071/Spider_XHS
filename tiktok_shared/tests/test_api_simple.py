"""
Test API cho TikTok Service
Chạy từ thư mục gốc: python -m src_shared_py.tests.test_api_simple

Hoặc copy file này ra ngoài và chạy: python test_api_simple.py
"""

import sys
from pathlib import Path

# Ensure we can import from src_shared_py
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

import time


def test_api():
    """Test TikTok API với real requests"""
    
    from src_shared_py.services.tiktok_service import TiktokService
    
    print("=" * 70)
    print("  🧪 TEST TIKTOK API")
    print("=" * 70)
    
    # Test 1: Get user info
    print("\n[TEST 1] Getting user info...")
    username = "tiktok"
    user = None
    videos = None
    
    try:
        user = TiktokService.get_user_info(username)
        print(f"✅ Success! Found user: @{user.unique_id}")
        print(f"   - Followers: {user.follower_count:,}")
        print(f"   - Videos: {user.aweme_count:,}")
        print(f"   - Sec UID: {user.sec_uid[:30]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        # return # Don't return, try other tests? No, subsequent tests depend on user
        return
    
    time.sleep(2)  # Rate limit
    
    # Test 2: Get video list
    print("\n[TEST 2] Getting video list...")
    
    try:
        if user:
            videos = TiktokService.get_user_aweme_list(user.sec_uid)
            print(f"✅ Success! Found {len(videos.aweme_list)} videos")
            
            if videos.aweme_list:
                first = videos.aweme_list[0]
                print(f"\n   First video:")
                print(f"   - ID: {first.id}")
                print(f"   - Type: {first.type}")
                print(f"   - Views: {first.stats.views:,}")
                print(f"   - Likes: {first.stats.likes:,}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    time.sleep(2)  # Rate limit
    
    # Test 3: Get video details
    if videos and videos.aweme_list:
        print("\n[TEST 3] Getting video details...")
        
        try:
            video_id = videos.aweme_list[0].id
            detail = TiktokService.get_aweme_details(video_id)
            print(f"✅ Success! Video details retrieved")
            print(f"   - Type: {detail.type}")
            print(f"   - Views: {detail.stats.views:,}")
            print(f"   - Comments: {detail.stats.comments:,}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("  ✅ All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    from src_shared_py.services.tiktok_service import TiktokService
    try:
        video_id = '7588829083551665428'
        detail = TiktokService.get_aweme_details(video_id)
        print(f"✅ Success! Video details retrieved")
        print(f"   - Type: {detail.type}")
        print(f"   - Views: {detail.stats.views:,}")
        print(f"   - Comments: {detail.stats.comments:,}")
    except Exception as e:
        print(f"❌ Error: {e}")
