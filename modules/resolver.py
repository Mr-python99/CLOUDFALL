#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dns.resolver
import socket

RESOLVERS = [
    '8.8.8.8',
    '1.1.1.1',
    '208.67.222.222',
    '9.9.9.9',
    '8.26.56.26',
]

def resolve_dns(domain, resolver_ip=None):
    try:
        if resolver_ip:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [resolver_ip]
            answers = resolver.resolve(domain, 'A')
            return [str(r) for r in answers]
        else:
            return [socket.gethostbyname(domain)]
    except:
        return []

def resolve_all(domain):
    results = {}
    for resolver in RESOLVERS:
        ips = resolve_dns(domain, resolver)
        if ips:
            results[resolver] = ips
    return results
