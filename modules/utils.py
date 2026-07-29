#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import csv
from datetime import datetime

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def save_results(results, domain):
    os.makedirs('results', exist_ok=True)
    
    json_path = f"results/{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    txt_path = f"results/{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(txt_path, 'w') as f:
        f.write(f"SPECTRA CLOUDFALL KALI EDITION - RESULTS\n")
        f.write(f"Target: {domain}\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"{'='*60}\n\n")
        for r in results:
            if r.get('real_ips'):
                f.write(f"[🔥] {r['subdomain']} → REAL IP: {', '.join(r['real_ips'])}\n")
            elif r.get('cf_protected'):
                f.write(f"[🛡️] {r['subdomain']} → Cloudflare Protected\n")
            else:
                f.write(f"[✗] {r['subdomain']} → No result\n")
    
    return json_path, txt_path

def save_csv(results, domain):
    os.makedirs('results', exist_ok=True)
    csv_path = f"results/{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Subdomain", "Real IP", "Resolvers", "Status"])
        for r in results:
            status = "REAL IP" if r.get('real_ips') else "CF PROTECTED" if r.get('cf_protected') else "NO RESULT"
            writer.writerow([
                r.get('subdomain'),
                ', '.join(r.get('real_ips', [])),
                ', '.join(r.get('resolvers', [])),
                status
            ])
    return csv_path
