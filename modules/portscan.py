#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
# ============================================================
# DATABASE PORT STANDAR (RESMI & PUNYA NAMA)
# ============================================================
PORTS = {
    # ===== WEB SERVERS =====
    80: "HTTP",
    443: "HTTPS",
    8080: "HTTP Alt",
    8443: "HTTPS Alt",
    8000: "Dev Server",
    8888: "Dev Server",
    3000: "Dev Server",
    5000: "Flask",
    7000: "Dev Server",
    9000: "Dev Server",
    
    # ===== CONTROL PANEL =====
    2082: "cPanel HTTP",
    2083: "cPanel HTTPS",
    2086: "WHM HTTP",
    2087: "WHM HTTPS",
    10000: "Webmin",
    8880: "Plesk HTTP",
    2222: "DirectAdmin",
    
    # ===== DATABASE =====
    3306: "MySQL",
    3307: "MySQL Alt",
    5432: "PostgreSQL",
    5433: "PostgreSQL Alt",
    1433: "MSSQL",
    1434: "MSSQL Browser",
    1521: "Oracle DB",
    1522: "Oracle Alt",
    6379: "Redis",
    6380: "Redis SSL",
    27017: "MongoDB",
    27018: "MongoDB Alt",
    27019: "MongoDB Config",
    9200: "Elasticsearch",
    9300: "Elasticsearch Node",
    5601: "Kibana",
    2483: "Oracle SSL",
    2484: "Oracle SSL",
    2638: "Sybase",
    3050: "GDS DB",
    3300: "Debian APT",
    4333: "Mini SQL",
    5022: "MSSQL",
    
    # ===== EMAIL =====
    25: "SMTP",
    110: "POP3",
    143: "IMAP",
    465: "SMTPS",
    587: "SMTP Submission",
    993: "IMAPS",
    995: "POP3S",
    2525: "SMTP Alt",
    4190: "Sieve",
    3660: "SMTP",
    3661: "SMTP",
    3662: "SMTP",
    3663: "SMTP",
    3664: "SMTP",
    3665: "SMTP",
    3666: "SMTP",
    3667: "SMTP",
    3668: "SMTP",
    3669: "SMTP",
    3670: "SMTP",
    3671: "SMTP",
    
    # ===== REMOTE ACCESS =====
    22: "SSH",
    2222: "SSH Alt",
    23: "Telnet",
    3389: "RDP",
    3390: "RDP Alt",
    5900: "VNC",
    5901: "VNC Alt",
    4200: "VNC",
    4242: "VNC",
    4899: "Radmin",
    4900: "Radmin",
    5120: "Barracuda",
    5405: "NetSupport",
    5421: "NetSupport",
    
    # ===== FILE TRANSFER =====
    21: "FTP",
    20: "FTP Data",
    989: "FTPS Data",
    990: "FTPS Control",
    69: "TFTP",
    445: "SMB",
    139: "NetBIOS",
    873: "Rsync",
    
    # ===== DNS =====
    53: "DNS",
    853: "DNS over TLS",
    5353: "mDNS",
    5355: "LLMNR",
    
    # ===== CLOUD & CDN =====
    2052: "Cloudflare HTTP",
    2053: "Cloudflare HTTPS",
    2096: "Cloudflare Alt",
    
    # ===== CONTAINER =====
    2375: "Docker",
    2376: "Docker SSL",
    6443: "Kubernetes",
    10250: "Kubelet",
    10255: "Kubelet Readonly",
    
    # ===== MONITORING =====
    9090: "Prometheus",
    9093: "Alertmanager",
    3100: "Loki",
    514: "Syslog",
    1984: "Big Brother",
    4949: "Munin",
    4950: "Munin",
    601: "Syslog",
    
    # ===== MESSAGING & QUEUE =====
    5672: "RabbitMQ",
    5671: "RabbitMQ SSL",
    61613: "ActiveMQ",
    61616: "ActiveMQ Alt",
    9092: "Kafka",
    2181: "Zookeeper",
    1883: "MQTT",
    8883: "MQTT SSL",
    
    # ===== AUTHENTICATION =====
    389: "LDAP",
    636: "LDAPS",
    3268: "Active Directory",
    3269: "AD SSL",
    464: "Kerberos",
    749: "Kerberos Admin",
    88: "Kerberos",
    
    # ===== PROXY =====
    3128: "Squid Proxy",
    1080: "SOCKS Proxy",
    
    # ===== VERSION CONTROL =====
    9418: "Git",
    3690: "SVN",
    2401: "CVS",
    
    # ===== VPN =====
    1194: "OpenVPN",
    51820: "WireGuard",
    500: "IPSec",
    4500: "IPSec NAT",
    1701: "L2TP",
    1723: "PPTP",
    
    # ===== VOIP =====
    5060: "SIP",
    5061: "SIP SSL",
    1719: "H.323",
    1720: "H.323",
    4569: "IAX",
    
    # ===== GAMING =====
    25565: "Minecraft",
    27015: "CS:GO",
    27016: "Steam",
    3074: "Xbox Live",
    1214: "Kazaa",
    4662: "eDonkey",
    
    # ===== IOT & SMART =====
    5683: "CoAP",
    4840: "OPC UA TCP",
    4843: "OPC UA HTTPS",
    502: "Modbus",
    623: "IPMI",
    860: "iSCSI",
    3260: "iSCSI",
    
    # ===== ENTERPRISE =====
    8005: "Tomcat Shutdown",
    8009: "Tomcat AJP",
    9043: "WebSphere",
    9060: "WebSphere Admin",
    9080: "WebSphere HTTP",
    9443: "WebSphere HTTPS",
    1001: "WebLogic",
    1110: "WebLogic",
    1414: "IBM MQ",
    1352: "Lotus Notes",
    
    # ===== ROUTING & NETWORK =====
    179: "BGP",
    520: "RIP",
    521: "RIPng",
    1985: "Cisco HSRP",
    1998: "Cisco X25",
    2000: "Cisco",
    
    # ===== OTHERS =====
    123: "NTP",
    161: "SNMP",
    162: "SNMP Trap",
    554: "RTSP",
    1935: "RTMP",
    3478: "STUN",
    3544: "Teredo",
    3702: "WS-Discovery",
    5222: "XMPP",
    5269: "XMPP Server",
    5280: "XMPP",
    666: "DOOM",
    1337: "Leet",
    4040: "Metasploit",
    4444: "Meterpreter",
}

def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            return port, PORTS.get(port, "Unknown")
        return None
    except:
        return None

def port_scan(ip, max_workers=100):
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_port, ip, port): port for port in PORTS.keys()}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                port, service = result
                open_ports.append(f"{port} ({service})")
    
    return open_ports
