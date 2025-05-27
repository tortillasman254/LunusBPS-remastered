import os, concurrent.futures, time, threading, random, string, json, ctypes, sys
import requests, colorama, pystyle, datetime, socks, socket, tls_client
import asyncio 
import aiohttp 
from aiohttp_socks import ProxyConnector, ProxyType, SocksConnectionError, SocksError # Added aiohttp-socks imports
import platform # Added platform import

from requests.exceptions import SSLError 

# Removed the try-except block for automatic module installation.
# Dependencies are now expected to be installed via requirements.txt.

# Apply Windows event loop policy fix for aiodns/aiohttp
if platform.system() == "Windows":
    try:
        # WindowsSelectorEventLoopPolicy is preferred for aiohttp on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except AttributeError:
        # Fallback for older Python versions where WindowsSelectorEventLoopPolicy might not be directly available
        # This might not fully resolve aiodns issues if WindowsSelectorEventLoopPolicy is truly needed and missing,
        # but it's better than a hard crash if the policy class itself isn't found.
        # A more robust solution for very old Pythons would involve checking Python version further.
        # However, aiodns itself has minimum Python version requirements.
        print(f"{Fore.YELLOW}Note: Could not apply WindowsSelectorEventLoopPolicy. Using default asyncio policy for Windows.{Fore.RESET}")
        pass # Or log a warning

from pystyle import Write, System, Colors, Colorate, Anime
from colorama import Fore, Style
from datetime import datetime

https_scraped = 0
socks4_scraped = 0
socks5_scraped = 0

http_checked = 0
socks4_checked = 0
socks5_checked = 0

red = Fore.RED
yellow = Fore.YELLOW
green = Fore.GREEN
blue = Fore.BLUE
orange = Fore.RED + Fore.YELLOW
pretty = Fore.LIGHTMAGENTA_EX + Fore.LIGHTCYAN_EX
magenta = Fore.MAGENTA
lightblue = Fore.LIGHTBLUE_EX
cyan = Fore.CYAN
gray = Fore.LIGHTBLACK_EX + Fore.WHITE
reset = Fore.RESET
pink = Fore.LIGHTGREEN_EX + Fore.LIGHTMAGENTA_EX
dark_green = Fore.GREEN + Style.BRIGHT
output_lock = threading.Lock() # For thread-safe printing from synchronous parts

def get_time_rn():
    date = datetime.now()
    hour = date.hour
    minute = date.minute
    second = date.second
    timee = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
    return timee

def update_title():
    global https_scraped, socks4_scraped, socks5_scraped
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(f'[ LunusBPS ] By H4cK3dR4Du & 452b | HTTP/s Scraped : {https_scraped} ~ Socks4 Scraped : {socks4_scraped} ~ Socks5 Scraped : {socks5_scraped}')
    except Exception: # Handle cases where console might not be available
        pass

def update_title2():
    global http_checked, socks4_checked, socks5_checked
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(f'[ LunusBPS ] By H4cK3dR4Du & 452b | HTTP/s Valid : {http_checked} ~ Socks4 Valid : {socks4_checked} ~ Socks5 Valid : {socks5_checked}')
    except Exception:
        pass

def ui():
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(f"[ LunusBPS ] By H4cK3dR4Du & 452b | Starting... ")
        System.Clear()
        Write.Print(f"""
		888                                              888888b.   8888888b.   .d8888b.  
		888                                              888  \"88b  888   Y88b d88P  Y88b 
		888                                              888  .88P  888    888 Y88b.      
		888     888  888 88888b.  888  888 .d8888b       8888888K.  888   d88P  \"Y888b.   
		888     888  888 888 \"88b 888  888 88K           888  \"Y88b 8888888P\"      \"Y88b. 
		888     888  888 888  888 888  888 \"Y8888b.      888    888 888              \"888 
		888     Y88b 888 888  888 Y88b 888      X88      888   d88P 888        Y88b  d88P 
		88888888 \"Y88888 888  888  \"Y88888  88888P'      8888888P\"  888         \"Y8888P\"                                                                                  
                                                                                  
		[ This tool is a scraper & checker for HTTP/s, SOCKS4, and SOCKS5 proxies. ]
					[ The Best Ever Not Gonna Lie ]                                                                          
""", Colors.red_to_blue, interval=0.000) # Interval 0 for no animation if too slow
        time.sleep(1) # Reduced sleep
    except Exception: # if pystyle fails or console issues
        print("Lunus Best Proxy Scraper 🪐")

# Function to load custom proxy sources / Display startup menu
def load_custom_sources():
    global http_links, socks4_list, socks5_list
    
    print(f"{cyan}--- Lunus Proxy Scraper Menu ---{reset}")
    print(f"{pink}Please choose an option:{reset}")
    print(f"{green}1. Scrape & Check Proxies (Default Sources){reset}")
    print(f"{yellow}2. Scrape & Check Proxies (Custom Sources){reset}")
    print(f"{red}3. Exit{reset}")
    
    choice = input(f"{cyan}Enter your choice (1-3): {reset}").strip()

    if choice == '1':
        print(f"{blue}> Proceeding with default proxy sources.{reset}\n")
        return # Default lists are already populated
    elif choice == '2':
        print(f"{cyan}--- Loading Custom Proxy Sources ---{reset}")
        source_types = [
            ("HTTP", "http_links"),
            ("SOCKS4", "socks4_list"),
            ("SOCKS5", "socks5_list")
        ]
        
        for display_name, list_variable_name in source_types:
            current_default_count = 0
            # Get current length of default lists to show in prompt
            if list_variable_name == "http_links": current_default_count = len(http_links)
            elif list_variable_name == "socks4_list": current_default_count = len(socks4_list)
            elif list_variable_name == "socks5_list": current_default_count = len(socks5_list)

            file_path = input(f"{yellow}Enter file path for {display_name} proxy sources (leave blank to use default - {current_default_count} sources): {reset}").strip()
            
            if file_path:
                try:
                    with open(file_path, 'r') as f:
                        custom_sources = [line.strip() for line in f if line.strip()]
                    
                    if custom_sources:
                        if list_variable_name == "http_links":
                            http_links = custom_sources
                        elif list_variable_name == "socks4_list":
                            socks4_list = custom_sources
                        elif list_variable_name == "socks5_list":
                            socks5_list = custom_sources
                        print(f"{green}> Loaded {len(custom_sources)} {display_name} sources from {file_path}.{reset}")
                    else:
                        print(f"{red}> File {file_path} is empty. Using default {display_name} sources ({current_default_count} sources).{reset}")
                except FileNotFoundError:
                    print(f"{red}> Error: File {file_path} not found. Using default {display_name} sources ({current_default_count} sources).{reset}")
                except OSError as e:
                    print(f"{red}> Error reading file {file_path}: {e}. Using default {display_name} sources ({current_default_count} sources).{reset}")
            else:
                print(f"{blue}> Using default {display_name} sources ({current_default_count} sources).{reset}")
        print(f"{cyan}--- End Custom Proxy Sources ---{reset}\n")
    elif choice == '3':
        print(f"{blue}Exiting script.{reset}")
        sys.exit(0)
    else:
        print(f"{red}Invalid choice. Exiting.{reset}")
        sys.exit(1)

# Default proxy source lists
http_links = [
    "https://api.proxyscrape.com/?request=getproxies&proxytype=https&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/saisuiu/Lionkings-Http-Proxys-Proxies/main/cnfree.txt",
    "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
    "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt"
]

socks4_list = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4",
    "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4&country=all",
    "https://api.openproxylist.xyz/socks4.txt",
    "https://proxyspace.pro/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks4.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
    "https://www.proxy-list.download/api/v1/get?type=socks4", 
    "https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks4.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks4.txt",
    "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS4.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies_anonymous/socks4.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks4.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt",
    "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt",
    "https://www.proxyscan.io/download?type=socks4",
]

socks5_list = [
    "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt",
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
    "https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks5.txt",
    "https://api.openproxylist.xyz/socks5.txt",
    "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5",
    "https://proxyspace.pro/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies_anonymous/socks5.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt",
    "https://spys.me/socks.txt", 
    "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt"
]

async def test_links_async(links_to_test, session, link_type_name_for_log):
    tasks = []
    for link in links_to_test:
        tasks.append(asyncio.create_task(session.get(link, timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True)))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid_links_for_current_batch = []
    
    for i, result_or_exc in enumerate(results):
        link = links_to_test[i]
        if isinstance(result_or_exc, aiohttp.ClientResponse):
            try:
                if result_or_exc.status == 200:
                    print(f"{green}[{get_time_rn()}] Success testing link (Async): {link}{reset}")
                    valid_links_for_current_batch.append(link)
                else:
                    print(f"{red}[{get_time_rn()}] Failed testing link (Async): {link} - Status: {result_or_exc.status}{reset}")
            finally:
                result_or_exc.close()
        elif isinstance(result_or_exc, SSLError):
            print(f"{red}[{get_time_rn()}] SSL Error testing link (Async): {link} - {result_or_exc}{reset}")
        elif isinstance(result_or_exc, asyncio.TimeoutError):
            print(f"{red}[{get_time_rn()}] Timeout testing link (Async): {link}{reset}")
        elif isinstance(result_or_exc, aiohttp.ClientError):
            print(f"{red}[{get_time_rn()}] Client Error testing link (Async): {link} - {result_or_exc}{reset}")
        elif isinstance(result_or_exc, Exception):
            print(f"{red}[{get_time_rn()}] Generic Error testing link (Async): {link} - {type(result_or_exc).__name__}: {result_or_exc}{reset}")
            
    return valid_links_for_current_batch

def scrape_proxy_links_https(link):
    global https_scraped
    try:
        response = requests.get(link, timeout=10) 
        response.raise_for_status()
        with output_lock:
            time_rn = get_time_rn()
            print(f"[ {pink}{time_rn}{reset} ] | ( {green}SCRAPED{reset} ) {pretty}HTTP/S --> {link[:60]}...{reset}")
        proxies = response.text.splitlines()
        https_scraped += len(proxies)
        update_title()
        return proxies
    except requests.exceptions.RequestException as e:
        with output_lock:
            print(f"{red}[{get_time_rn()}] Failed to scrape HTTPS {link}: {e}{reset}")
    return []

async def scrape_proxy_links_https(link, session):
    global https_scraped
    try:
        async with session.get(link, timeout=aiohttp.ClientTimeout(total=10)) as response: # Use session
            response.raise_for_status()
            proxies_text = await response.text()
            with output_lock:
                time_rn = get_time_rn()
                print(f"[ {pink}{time_rn}{reset} ] | ( {green}SCRAPED{reset} ) {pretty}HTTP/S --> {link[:60]}...{reset}")
            proxies = proxies_text.splitlines()
            https_scraped += len(proxies)
            update_title()
            return proxies
    except (aiohttp.ClientError, asyncio.TimeoutError) as e: # Updated exceptions
        with output_lock:
            print(f"{red}[{get_time_rn()}] Failed to async scrape HTTPS {link}: {e}{reset}")
    return []

async def scrape_proxy_links_socks4(link, session):
    global socks4_scraped
    try:
        async with session.get(link, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            proxies_text = await response.text()
            with output_lock:
                time_rn = get_time_rn()
                print(f"[ {pink}{time_rn}{reset} ] | ( {green}SCRAPED{reset} ) {pretty}SOCKS4 --> {link[:60]}...{reset}")
            proxies = proxies_text.splitlines()
            socks4_scraped += len(proxies)
            update_title()
            return proxies
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        with output_lock:
            print(f"{red}[{get_time_rn()}] Failed to async scrape SOCKS4 {link}: {e}{reset}")
    return []

async def scrape_proxy_links_socks5(link, session):
    global socks5_scraped
    try:
        async with session.get(link, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            proxies_text = await response.text()
            with output_lock:
                time_rn = get_time_rn()
                print(f"[ {pink}{time_rn}{reset} ] | ( {green}SCRAPED{reset} ) {pretty}SOCKS5 --> {link[:60]}...{reset}")
            proxies = proxies_text.splitlines()
            socks5_scraped += len(proxies)
            update_title()
            return proxies
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        with output_lock:
            print(f"{red}[{get_time_rn()}] Failed to async scrape SOCKS5 {link}: {e}{reset}")
    return []

async def check_proxy_http_async(proxy, session):
    global http_checked
    url = 'https://httpbin.org/ip' 
    proxy_url = f"http://{proxy}"
    try:
        async with session.get(url, proxy=proxy_url, timeout=aiohttp.ClientTimeout(total=7)) as response:
            response.raise_for_status() # Will raise for 4xx/5xx status
            # Optionally, check response content if needed
            # await response.text() 
            with output_lock:
                time_rn = get_time_rn()
                print(f"[ {pink}{time_rn}{reset} ] | ( {green}VALID{reset} ) {pretty}HTTP/S --> {proxy}{reset}")
            http_checked += 1
            update_title2()
            with open(os.path.join("Results", "http.txt"), "a") as f:
                f.write(proxy + "\n")
    except (aiohttp.ClientError, asyncio.TimeoutError, SocksConnectionError, SocksError, OSError) as e:
        # print(f"{red}Failed HTTP check for {proxy}: {e}{reset}") # Optional: for debugging
        pass

async def checker_proxy_socks_async(proxy, proxy_type_const):
    global socks4_checked, socks5_checked
    
    try:
        parts = proxy.split(':')
        if len(parts) < 2: # Basic check for at least ip:port
            # Potentially log to console with output_lock if desired
            # print(f"{yellow}[{get_time_rn()}] Skipping malformed SOCKS proxy (not enough parts): {proxy}{reset}")
            return # Skip this proxy

        ip = parts[0]
        port_str = parts[1]

        # Validate IP (basic check, can be enhanced if needed)
        if not ip: # Check if IP is empty
            # print(f"{yellow}[{get_time_rn()}] Skipping SOCKS proxy with empty IP: {proxy}{reset}")
            return

        port = int(port_str) # This can raise ValueError

        if not (0 <= port <= 65535):
            # print(f"{yellow}[{get_time_rn()}] Skipping SOCKS proxy with invalid port range: {proxy}{reset}")
            return # Skip this proxy

    except ValueError: # Catches if port_str is not a valid integer
        # print(f"{yellow}[{get_time_rn()}] Skipping SOCKS proxy with non-integer port: {proxy}{reset}")
        return # Skip this proxy
    except Exception as e: # Catch any other unexpected parsing errors
        # print(f"{red}[{get_time_rn()}] Error parsing SOCKS proxy string {proxy}: {e}{reset}")
        return

    if proxy_type_const == socks.PROXY_TYPE_SOCKS4:
        connector = ProxyConnector.from_url(f"socks4://{ip}:{port}")
        type_str = "SOCKS4"
    elif proxy_type_const == socks.PROXY_TYPE_SOCKS5:
        connector = ProxyConnector.from_url(f"socks5://{ip}:{port}")
        type_str = "SOCKS5"
    else:
        return # Should not happen

    try:
        async with aiohttp.ClientSession(connector=connector, trust_env=False) as proxy_session:
            # Using HEAD for efficiency, target doesn't need to be Google specifically, just a reliable server
            async with proxy_session.head("https://www.google.com", timeout=aiohttp.ClientTimeout(total=7), allow_redirects=False) as resp:
                # Consider 2xx and 3xx as success for connectivity check
                if 200 <= resp.status < 400:
                    with output_lock:
                        time_rn = get_time_rn()
                        print(f"[ {pink}{time_rn}{reset} ] | ( {green}VALID{reset} ) {pretty}{type_str} --> {proxy}{reset}")
                    
                    if proxy_type_const == socks.PROXY_TYPE_SOCKS4:
                        socks4_checked += 1
                        with open(os.path.join("Results", "socks4.txt"), "a") as f:
                            f.write(proxy + "\n")
                    else: # SOCKS5
                        socks5_checked += 1
                        with open(os.path.join("Results", "socks5.txt"), "a") as f:
                            f.write(proxy + "\n")
                    update_title2()
    except (aiohttp.ClientError, SocksConnectionError, SocksError, asyncio.TimeoutError, OSError) as e:
        # print(f"{red}Failed {type_str} check for {proxy}: {e}{reset}") # Optional: for debugging
        pass
    finally:
        # Connectors should be closed if they are not managed by a session's context manager
        # However, in this case, the session created with the connector is closed, which handles the connector.
        if 'connector' in locals() and connector: # Ensure connector was initialized
             await connector.close()


async def check_all_proxies_async(proxy_type_str, pathTXT, session): # session is for HTTP checks
    with open(pathTXT, "r") as f:
        proxies = [line.strip() for line in f if line.strip() and ":" in line]

    if not proxies:
        print(f"{yellow}No proxies to check in {pathTXT}{reset}")
        return

    # num_check_workers = min(len(proxies), 200) # Max concurrency for asyncio.gather
    # print(f"{cyan}Checking {len(proxies)} {proxy_type_str.upper()} proxies from {pathTXT} asynchronously...{reset}")

    tasks = []
    if proxy_type_str == "http":
        tasks = [check_proxy_http_async(p, session) for p in proxies]
    elif proxy_type_str == "socks4":
        tasks = [checker_proxy_socks_async(p, socks.PROXY_TYPE_SOCKS4) for p in proxies]
    elif proxy_type_str == "socks5":
        tasks = [checker_proxy_socks_async(p, socks.PROXY_TYPE_SOCKS5) for p in proxies]
    
    if tasks:
        await asyncio.gather(*tasks)

async def run_checkers_async(proxy_config, session): # session is the main session for HTTP
    checker_tasks = []
    for proxy_type_str, file_path in proxy_config:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            # Pass the main session only if it's for HTTP checks, SOCKS checks create their own.
            current_session_for_task = session if proxy_type_str == "http" else None
            checker_tasks.append(check_all_proxies_async(proxy_type_str, file_path, current_session_for_task))
        else:
            print(f"{yellow}Skipping checks for {proxy_type_str.upper()}: {file_path} is empty or missing.{reset}")
            
    if checker_tasks:
        await asyncio.gather(*checker_tasks)

async def main_async():
    global http_links, socks4_list, socks5_list

    ui()
    load_custom_sources() # Call the new function here

    async with aiohttp.ClientSession() as session: # Main session for HTTP checks and link testing/scraping
        print(f"{pink}Testing HTTP links asynchronously...{reset}")
        http_links = await test_links_async(list(http_links), session, "HTTP")
        
        print(f"\n{pink}Testing SOCKS4 links asynchronously...{reset}")
        socks4_list = await test_links_async(list(socks4_list), session, "SOCKS4")
        
        print(f"\n{pink}Testing SOCKS5 links asynchronously...{reset}")
        socks5_list = await test_links_async(list(socks5_list), session, "SOCKS5")

        print(f"\n{cyan}--- Starting Asynchronous Scraping Process ---{reset}")
    
        scraped_proxies_http = []
        if http_links:
            # Assuming scrape_proxy_links_https is already async and takes session
            http_scrape_tasks = [scrape_proxy_links_https(link, session) for link in http_links]
            results_http = await asyncio.gather(*http_scrape_tasks, return_exceptions=True)
            for res in results_http:
                if isinstance(res, list): scraped_proxies_http.extend(res)
        
        with open("http_proxies.txt", "w") as file:
            count = 0
            for proxy in scraped_proxies_http:
                if proxy and ":" in proxy and not any(c.isalpha() for c in proxy.split(':')[0]):
                    file.write(proxy + '\n')
                    count +=1
            print(f"{green}Saved {count} HTTP/S proxies to http_proxies.txt{reset}")
        
        scraped_proxies_socks4 = []
        if socks4_list:
            socks4_scrape_tasks = [scrape_proxy_links_socks4(link, session) for link in socks4_list]
            results_socks4 = await asyncio.gather(*socks4_scrape_tasks, return_exceptions=True)
            for res in results_socks4:
                if isinstance(res, list): scraped_proxies_socks4.extend(res)
                
        with open("socks4_proxies.txt", "w") as file:
            count = 0
            for proxy in scraped_proxies_socks4:
                if proxy and ":" in proxy and not any(c.isalpha() for c in proxy.split(':')[0]):
                    file.write(proxy + '\n')
                    count +=1
            print(f"{green}Saved {count} SOCKS4 proxies to socks4_proxies.txt{reset}")

        scraped_proxies_socks5 = []
        if socks5_list:
            socks5_scrape_tasks = [scrape_proxy_links_socks5(link, session) for link in socks5_list]
            results_socks5 = await asyncio.gather(*socks5_scrape_tasks, return_exceptions=True)
            for res in results_socks5:
                if isinstance(res, list): scraped_proxies_socks5.extend(res)

        with open("socks5_proxies.txt", "w") as file:
            count = 0
            for proxy in scraped_proxies_socks5:
                if proxy and ":" in proxy and not any(c.isalpha() for c in proxy.split(':')[0]):
                    file.write(proxy + '\n')
                    count +=1
            print(f"{green}Saved {count} SOCKS5 proxies to socks5_proxies.txt{reset}")

        await asyncio.sleep(0.5)

        print(f"\n{cyan}--- Starting Asynchronous Checking Process ---{reset}")
        results_dir = "Results"
        if not os.path.exists(results_dir):
            os.mkdir(results_dir)

        for p_type in ["http", "socks4", "socks5"]:
            with open(os.path.join(results_dir, f"{p_type}.txt"), "w") as f:
                f.write("")
        
        proxy_check_config = [
            ("http", "http_proxies.txt"),
            ("socks4", "socks4_proxies.txt"),
            ("socks5", "socks5_proxies.txt")
        ]
        # Pass the main session to run_checkers_async, it will be used for HTTP checks
        await run_checkers_async(proxy_check_config, session) 

    print(f"\n{cyan}--- Cleaning up temporary files ---{reset}")
    for temp_file in ["http_proxies.txt", "socks4_proxies.txt", "socks5_proxies.txt"]:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"{gray}Removed {temp_file}{reset}")
        except OSError as e:
            print(f"{red}Error removing temporary file {temp_file}: {e}{reset}")

    print(f"\n{green}Process Complete. Valid proxies saved in '{results_dir}' directory.")
    input(f"{cyan}Press Enter to exit...{reset}")


if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print(f"{red}\n[!] Exiting gracefully...{reset}")
    except Exception as e:
        import traceback
        print(f"{red}\n[!] An unexpected error occurred in main execution: {e}")
        traceback.print_exc()
    finally:
        print(reset)
