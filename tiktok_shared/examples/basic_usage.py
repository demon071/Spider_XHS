"""
Basic Usage Example for TikTok Shared Library

This example demonstrates how to:
1. Get user information
2. Fetch user's video list
3. Handle pagination
4. Get video details
"""

from src_shared_py.services.tiktok_service import TiktokService


def main():
    """Main example function"""
    
    # Example 1: Get user information
    print("=" * 70)
    print("Example 1: Getting User Information")
    print("=" * 70)
    
    try:
        username = "tiktok"  # Replace with actual username
        print(f"Searching for user: {username}")
        
        user = TiktokService.get_user_info(username)
        
        print(f"\n✅ User Found!")
        print(f"  - User ID: {user.uid}")
        print(f"  - Username: {user.unique_id}")
        print(f"  - Sec UID: {user.sec_uid}")
        print(f"  - Followers: {user.follower_count:,}")
        print(f"  - Following: {user.following_count:,}")
        print(f"  - Total Videos: {user.aweme_count:,}")
        print(f"  - Avatar: {user.avatar_uri}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return
    
    # Example 2: Get user's video list
    print("\n" + "=" * 70)
    print("Example 2: Fetching User's Video List")
    print("=" * 70)
    
    try:
        print(f"\nFetching videos for {user.unique_id}...")
        
        videos = TiktokService.get_user_aweme_list(user.sec_uid)
        
        print(f"\n✅ Found {len(videos.aweme_list)} videos")
        print(f"  - Has More: {videos.pagination.has_more}")
        print(f"  - Next Cursor: {videos.pagination.cursor}")
        print(f"  - Max Cursor: {videos.pagination.max_cursor}")
        
        # Display first 5 videos
        print("\nFirst 5 videos:")
        for i, aweme in enumerate(videos.aweme_list[:5], 1):
            print(f"\n  [{i}] Video ID: {aweme.id}")
            print(f"      Type: {aweme.type}")
            print(f"      Description: {aweme.description[:50]}..." if len(aweme.description) > 50 else f"      Description: {aweme.description}")
            print(f"      Views: {aweme.stats.views:,}")
            print(f"      Likes: {aweme.stats.likes:,}")
            print(f"      Comments: {aweme.stats.comments:,}")
            print(f"      Shares: {aweme.stats.shares:,}")
            
            if aweme.type == "VIDEO" and aweme.video:
                print(f"      Video URL: {aweme.video.mp4_uri[:60]}...")
            elif aweme.type == "PHOTO":
                print(f"      Images: {len(aweme.images_uri)} photos")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return
    
    # Example 3: Pagination
    print("\n" + "=" * 70)
    print("Example 3: Pagination (Loading Next Page)")
    print("=" * 70)
    
    if videos.pagination.has_more:
        try:
            print("\nLoading next page...")
            
            page2 = TiktokService.get_user_aweme_list(
                user.sec_uid,
                max_cursor=videos.pagination.max_cursor,
                cursor=videos.pagination.cursor
            )
            
            print(f"\n✅ Loaded page 2: {len(page2.aweme_list)} videos")
            print(f"  - Has More: {page2.pagination.has_more}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("\nℹ️  No more videos to load")
    
    # Example 4: Get video details
    print("\n" + "=" * 70)
    print("Example 4: Getting Video Details")
    print("=" * 70)
    
    if videos.aweme_list:
        try:
            first_video = videos.aweme_list[0]
            print(f"\nFetching details for video: {first_video.id}")
            
            video_detail = TiktokService.get_aweme_details(first_video.id)
            
            print(f"\n✅ Video Details:")
            print(f"  - ID: {video_detail.id}")
            print(f"  - Type: {video_detail.type}")
            print(f"  - Description: {video_detail.description}")
            print(f"  - Created: {video_detail.created_at}")
            print(f"  - URL: {video_detail.url}")
            print(f"\n  Statistics:")
            print(f"    - Views: {video_detail.stats.views:,}")
            print(f"    - Likes: {video_detail.stats.likes:,}")
            print(f"    - Comments: {video_detail.stats.comments:,}")
            print(f"    - Shares: {video_detail.stats.shares:,}")
            print(f"    - Collects: {video_detail.stats.collects:,}")
            
            if video_detail.type == "VIDEO" and video_detail.video:
                print(f"\n  Video Info:")
                print(f"    - Cover: {video_detail.video.cover_uri[:60]}...")
                print(f"    - MP4: {video_detail.video.mp4_uri[:60]}...")
            
            if video_detail.music_uri:
                print(f"\n  Music: {video_detail.music_uri[:60]}...")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ All Examples Completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
