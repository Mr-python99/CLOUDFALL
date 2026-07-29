#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import ipaddress

CF_RANGES_URL = "https://www.cloudflare.com/ips-v4"

def get_cf_ranges():
    try:
        r = requests.get(CF_RANGES_URL, timeout=10)
        if r.status_code == 200:
            return [ip.strip() for ip in r.text.splitlines() if ip.strip()]
    except:
        pass
    return []

def is_cf_ip(ip, cf_ranges):
    try:
        ip_obj = ipaddress.ip_address(ip)
        for cidr in cf_ranges:
            if ip_obj in ipaddress.ip_network(cidr, strict=False):
                return True
    except:
        pass
    return False
