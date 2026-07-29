#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import requests
import socket
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from modules.waf_bypass import waf_bypass_test, ip_protection_check

from modules.resolver import RESOLVERS
from modules.cloudflare import get_cf_ranges
from modules.scanner import scan_all_subs
from modules.portscan import port_scan
from modules.utils import clear, save_results, save_csv
from modules.verifier import smart_verify
from modules.cdn_detector import cdn_check, CDN_SIGNATURES
from modules.waf_detector import detect_waf
from concurrent.futures import ThreadPoolExecutor, as_completed

console = Console()
VERSION = "2.1"
AUTHOR = "Spectra"

BANNER = """
[bold cyan]
 ██████╗██╗      ██████╗ ██╗   ██╗██████╗
██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗
██║     ██║     ██║   ██║██║   ██║██║  ██║
██║     ██║     ██║   ██║██║   ██║██║  ██║
╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝
 ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝

███████╗ █████╗ ██╗     ██╗
██╔════╝██╔══██╗██║     ██║
█████╗  ███████║██║     ██║
██╔══╝  ██╔══██║██║     ██║
██║     ██║  ██║███████╗███████╗
╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝
CLOUDFALL v2.1 - ULTIMATE EDITION
Developer : Spectra
langueage : python
[/bold cyan]
"""
def show_guide():
    """Tampilkan panduan penggunaan"""
    console.print(Panel(
        "[bold yellow]📖 PANDUAN PENGGUNAAN CLOUDFALL[/bold yellow]\n\n"
        "[cyan]1. Masukkan domain target[/cyan]\n"
        "   [dim]Contoh: dpr.go.id, tokopedia.com, google.com[/dim]\n\n"
        "[cyan]2. Tools akan melakukan:[/cyan]\n"
        "   [dim]- Scan 794+ subdomain[/dim]\n"
        "   [dim]- Resolve DNS dengan 5 resolver[/dim]\n"
        "   [dim]- Filter IP Cloudflare[/dim]\n"
        "   [dim]- Verifikasi IP otomatis[/dim]\n"
        "   [dim]- Scan port terbuka[/dim]\n\n"
        "[cyan]3. Hasil akan ditampilkan dalam tabel[/cyan]\n"
        "   [dim]- ✅ VALID = IP mengembalikan halaman yang sama[/dim]\n"
        "   [dim]- ⚠️ CDN = IP masih terdeteksi CDN[/dim]\n"
        "   [dim]- ❌ INVALID = IP tidak merespon[/dim]\n\n"
        "[cyan]4. Hasil disimpan di folder results/[/cyan]\n"
        "   [dim]- JSON, TXT, CSV[/dim]",
        title="[bold cyan]📖 PANDUAN[/bold cyan]",
        title_align="center",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))

def load_wordlist(path="wordlists/exploit.txt"):
    try:
        with open(path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        console.print(f"[red][!] Wordlist tidak ditemukan: {path}[/red]")
        sys.exit(1)

def show_results(results, domain):
    has_cdn, cdns = cdn_check(domain)
    real_ips = [r for r in results if r.get('real_ips')]

    if real_ips:
        console.print(f"\n[bold red][🔥] REAL IP DITEMUKAN (SMART VERIFY):[/bold red]")

        table = Table(show_header=True, header_style="bold red", box=box.ROUNDED)
        table.add_column("Subdomain", style="bold cyan")
        table.add_column("Real IP", style="green")
        table.add_column("Status", style="bold")
        table.add_column("Akses", style="yellow")
        table.add_column("Ports", style="magenta")

        with Progress(SpinnerColumn(), TextColumn("[cyan]Verifying with Smart Method...[/cyan]"), console=console) as progress:
            task = progress.add_task("", total=len(real_ips))
            for r in real_ips:
                ip = r['real_ips'][0]
                status, method, code = smart_verify(ip, domain)
                ports = port_scan(ip)

                # ===== LOGIKA LINK =====
                if "VALID" in status:
                    status_display = f"[green]✅ {status}[/green]"

                    try:
                        import requests
                        test = requests.get(f"http://{ip}", timeout=3)
                        if test.status_code == 200:
                            akses = f"[cyan]🌐 http://{ip}[/cyan]"
                        elif test.status_code in [301, 302]:
                            location = test.headers.get('Location', '')
                            akses = f"[yellow]🔀 {location}[/yellow]"
                        else:
                            akses = f"[dim]🔗 curl -H \"Host: {domain}\" http://{ip}[/dim]"
                    except:
                        akses = f"[dim]🔗 curl -H \"Host: {domain}\" http://{ip}[/dim]"
                else:
                    status_display = f"[red]❌ {status}[/red]"
                    akses = "[dim]Tidak dapat diakses[/dim]"

                table.add_row(
                    r['subdomain'],
                    ip,
                    status_display,
                    akses,
                    ', '.join(ports) if ports else "-"
                )
                progress.update(task, advance=1)

        console.print(table)

    wafs = detect_waf(domain)
    
    if wafs:
        console.print(f"\n[red][🛡️] WAF TERDETEKSI![/red]")
        for waf in wafs:
            console.print(f"  [yellow]→ {waf}[/yellow]")
    else:
        console.print(f"\n[green]✅ TIDAK ADA WAF[/green]")


    # ===== CDN DETECTION =====
    if has_cdn:
        console.print(f"\n[yellow][🛡️] CDN TERDETEKSI PADA DOMAIN UTAMA:[/yellow]")
        for cdn in cdns:
            console.print(f"  [yellow]→ {cdn}[/yellow]")

        console.print(f"\n[bold yellow]💡 REKOMENDASI:[/bold yellow]")
        console.print("  [dim]• Gunakan IP di atas dengan 'Host header' untuk verifikasi[/dim]")
        console.print("  [dim]• Coba akses: curl -H \"Host: {domain}\" http://[IP][/dim]")
    else:
        console.print(f"\n[green]✅ TIDAK ADA CDN PADA DOMAIN UTAMA[/green]")
        console.print("  [dim]→ Domain ini bisa langsung diakses tanpa proteksi CDN[/dim]")
    
    try:
        import socket
        ip = socket.gethostbyname(domain)
        console.print(f"\n[bold cyan]📌 INFO DOMAIN:[/bold cyan]")
        console.print(f"  [green]IP: {ip}[/green]")
    except:
        pass
    
    console.input("\n[dim]Press Enter to continue...[/dim]")

def main():
    clear()
    console.print(BANNER)
    console.print()
    
    show_guide()
    
    console.print(Panel(
        "[bold red]☁️ READY TO RIP THE CLOUDS - ULTIMATE EDITION[/bold red]",
        title="[bold yellow]WELCOME TO CLOUDFALL[/bold yellow]",
        title_align="center",
        border_style="red",
        box=box.ROUNDED,
        expand=True,
        padding=(1, 2)
    ))
    
    console.print(f"\n[bold green]📌 Resolvers: {', '.join(RESOLVERS)}[/bold green]")
    console.print(f"[bold green]📌 CF Ranges: {len(get_cf_ranges())} CIDR[/bold green]")
    console.print("[dim]💡 Ketik '?' untuk panduan, 'exit' untuk keluar[/dim]\n")
    
    domain = Prompt.ask("[bold yellow]Domain >[/bold yellow]")
    if not domain or domain.lower() == 'exit':
        console.print("[red][!] Keluar...[/red]")
        sys.exit(0)
    
    if domain == '?':
        show_guide()
        input("\n[dim]Press Enter to continue...[/dim]")
        return main()
    
    subs = load_wordlist()
    console.print(f"[dim][INFO] Wordlist: exploit.txt ({len(subs)} subs)[/dim]\n")
    
    results = scan_all_subs(subs, domain, max_workers=100)
    
    show_results(results, domain)
    
    if results:
        json_path, txt_path = save_results(results, domain)
        csv_path = save_csv(results, domain)
        console.print(f"\n[green][✓] Hasil disimpan:[/green]")
        console.print(f"  [dim]JSON: {json_path}[/dim]")
        console.print(f"  [dim]TXT: {txt_path}[/dim]")
        console.print(f"  [dim]CSV: {csv_path}[/dim]")
    
    console.print("\n[dim]Press Enter to exit...[/dim]")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow][!] Keluar...[/yellow]")
        sys.exit(0)
