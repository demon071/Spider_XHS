"""
Test Python với CHÍNH XÁC parameters từ JS successful request
"""

import sys
from pathlib import Path

current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

import requests
import httpx
import json


def test_with_exact_js_params():
    """Test với CHÍNH XÁC params, query string và headers như JS"""
    
    print("=" * 70)
    print("PYTHON TEST - Using EXACT JS Parameters")
    print("=" * 70)
    
    # EXACT parameters từ JS output (FRESH - video 7588829083551665428)
    aweme_id = "7588829083551665428"
    
    # EXACT query string từ JS (994 chars) - FRESH
    query_string = "_rticket=1767157937798&device_id=7555746395380368897&ts=1767157937&iid=7580036180676593416&openudid=8104ec073a3062e0&cdid=c81f923f-aec3-44d1-b342-eaaccc2b7cf7&manifest_version_code=410405&app_language=en&app_type=normal&app_package=com.zhiliaoapp.musically.go&channel=googleplay&device_type=SM-G998B&language=en&host_abi=x86_64&locale=en&resolution=900%2A1600&update_version_code=410405&ac2=wifi&sys_region=US&os_api=28&timezone_name=Asia%2FSaigon&dpi=240&carrier_region=VN&ac=wifi&os=android&os_version=9&timezone_offset=25200&version_code=410405&app_name=musically_go&ab_version=41.4.5&version_name=41.4.5&device_brand=samsung&op_region=VN&ssmix=a&device_platform=android&build_number=41.4.5&region=US&aid=1340&aweme_id=7588829083551665428&origin_type=web&request_source=0&ecom_version=350900&ecomAppVersion=35.9.0&ecom_version_code=350900&ecom_version_name=35.9.0&ecom_appid=614896&ecom_build_number=1.0.10-alpha.67.2-bugfix&ecom_commit_id=4abc9b292&ecom_aar_version=1.0.10-alpha.67.2-bugfix"
    
    print(f"\n📌 Testing with aweme_id: {aweme_id}")
    print(f"📝 Query string length: {len(query_string)}")
    
    # EXACT headers từ JS output - FRESH
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        # 'Content-Type': 'application/json',
        'x-tt-ttnet-origin-host': 'api22-normal-c-alisg.tiktokv.com',
        'X-Gorgon': '0404b0d3000031588c75eb57387ccee15dbc3694a6279f2b8883',
        'X-Khronos': '1767157937',
        'x-ss-req-ticket': '1767157937000',
        'X-Ladon': 'v0MAI0TF8j1aSMMk39PJX/hw8FjNfGp/fODqUu904qfsg1VN',
        'X-Argus': '8oHP6+/J0++u4Usca5UIs+QciQ1OkwjZ0tIFwJzFNc1PQiujw0yQqocV2cqVzpKgf/u99w6UdAJEs1XzxcpiFY3HfW/KuhyKz4nwqICBMqIBqMCOEogxqYoJfhmv2Fin4OeHBTGfnMhRUiI5kkS0K5qRd6251OBfypv4FwWVkVbJoj5m7QEUXFJbouES8LEKF4rPzwvnybr5vY7LPWYVoE7inwWf0gDYoGbdsKspmqTNCG93KmVvK2Ju6DQkB2kmZ6YeDhW5dTvl2xmfms8tdpp8/V1wJMdRHsKHutaLej4g/0Gs91Y8FnQkYWUXfMlKMY8=',
        'user-agent': 'axios/1.7.9',
    }
    
    print(f"\n🔐 Headers:")
    for k, v in headers.items():
        print(f"   {k}: {v[:60]}..." if len(v) > 60 else f"   {k}: {v}")
    
    # URL từ JS
    url = "https://aggr22-normal-alisg.tiktokv.com/aweme/v1/aweme/detail/"
    
    # Build full URL với query string (giống JS axios)
    full_url = f"{url}?{query_string}"
    
    print(f"\n📤 Request:")
    print(f"   URL: {url}")
    print(f"   Full URL length: {len(full_url)}")
    print(f"   Method: GET")
    
    print(f"\n⏳ Sending Python request...")
    
    try:
        # Method 1: Full URL (like JS does)
        response = requests.get(
            full_url,
            headers=headers,
        )
        
        print(f"\n✅ Response received!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Try parse JSON
            try:
                data = response.json()
                print(f"\n✅ JSON parsed successfully!")
                print(f"   Response keys: {list(data.keys())}")
                
                if 'aweme_detail' in data:
                    print(f"\n✅✅✅ SUCCESS! aweme_detail found!")
                    aweme = data['aweme_detail']
                    if aweme:
                        print(f"   - aweme_id: {aweme.get('aweme_id', 'N/A')}")
                        print(f"   - desc: {aweme.get('desc', 'N/A')[:50]}...")
                        stats = aweme.get('statistics', {})
                        print(f"   - views: {stats.get('play_count', 0):,}")
                        print(f"   - likes: {stats.get('digg_count', 0):,}")
                    else:
                        print(f"   ⚠️ aweme_detail is empty")
                else:
                    print(f"\n❌ aweme_detail NOT in response")
                    print(f"   Full response: {json.dumps(data, indent=2)[:500]}...")
                    
            except json.JSONDecodeError as e:
                print(f"\n❌ Failed to parse JSON: {e}")
                print(f"   Response text (first 500): {response.text[:500]}")
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_with_exact_js_params()
