#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from rich.console import Console

console = Console()
session = requests.Session()
session.verify = False
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

def smart_verify(ip, domain):
    """Verifikasi IP dengan metode cerdas"""
    results = []
    
    # 1. Coba akses langsung
    try:
        r = session.get(f"http://{ip}", timeout=5)
        if r.status_code == 200 and domain in r.text.lower():
            return "VALID", "Direct", r.status_code
        elif r.status_code == 302 or r.status_code == 301:
            # Redirect detected
            location = r.headers.get('Location', '')
            results.append(("Redirect", r.status_code, location))
    except:
        pass
    
    # 2. Coba dengan Host header
    try:
        r = session.get(f"http://{ip}", timeout=5, headers={'Host': domain})
        if r.status_code == 200 and domain in r.text.lower():
            return "VALID", "Host Header", r.status_code
        elif r.status_code in [301, 302]:
            location = r.headers.get('Location', '')
            results.append(("Redirect with Host", r.status_code, location))
    except:
        pass
    
    # 3. Coba HTTPS dengan Host header
    try:
        r = session.get(f"https://{ip}", timeout=5, headers={'Host': domain}, verify=False)
        if r.status_code == 200 and domain in r.text.lower():
            return "VALID", "HTTPS + Host Header", r.status_code
        elif r.status_code in [301, 302]:
            location = r.headers.get('Location', '')
            results.append(("HTTPS Redirect", r.status_code, location))
    except:
        pass
    
    # 4. Coba pakai domain langsung (fallback)
    try:
        r = session.get(f"http://{domain}", timeout=5)
        if r.status_code == 200:
            return "VALID (via domain)", "Domain", r.status_code
    except:
        pass
    
    # 5. Jika redirect, coba ikuti
    for method, status, location in results:
        if location:
            try:
                r = session.get(location, timeout=5)
                if domain in r.text.lower():
                    return "VALID (Redirected)", f"{method} → {location}", status
            except:
                pass
    
    return "INVALID", "None", None
