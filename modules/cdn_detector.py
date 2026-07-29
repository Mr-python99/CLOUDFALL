#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

CDN_SIGNATURES = {
    'Cloudflare': [
        ('Server', 'cloudflare'),
        ('cf-ray', ''),
    ],
    'Akamai': [
        ('Server', 'AkamaiGHost'),
        ('X-Akamai-Transformed', ''),
        ('X-Akamai-Request-ID', ''),
    ],
    'Fastly': [
        ('Server', 'Fastly'),
        ('X-Served-By', 'cache'),
        ('X-Cache', ''),
    ],
    'Incapsula': [
        ('Server', 'Incapsula'),
        ('X-CDN', 'Incapsula'),
    ],
    'Cloudfront': [
        ('Server', 'CloudFront'),
        ('X-Amz-Cf-Id', ''),
        ('X-Amz-Cf-Pop', ''),
    ],
    'Sucuri': [
        ('Server', 'Sucuri'),
        ('X-Sucuri-ID', ''),
    ],
    'AWS ELB': [
        ('Server', 'awselb'),
        ('X-Amzn-RequestId', ''),
    ],
}

def detect_cdn(domain):
    """Deteksi CDN dari response header domain"""
    detected = []
    
    try:
        r = requests.get(f"http://{domain}", timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        
        for cdn_name, signatures in CDN_SIGNATURES.items():
            for key, value in signatures:
                for header_key, header_value in r.headers.items():
                    if key.lower() in header_key.lower():
                        if not value or value.lower() in str(header_value).lower():
                            detected.append(cdn_name)
                            break
    except:
        pass
    
    return list(set(detected))

def cdn_check(domain):
    """Fungsi utama untuk cek CDN dan tampilkan hasil"""
    detected = detect_cdn(domain)
    
    if detected:
        return True, detected
    else:
        return False, []
