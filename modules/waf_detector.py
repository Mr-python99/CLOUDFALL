#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

WAF_SIGNATURES = {
    'Cloudflare WAF': [
        ('Server', 'cloudflare'),
        ('cf-ray', ''),
        ('cf-mitigated', 'challenge')
    ],
    'ModSecurity': [
        ('Server', 'mod_security'),
        ('X-Mod-Security', ''),
        ('Mod-Security', '')
    ],
    'AWS WAF': [
        ('Server', 'awselb'),
        ('x-amzn-RequestId', ''),
        ('x-amzn-ErrorType', '')
    ],
    'Sucuri WAF': [
        ('Server', 'Sucuri'),
        ('X-Sucuri-ID', ''),
        ('X-Sucuri-Cache', '')
    ],
    'Akamai WAF': [
        ('Server', 'AkamaiGHost'),
        ('X-Akamai-Transformed', ''),
        ('X-Akamai-Request-ID', '')
    ],
    'Cloudfront WAF': [
        ('Server', 'CloudFront'),
        ('X-Amz-Cf-Id', ''),
        ('X-Amz-Cf-Pop', '')
    ],
    'Incapsula WAF': [
        ('Server', 'Incapsula'),
        ('X-CDN', 'Incapsula'),
        ('X-Iinfo', '')
    ],
}

def detect_waf(domain):
    """Deteksi WAF dari response header domain"""
    detected = []
    
    try:
        # Coba akses dengan payload sederhana untuk memicu WAF
        r = requests.get(
            f"http://{domain}/?test=' OR 1=1--",
            timeout=5,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        # Cek dari header
        for waf_name, signatures in WAF_SIGNATURES.items():
            for key, value in signatures:
                for header_key, header_value in r.headers.items():
                    if key.lower() in header_key.lower():
                        if not value or value.lower() in str(header_value).lower():
                            detected.append(waf_name)
                            break
        
        # Cek dari status code
        if r.status_code in [403, 406, 429]:
            detected.append("Unknown WAF (blocking based on payload)")
            
    except:
        pass
    
    return list(set(detected))
