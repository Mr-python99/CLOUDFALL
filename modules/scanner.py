#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .verifier import smart_verify
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from .resolver import resolve_all
from .cloudflare import get_cf_ranges, is_cf_ip

console = Console()

def scan_subdomain(sub, domain, cf_ranges):
    full = f"{sub}.{domain}"
    try:
        ips = resolve_all(full)
        if not ips:
            return None
        
        all_ips = set()
        for resolver, ip_list in ips.items():
            all_ips.update(ip_list)
        
        real_ips = []
        for ip in all_ips:
            if not is_cf_ip(ip, cf_ranges):
                real_ips.append(ip)
        
        if real_ips:
            return {
                'subdomain': full,
                'real_ips': real_ips,
                'all_ips': list(all_ips),
                'resolvers': list(ips.keys())
            }
        else:
            return {
                'subdomain': full,
                'real_ips': [],
                'all_ips': list(all_ips),
                'resolvers': list(ips.keys()),
                'cf_protected': True
            }
    except:
        return None

def scan_all_subs(subs, domain, max_workers=100):
    cf_ranges = get_cf_ranges()
    results = []
    total = len(subs)
    
    console.print(f"[*] CF Ranges: {len(cf_ranges)} CIDR loaded")
    console.print(f"[*] Total subdomain: {total}")
    console.print(f"[*] Root: {domain}")
    console.print(f"[*] Threads: {max_workers} (KALI MODE)\n")
    
    with Progress(
        SpinnerColumn(),
        BarColumn(bar_width=40, style="cyan"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]🔍 SCANNING SUBDOMAIN...[/cyan]", total=total)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scan_subdomain, sub, domain, cf_ranges): sub for sub in subs}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
                    if result.get('real_ips'):
                        console.print(f"  [red][🔥] {result['subdomain']} → {result['real_ips']}[/red]")
                    elif result.get('cf_protected'):
                        console.print(f"  [yellow][🛡️] {result['subdomain']} → CF Protected[/yellow]")
                    else:
                        console.print(f"  [dim][✗] {result['subdomain']} → No result[/dim]")
                progress.update(task, advance=1)
    
    return results
