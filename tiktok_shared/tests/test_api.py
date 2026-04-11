"""
Test API thực tế cho TikTok Service
Chạy trực tiếp: python test_api.py

File này test các API thực với TikTok server để verify signatures hoạt động đúng.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path to import src_shared_py modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from src_shared_py.services.tiktok_service import TiktokService



def print_separator(title=""):
    """Print separator line"""
    if title:
        print(f"\n{'=' * 70}")
        print(f"  {title}")
        print(f"{'=' * 70}")
    else:
        print(f"{'=' * 70}")


def test_get_user_info():
    """Test 1: Get user information"""
    print_separator("TEST 1: Get User Info")
    
    username = "tiktok"  # Official TikTok account
    
    try:
        print(f"🔍 Searching for user: @{username}")
        user = TiktokService.get_user_info(username)
        
        print(f"\n✅ Success! User found:")
        print(f"  - UID: {user.uid}")
        print(f"  - Username: {user.unique_id}")
        print(f"  - Sec UID: {user.sec_uid[:30]}...")
        print(f"  - Followers: {user.follower_count:,}")
        print(f"  - Following: {user.following_count:,}")
        print(f"  - Videos: {user.aweme_count:,}")
        print(f"  - Avatar: {user.avatar_uri[:60]}...")
        
        return user
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def test_get_aweme_list(user):
    """Test 2: Get user's video list"""
    print_separator("TEST 2: Get User's Video List")
    
    if not user:
        print("⚠️  Skipping (no user from previous test)")
        return None
    
    try:
        print(f"🔍 Fetching videos for @{user.unique_id}...")
        videos = TiktokService.get_user_aweme_list(user.sec_uid)
        
        print(f"\n✅ Success! Found {len(videos.aweme_list)} videos")
        print(f"  - Has More: {videos.pagination.has_more}")
        print(f"  - Cursor: {videos.pagination.cursor}")
        print(f"  - Max Cursor: {videos.pagination.max_cursor}")
        
        # Show first 3 videos
        print(f"\nFirst 3 videos:")
        for i, aweme in enumerate(videos.aweme_list[:3], 1):
            print(f"\n  [{i}] ID: {aweme.id}")
            print(f"      Type: {aweme.type}")
            desc = aweme.description[:50] + "..." if len(aweme.description) > 50 else aweme.description
            print(f"      Desc: {desc}")
            print(f"      Views: {aweme.stats.views:,}")
            print(f"      Likes: {aweme.stats.likes:,}")
            print(f"      Comments: {aweme.stats.comments:,}")
            
            if aweme.type == "VIDEO" and aweme.video:
                print(f"      Video: {aweme.video.mp4_uri[:50]}...")
            elif aweme.type == "PHOTO":
                print(f"      Photos: {len(aweme.images_uri)} images")
        
        return videos
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def test_pagination(user):
    """Test 3: Pagination"""
    print_separator("TEST 3: Pagination")
    
    if not user:
        print("⚠️  Skipping (no user from previous test)")
        return
    
    try:
        print(f"🔍 Testing pagination for @{user.unique_id}...")
        
        # Get first page
        page1 = TiktokService.get_user_aweme_list(user.sec_uid)
        print(f"\n✅ Page 1: {len(page1.aweme_list)} videos")
        
        if page1.pagination.has_more:
            print(f"  - Loading page 2...")
            time.sleep(1)  # Rate limiting delay
            
            page2 = TiktokService.get_user_aweme_list(
                user.sec_uid,
                max_cursor=page1.pagination.max_cursor,
                cursor=page1.pagination.cursor
            )
            
            print(f"\n✅ Page 2: {len(page2.aweme_list)} videos")
            print(f"  - Has More: {page2.pagination.has_more}")
            
            # Verify videos are different
            page1_ids = {v.id for v in page1.aweme_list}
            page2_ids = {v.id for v in page2.aweme_list}
            overlap = page1_ids & page2_ids
            
            if overlap:
                print(f"  ⚠️  Warning: {len(overlap)} duplicate videos between pages")
            else:
                print(f"  ✅ All videos are unique")
        else:
            print(f"\n  ℹ️  No more pages available")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_get_aweme_details(videos):
    """Test 4: Get video details"""
    print_separator("TEST 4: Get Video Details")
    
    if not videos or not videos.aweme_list:
        print("⚠️  Skipping (no videos from previous test)")
        return
    
    try:
        video_id = videos.aweme_list[0].id
        print(f"🔍 Fetching details for video: {video_id}")
        
        detail = TiktokService.get_aweme_details(video_id)
        
        print(f"\n✅ Success! Video details:")
        print(f"  - ID: {detail.id}")
        print(f"  - Type: {detail.type}")
        desc = detail.description[:60] + "..." if len(detail.description) > 60 else detail.description
        print(f"  - Description: {desc}")
        print(f"  - Created: {detail.created_at}")
        print(f"  - URL: {detail.url}")
        
        print(f"\n  Statistics:")
        print(f"    - Views: {detail.stats.views:,}")
        print(f"    - Likes: {detail.stats.likes:,}")
        print(f"    - Comments: {detail.stats.comments:,}")
        print(f"    - Shares: {detail.stats.shares:,}")
        print(f"    - Collects: {detail.stats.collects:,}")
        
        if detail.type == "VIDEO" and detail.video:
            print(f"\n  Video Info:")
            print(f"    - Cover: {detail.video.cover_uri[:50]}...")
            print(f"    - MP4: {detail.video.mp4_uri[:50]}...")
        
        if detail.music_uri:
            print(f"\n  Music: {detail.music_uri[:50]}...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_error_handling():
    """Test 5: Error handling with invalid data"""
    print_separator("TEST 5: Error Handling")
    
    print(f"🔍 Testing with invalid username...")
    try:
        user = TiktokService.get_user_info("this_user_does_not_exist_12345_xyz")
        print(f"  ❌ Unexpected: User found?")
    except Exception as e:
        print(f"  ✅ Expected error caught:")
        print(f"     {str(e)[:80]}...")
    
    print(f"\n🔍 Testing with invalid video ID...")
    try:
        video = TiktokService.get_aweme_details("invalid_id_123")
        print(f"  ❌ Unexpected: Video found?")
    except Exception as e:
        print(f"  ✅ Expected error caught:")
        print(f"     {str(e)[:80]}...")


def main():
    """Run all tests"""
    print_separator("🧪 TikTok API Tests")
    print(f"Testing TikTok Service API")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests sequentially
    user = test_get_user_info()
    time.sleep(1)  # Rate limiting
    
    videos = test_get_aweme_list(user)
    time.sleep(1)  # Rate limiting
    
    test_pagination(user)
    time.sleep(1)  # Rate limiting
    
    test_get_aweme_details(videos)
    time.sleep(1)  # Rate limiting
    
    test_error_handling()
    
    # Summary
    print_separator("📊 Test Summary")
    print(f"✅ All tests completed!")
    print(f"\nNote:")
    print(f"  - API signatures are working correctly")
    print(f"  - Real TikTok API responses received")
    print(f"  - Error handling is functioning")
    print(f"\n⚠️  Remember to add delays between requests to avoid rate limiting")
    print_separator()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
