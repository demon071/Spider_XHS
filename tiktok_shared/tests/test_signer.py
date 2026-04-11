"""
Unit tests for signature generators
Run with: pytest tests/test_signer.py -v
"""

import pytest
import time
from src_shared_py.signer.gorgon import Gorgon
from src_shared_py.signer.ladon import Ladon
from src_shared_py.signer.argus import Argus
from src_shared_py.signer.mobile_headers import (
    create_mobile_headers_signature,
    get_base_mobile_params
)


class TestGorgon:
    """Test Gorgon signature generator"""
    
    def test_gorgon_basic(self):
        """Test basic Gorgon signature generation"""
        params = "device_id=123&iid=456"
        unix_time = int(time.time())
        
        gorgon = Gorgon(params, unix_time)
        result = gorgon.get_value()
        
        assert 'X-Gorgon' in result
        assert 'X-Khronos' in result
        assert 'x-ss-req-ticket' in result
        assert result['X-Gorgon'].startswith('0404b0d30000')
        assert result['X-Khronos'] == str(unix_time)
    
    def test_gorgon_with_body(self):
        """Test Gorgon with body payload"""
        params = "device_id=123"
        unix_time = int(time.time())
        body = '{"key":"value"}'
        
        gorgon = Gorgon(params, unix_time, body_payload=body)
        result = gorgon.get_value()
        
        assert 'X-Gorgon' in result
        assert len(result['X-Gorgon']) > 12
    
    def test_gorgon_consistency(self):
        """Test Gorgon produces consistent results"""
        params = "test=123"
        unix_time = 1234567890
        
        gorgon1 = Gorgon(params, unix_time)
        gorgon2 = Gorgon(params, unix_time)
        
        result1 = gorgon1.get_value()
        result2 = gorgon2.get_value()
        
        assert result1['X-Gorgon'] == result2['X-Gorgon']


class TestLadon:
    """Test Ladon encryption"""
    
    def test_ladon_basic(self):
        """Test basic Ladon encryption"""
        unix_time = int(time.time())
        result = Ladon.encrypt(unix_time)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_ladon_with_params(self):
        """Test Ladon with custom parameters"""
        result = Ladon.encrypt(
            khronos=1234567890,
            license_id=1611921764,
            aid=1233
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_ladon_deterministic(self):
        """Test Ladon with fixed random bytes"""
        rand_bytes = b'\x01\x02\x03\x04'
        
        result1 = Ladon.encrypt(1234567890, rand_bytes_data=rand_bytes)
        result2 = Ladon.encrypt(1234567890, rand_bytes_data=rand_bytes)
        
        assert result1 == result2


class TestArgus:
    """Test Argus signature generator"""
    
    def test_argus_basic(self):
        """Test basic Argus signature"""
        query_params = "device_id=123&version_name=1.0.0&device_type=test"
        result = Argus.get_sign(query_params=query_params)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_argus_with_stub(self):
        """Test Argus with body stub"""
        query_params = "device_id=123&version_name=1.0.0&device_type=test"
        stub = "d41d8cd98f00b204e9800998ecf8427e"  # MD5 of empty string
        
        result = Argus.get_sign(
            query_params=query_params,
            x_ss_stub=stub
        )
        
        assert isinstance(result, str)
    
    def test_argus_bodyhash(self):
        """Test Argus body hash generation"""
        stub = "abc123"
        result = Argus.get_bodyhash(stub)
        
        assert isinstance(result, bytes)
        assert len(result) == 6  # First 6 bytes of SM3 hash
    
    def test_argus_queryhash(self):
        """Test Argus query hash generation"""
        query = "test=123"
        result = Argus.get_queryhash(query)
        
        assert isinstance(result, bytes)
        assert len(result) == 6


class TestMobileHeaders:
    """Test mobile headers signature generator"""
    
    def test_get_base_params(self):
        """Test get base mobile parameters"""
        params = get_base_mobile_params()
        
        assert 'device_id' in params
        assert 'iid' in params
        assert 'version_name' in params
        assert 'device_type' in params
        assert params['aid'] == 1340
    
    def test_create_headers_basic(self):
        """Test create mobile headers"""
        query_params = "device_id=123&iid=456"
        headers = create_mobile_headers_signature(query_params)
        
        assert 'X-Gorgon' in headers
        assert 'X-Khronos' in headers
        assert 'X-Ladon' in headers
        assert 'X-Argus' in headers
        assert 'x-ss-req-ticket' in headers
    
    def test_create_headers_with_body(self):
        """Test create headers with body payload"""
        query_params = "device_id=123"
        body = '{"test":"data"}'
        
        headers = create_mobile_headers_signature(
            query_params,
            body_payload=body
        )
        
        assert 'x-ss-stub' in headers
        assert headers['x-ss-stub'] is not None
    
    def test_create_headers_with_cookies(self):
        """Test create headers with cookies"""
        query_params = "device_id=123"
        cookies = "sessionid=abc; tt_webid=123"
        
        headers = create_mobile_headers_signature(
            query_params,
            cookies=cookies
        )
        
        assert 'X-Gorgon' in headers
        assert 'X-Ladon' in headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
