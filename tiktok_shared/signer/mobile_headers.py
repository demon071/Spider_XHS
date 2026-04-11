"""
Mobile Headers Signature Generator
Converted from: src/shared/tiktok-signer/signHeadersMobile.ts

Main module for generating all TikTok Mobile API signature headers.
"""

import time
import uuid
import random
from typing import Dict, Optional
from ..crypto.buffer_utils import bytes_to_hex, random_bytes
from ..crypto.crypto_utils import md5_hex
from .gorgon import Gorgon
from .ladon import Ladon
from .argus import Argus
from .device_id import devicess


def get_base_mobile_params(use_static_device: bool = False) -> Dict[str, any]:
    """
    Get base mobile parameters for TikTok API requests
    
    Returns:
        Dictionary with device info and app parameters
    """
    if use_static_device:
        device = random.choice(devicess)
        device_id = device.get('device_id')
        iid = device.get('iid')
        openudid = device.get('openudid')
        cdid = device.get('cdid', str(uuid.uuid4()))
    else:
        # Generate random device_id and iid (19 digits) to avoid rate limits
        device_id = str(random.randint(10**18, (10**19)-1))
        iid = str(random.randint(10**18, (10**19)-1))
        cdid = str(uuid.uuid4())
        openudid = bytes_to_hex(random_bytes(8))
    
    timestamp = int(time.time())
    
    return {
        '_rticket': int(time.time() * 1000),
        'device_id': device_id,
        'ts': timestamp,
        'iid': iid,
        'openudid': openudid,
        'cdid': cdid,
        'manifest_version_code': 410405,
        'app_language': 'en',
        'app_type': 'normal',
        'app_package': 'com.zhiliaoapp.musically.go',
        'channel': 'googleplay',
        'device_type': 'SM-G998B',
        'language': 'en',
        'host_abi': 'x86_64',
        'locale': 'en',
        'resolution': '900*1600',
        'update_version_code': 410405,
        'ac2': 'wifi',
        'sys_region': 'US',
        'os_api': 28,
        'timezone_name': 'Asia/Saigon',
        'dpi': 240,
        'carrier_region': 'VN',
        'ac': 'wifi',
        'os': 'android',
        'os_version': '9',
        'timezone_offset': 25200,
        'version_code': 410405,
        'app_name': 'musically_go',
        'ab_version': '41.4.5',
        'version_name': '41.4.5',
        'device_brand': 'samsung',
        'op_region': 'VN',
        'ssmix': 'a',
        'device_platform': 'android',
        'build_number': '41.4.5',
        'region': 'US',
        'aid': 1340
    }


def create_mobile_headers_signature(
    query_params: str,
    body_payload: Optional[str] = None,
    cookies: Optional[str] = None
) -> Dict[str, Optional[str]]:
    """
    Create all mobile signature headers for TikTok API
    
    Args:
        query_params: URL query parameters string
        body_payload: Optional POST body
        cookies: Optional cookies string
    
    Returns:
        Dictionary with X-Gorgon, X-Khronos, x-ss-req-ticket, X-Ladon, X-Argus, x-ss-stub
    
    Raises:
        Exception: If signature generation fails
    """
    unix_timestamp = int(time.time())
    aid = 1340
    license_id = 1611921764
    sec_device_id = ''
    sdk_version = 'v05.00.03-ov-android'
    sdk_version_int = 167773760
    platform = 0
    
    try:
        # Generate Gorgon signature
        gorgon_instance = Gorgon(
            params=query_params,
            unix=unix_timestamp,
            body_payload=body_payload,
            cookies=cookies
        )
        gorgon_headers = gorgon_instance.get_value()
        
        # Generate Ladon signature
        x_ladon = Ladon.encrypt(
            khronos=unix_timestamp,
            license_id=license_id,
            aid=aid
        )
        
        # Generate x-ss-stub if body payload exists
        x_ss_stub = None
        if body_payload:
            x_ss_stub = md5_hex(body_payload)
        
        # Generate Argus signature
        x_argus = Argus.get_sign(
            query_params=query_params,
            x_ss_stub=x_ss_stub,
            timestamp=unix_timestamp,
            aid=aid,
            license_id=license_id,
            platform=platform,
            sec_device_id=sec_device_id,
            sdk_version=sdk_version,
            sdk_version_int=sdk_version_int
        )
        
        return {
            'X-Gorgon': gorgon_headers['X-Gorgon'],
            'X-Khronos': gorgon_headers['X-Khronos'],
            'x-ss-req-ticket': gorgon_headers['x-ss-req-ticket'],
            'X-Ladon': x_ladon,
            'X-Argus': x_argus,
            'x-ss-stub': x_ss_stub.upper() if x_ss_stub else None
        }
    except Exception as err:
        raise Exception(f'Failed to create mobile headers signature: {str(err)}')
