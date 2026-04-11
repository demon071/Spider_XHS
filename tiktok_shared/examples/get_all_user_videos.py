"""
Example: Get All User Videos (Bulk Downloader Logic)

This script demonstrates how to fetch ALL videos from a TikTok user,
replicating the logic from src/renderer/src/features/BulkDownloader.tsx.

Key Logic:
1. Get User Info -> Get sec_uid
2. Loop through get_user_aweme_list using cursor pagination
3. Collect all video items
"""

import sys
import time
from pathlib import Path

# Ensure we can import from src_shared_py
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from src_shared_py.services.tiktok_service import TiktokService

def get_all_user_videos(username: str, sid_tt: str = ''):
    """
    Fetch all videos for a given username.
    
    Args:
        username: TikTok username (e.g. 'tiktok')
        sid_tt: Optional session ID cookie (required for some users/private content)
    """
    print(f"🔍 Fetching profile for: {username}")
    
    # 1. Get User Info to get sec_uid
    try:
        user_info = TiktokService.get_user_info(username)
        print(f"✅ User found: {user_info.unique_id} (UID: {user_info.uid})")
        print(f"   SecUID: {user_info.sec_uid[:20]}...")
        print(f"   Total Videos (approx): {user_info.aweme_count}")
    except Exception as e:
        print(f"❌ Failed to get user info: {e}")
        return

    # 2. Pagination Loop
    all_videos = []
    current_cursor = '0'
    max_cursor = '0'
    has_more = True
    page_num = 1
    
    # Cookie string format
    cookie = f"sid_tt={sid_tt}" if sid_tt else ""
    
    print("\n📥 Starting video fetch loop...")
    
    while has_more:
        print(f"   PLEASE WAIT... Fetching page {page_num} (max_cursor: {max_cursor})...")
        
        try:
            # Call API
            response = TiktokService.get_user_aweme_list(
                sec_uid=user_info.sec_uid,
                cursor=current_cursor,      # Some APIs use cursor
                max_cursor=max_cursor,      # TikTok mobile API often uses max_cursor for pagination
                cookie=cookie
            )
            
            # Add videos to list
            new_videos = response.aweme_list
            all_videos.extend(new_videos)
            print(f"   ✅ Page {page_num}: Found {len(new_videos)} videos. Total so far: {len(all_videos)}")
            
            # Update pagination cursors
            # Logic from TSX:
            # currentCursor = res.pagination.cursor
            # currentMaxCursor = res.pagination.maxCursor
            # hasMore = res.pagination.hasMore
            
            current_cursor = response.pagination.cursor
            max_cursor = response.pagination.max_cursor
            has_more = response.pagination.has_more
            
            # Safety check: if no new videos and has_more is True, we might be stuck
            if not new_videos and has_more:
                print("   ⚠️ Warning: No videos in this page but has_more is True. Stopping to avoid loop.")
                break
                
            page_num += 1
            
            # Delay to avoid rate limiting (Simulating the 'delay' state in TSX)
            time.sleep(1) 
            
        except Exception as e:
            print(f"   ❌ Error fetching page {page_num}: {e}")
            break
            
    # 3. Summary
    print("\n" + "="*50)
    print(f"🎉 COMPLETED! Fetched {len(all_videos)} videos for {username}")
    print("="*50)
    
    # Optional: Print first few videos
    if all_videos:
        print("First 5 videos:")
        for idx, video in enumerate(all_videos[:5]):
            print(f"{idx+1}. [{video.id}] {video.desc[:50]}... | Views: {video.stats.views}")

if __name__ == "__main__":
    # Change username here to test
    TARGET_USERNAME = "therock" 
    # SID_TT = "your_sid_tt_here" # Optional
    
    get_all_user_videos(TARGET_USERNAME)
