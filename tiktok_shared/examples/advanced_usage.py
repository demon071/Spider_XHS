"""
Advanced Usage Examples for TikTok Shared Library

Demonstrates:
1. Custom signature generation
2. Using crypto modules directly
3. Error handling
4. Working with cookies
"""

from src_shared_py.signer.mobile_headers import (
    create_mobile_headers_signature,
    get_base_mobile_params
)
from src_shared_py.crypto.sm3 import SM3
from src_shared_py.crypto.simon import simon_enc, simon_dec
from src_shared_py.crypto.buffer_utils import bytes_to_hex
from src_shared_py.services.tiktok_service import TiktokService
from urllib.parse import urlencode


def example_custom_signatures():
    """Example 1: Generate custom API signatures"""
    print("=" * 70)
    print("Example 1: Custom Signature Generation")
    print("=" * 70)
    
    # Get base parameters
    params = get_base_mobile_params()
    params.update({
        'count': '20',
        'cursor': '0'
    })
    
    # Create query string
    query_string = urlencode(params)
    print(f"\nQuery String (first 100 chars): {query_string[:100]}...")
    
    # Generate signatures
    headers = create_mobile_headers_signature(
        query_params=query_string,
        body_payload=None,
        cookies=None
    )
    
    print("\n✅ Generated Headers:")
    for key, value in headers.items():
        if value:
            display_value = value[:50] + "..." if len(str(value)) > 50 else value
            print(f"  {key}: {display_value}")


def example_crypto_modules():
    """Example 2: Using crypto modules directly"""
    print("\n" + "=" * 70)
    print("Example 2: Cryptographic Operations")
    print("=" * 70)
    
    # SM3 Hash
    print("\nSM3 Hash:")
    sm3 = SM3()
    test_data = "Hello, TikTok!"
    hash_result = sm3.sm3_hash(test_data)
    print(f"  Input: {test_data}")
    print(f"  SM3 Hash: {bytes_to_hex(hash_result)}")
    print(f"  Length: {len(hash_result)} bytes")
    
    # Simon Cipher
    print("\nSimon Cipher Encryption/Decryption:")
    key = [
        0x123456789ABCDEF0, 0xFEDCBA9876543210,
        0x0123456789ABCDEF, 0xFEDCBA0987654321
    ]
    plaintext = [0x1234567890ABCDEF, 0xFEDCBA0987654321]
    
    print(f"  Plaintext: {[hex(x) for x in plaintext]}")
    
    ciphertext = simon_enc(plaintext, key)
    print(f"  Ciphertext: {[hex(x) for x in ciphertext]}")
    
    decrypted = simon_dec(ciphertext, key)
    print(f"  Decrypted: {[hex(x) for x in decrypted]}")
    print(f"  ✅ Match: {plaintext == decrypted}")


def example_error_handling():
    """Example 3: Proper error handling"""
    print("\n" + "=" * 70)
    print("Example 3: Error Handling")
    print("=" * 70)
    
    # Test 1: Invalid username
    print("\nTest 1: Invalid username")
    try:
        user = TiktokService.get_user_info("this_user_definitely_does_not_exist_12345")
        print(f"  User found: {user.unique_id}")
    except Exception as e:
        print(f"  ❌ Expected error caught: {str(e)[:80]}...")
    
    # Test 2: Invalid video ID
    print("\nTest 2: Invalid video ID")
    try:
        video = TiktokService.get_aweme_details("invalid_id_123")
        print(f"  Video found: {video.id}")
    except Exception as e:
        print(f"  ❌ Expected error caught: {str(e)[:80]}...")
    
    # Test 3: Network timeout handling
    print("\nTest 3: Always use try-except for API calls")
    print("  ✅ Recommended pattern:")
    print("""
    try:
        user = TiktokService.get_user_info(username)
        # Process user data
    except Exception as e:
        logger.error(f"Failed to fetch user: {e}")
        # Handle error gracefully
    """)


def example_with_cookies():
    """Example 4: Using cookies for authentication"""
    print("\n" + "=" * 70)
    print("Example 4: Working with Cookies")
    print("=" * 70)
    
    # Note: Replace with actual cookies for private accounts
    cookies = "sessionid=your_session_id; tt_webid=your_webid; ..."
    
    print("\nCookies are used for:")
    print("  1. Accessing private accounts")
    print("  2. Getting higher rate limits")
    print("  3. Accessing age-restricted content")
    print("  4. Better API responses")
    
    print("\nExample usage:")
    print("""
    # Get cookies from browser or login
    cookies = "sessionid=xxx; tt_webid=yyy; ..."
    
    # Use with API calls
    videos = TiktokService.get_user_aweme_list(
        sec_uid=user.sec_uid,
        cookie=cookies
    )
    
    video_detail = TiktokService.get_aweme_details(
        aweme_id=video_id,
        cookie=cookies
    )
    """)
    
    print("\n⚠️  Security Warning:")
    print("  - Never commit cookies to git")
    print("  - Store cookies securely")
    print("  - Rotate cookies regularly")


def example_batch_processing():
    """Example 5: Batch processing users"""
    print("\n" + "=" * 70)
    print("Example 5: Batch Processing Multiple Users")
    print("=" * 70)
    
    usernames = ["tiktok", "tiktoknews", "tiktokfashion"]
    
    print(f"\nProcessing {len(usernames)} users...")
    
    results = []
    for username in usernames:
        try:
            print(f"\n  Processing: {username}")
            user = TiktokService.get_user_info(username)
            results.append({
                'username': username,
                'success': True,
                'data': user
            })
            print(f"    ✅ Success: {user.follower_count:,} followers")
        except Exception as e:
            results.append({
                'username': username,
                'success': False,
                'error': str(e)
            })
            print(f"    ❌ Failed: {str(e)[:50]}...")
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"\n📊 Summary:")
    print(f"  - Total: {len(results)}")
    print(f"  - Successful: {successful}")
    print(f"  - Failed: {len(results) - successful}")


def main():
    """Run all advanced examples"""
    example_custom_signatures()
    example_crypto_modules()
    example_error_handling()
    example_with_cookies()
    example_batch_processing()
    
    print("\n" + "=" * 70)
    print("✅ All Advanced Examples Completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
