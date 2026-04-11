"""
TikTok API Service
Converted from: src/shared/services/tiktok.service.ts

Provides high-level functions to interact with TikTok API.
"""

from typing import Optional
from urllib.parse import urlencode
import requests

from ..constants import TIKTOK_API_URL
from ..types import UserInfo, AwemeListResponse, AwemeItem, AwemeListPagination
from ..signer.mobile_headers import create_mobile_headers_signature, get_base_mobile_params
from ..utils.tiktok_utils import format_aweme_item_response


class TiktokService:
    """TikTok API service for fetching user info and videos"""
    
    @staticmethod
    def get_user_info(username: str) -> UserInfo:
        """
        Get user information by username
        
        Args:
            username: TikTok username (unique_id)
        
        Returns:
            UserInfo object with user details
        
        Raises:
            Exception: If user not found or API error
        """
        try:
            base_params = get_base_mobile_params()
            payload = {
                'keyword': username.lower(),
                'offset': '0',
                'count': '10',
                # 'search_source': 'normal_search',
                'hot_search': '0',
                'query_correct_type': '1',
                'multi_mod': '0',
                'is_filter_search': '0',
                'publish_time': '0',
                'sort_type': '0',
                'backtrace': 'ad_cursor%3D14%3Bcs_next_img_group%3D7%3Bright_side%3D1%3Brs_card_next_index%3D1%3Brs_next_a%3D0%3Brs_next_index%3D1%3Brs_word_next_index%3D5',
                'search_context': '',
            }
            
            query_string = urlencode(base_params)
            signature_headers = create_mobile_headers_signature(
                query_params=query_string
            )
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'user-agent': 'okhttp/3.10.0.1',
            }
            headers['x-ss-stub'] = signature_headers['x-ss-stub']
            headers['x-gorgon'] = signature_headers['X-Gorgon']
            headers["x-khronos"] = signature_headers['X-Khronos']
            
            url = 'https://api-h2.tiktokv.com/aweme/v1/general/search/single/'
            response = requests.post(
                url,
                params=base_params,
                data=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            response_data = response.json()
            
            # Find user in response
            user_list = response_data.get('user_list', [])
            user = None
            def get_data_user(data):
                for d in data['data']:
                    if d['doc_type'] == 180:
                        for u in d['user_list']:
                            if u['user_info']['unique_id'] == username.lower():
                                return u['user_info']
                    if d['doc_type'] == 183:
                        if d['aweme_info']['author']['unique_id'] == username.lower():
                            return d['aweme_info']['author']
                return {}
            user_info = get_data_user(response_data)
            
            if not user_info:
                raise Exception(f'User {username} not found')
            
            return UserInfo(
                uid=user_info['uid'],
                unique_id=user_info['unique_id'],
                sec_uid=user_info['sec_uid'],
                aweme_count=user_info['aweme_count'],
                follower_count=user_info['follower_count'],
                following_count=user_info['following_count'],
                avatar_uri=user_info.get('avatar_larger', {}).get('url_list', [''])[0]
            )
        except requests.RequestException as e:
            raise Exception(f'Failed to fetch user info: {str(e)}')
        except Exception as e:
            raise Exception(f'Error processing user info: {str(e)}')
    
    @staticmethod
    def get_user_aweme_list(
        sec_uid: str,
        max_cursor: str = '0',
        cursor: str = '0',
        cookie: str = ''
    ) -> AwemeListResponse:
        """
        Get user's video list
        
        Args:
            sec_uid: User's secure UID
            max_cursor: Maximum cursor for pagination
            cursor: Current cursor for pagination
            cookie: Optional cookies for authentication
        
        Returns:
            AwemeListResponse with videos and pagination info
        
        Raises:
            Exception: If API error
        """
        try:
            base_params = get_base_mobile_params()
            params = {
                **base_params,
                'source': '0',
                'max_cursor': max_cursor,
                'cursor': cursor,
                'sec_user_id': sec_uid,
                'count': '21',
                'filter_private': '1',
                'lite_flow_schedule': 'new',
                'cdn_cache_is_login': '1',
                'cdn_cache_strategy': 'v0',
                'data_saver_type': '1',
                'data_saver_work': 'false',
                'page_type': '2'
            }
            
            query_string = urlencode(params)
            signature_headers = create_mobile_headers_signature(
                query_params=query_string,
                cookies=cookie
            )
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'x-tt-ttnet-origin-host': 'api22-normal-c-alisg.tiktokv.com',
                'Host': 'aggr22-normal-alisg.tiktokv.com',
                'Cookie': cookie
            }
            
            for k, v in signature_headers.items():
                if v:
                    headers[k] = v
            
            response = requests.get(
                TIKTOK_API_URL['GET_USER_AWEME_LIST'],
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            response_data = response.json()

            
            has_more = response_data.get('has_more', 0) == 1
            aweme_list = response_data.get('aweme_list', [])
            
            pagination = AwemeListPagination(
                cursor=str(response_data.get('min_cursor', '')),
                max_cursor=str(response_data.get('max_cursor', '')),
                has_more=has_more
            )
            
            formatted_aweme_list = [
                format_aweme_item_response(item) for item in aweme_list
            ]
            
            return AwemeListResponse(
                aweme_list=formatted_aweme_list,
                pagination=pagination
            )
        except requests.RequestException as e:
            raise Exception(f'Failed to fetch user aweme list: {str(e)}')
        except Exception as e:
            raise Exception(f'Error processing aweme list: {str(e)}')
    
    @staticmethod
    def get_aweme_details(aweme_id: str, cookie: str = '') -> AwemeItem:
        """
        Get detailed information about a specific video
        
        Args:
            aweme_id: Video ID
            cookie: Optional cookies for authentication
        
        Returns:
            AwemeItem with video details
        
        Raises:
            Exception: If API error
        """
        try:
            base_params = get_base_mobile_params(use_static_device=True)
            params = {
                **base_params,
                'aweme_id': aweme_id,
                'origin_type': 'web',
                'request_source': '0',
                # E-commerce related
                'ecom_version': '350900',
                'ecomAppVersion': '35.9.0',
                'ecom_version_code': '350900',
                'ecom_version_name': '35.9.0',
                'ecom_appid': '614896',
                'ecom_build_number': '1.0.10-alpha.67.2-bugfix',
                'ecom_commit_id': '4abc9b292',
                'ecom_aar_version': '1.0.10-alpha.67.2-bugfix'
            }
            
            query_string = urlencode(params)
            signature_headers = create_mobile_headers_signature(
                query_params=query_string,
                cookies=cookie
            )
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'x-tt-ttnet-origin-host': 'api22-normal-c-alisg.tiktokv.com',
                'User-Agent': 'axios/1.7.9'
            }
            
            for k, v in signature_headers.items():
                if v:
                    headers[k] = v
            
            response = requests.get(
                TIKTOK_API_URL['GET_AWEME_DETAIL'],
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            response_data = response.json()
            
            aweme_detail = response_data.get('aweme_detail', {})
            return format_aweme_item_response(aweme_detail)
        except requests.RequestException as e:
            raise Exception(f'Failed to fetch aweme details: {str(e)}')
        except Exception as e:
            raise Exception(f'Error processing aweme details: {str(e)}')
