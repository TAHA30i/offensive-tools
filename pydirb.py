"""
A simple ASYNC directory Brute Force 

+ Please Use it for Ethical Usage , this script is only meant for teaching and learning
    You are at Your Own Risk
"""

import asyncio
import aiohttp
import aiofiles
import argparse

# =========================
# GLOBALS
# =========================
FOUND_URLS = []
semaphore = asyncio.Semaphore(500)

# wildcard globals
USE_BASELINE = False
BASELINE_LENGTH = 0

#==================
# COLORS
#==================
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


# =========================
# CORE LOGIC
# =========================
async def get_url(session: aiohttp.ClientSession, url: str):
    async with semaphore:
        try:
            async with session.get(url) as resp:
                body = await resp.text()
                length = len(body)

                #  wildcard filtering
                if USE_BASELINE:
                    if abs(length - BASELINE_LENGTH) < 10:
                        return

                if resp.status == 200:
                    FOUND_URLS.append(f'[{GREEN}200{RESET}] {url}')
                elif resp.status in [300, 301, 302, 307, 401, 403]:
                    FOUND_URLS.append(f'[{YELLOW}{resp.status}{RESET}] {url}')

        except aiohttp.ClientError:
            pass


async def open_wordlist(path: str) -> list:
    try:
        async with aiofiles.open(path, mode='r') as f:
            content = await f.read()
            return content.split()

    except FileNotFoundError:
        raise FileNotFoundError(f"{RED}{path} is not Found!{RESET}")


async def time_and_exec(session: aiohttp.ClientSession, url: str, timeout: float):
    try:
        await asyncio.wait_for(get_url(session, url), timeout=timeout)
    except asyncio.TimeoutError:
        pass


async def detect_wild_card(url: str, session: aiohttp.ClientSession) -> dict:
    target = url.rstrip('/') + '/idontexist123456'

    async with session.get(target) as resp:
        body = await resp.text()
        return {
            "status": resp.status,
            "length": len(body)
        }


# =========================
# CLI
# =========================
def arguments():
    parser = argparse.ArgumentParser(description="Async directory brute forcer")

    parser.add_argument('url', type=str, help='Specify the target URL')
    parser.add_argument('-w', '--wordlist', required=True, type=str, help='Path to wordlist file')
    parser.add_argument('-t', '--timeout', type=float, default=0.5, help='Request timeout')
    parser.add_argument('--detectWildCard', action='store_true', help='Detect wildcard responses')

    return parser.parse_args()


# =========================
# ENTRY POINT
# =========================
async def main() -> None:
    global USE_BASELINE, BASELINE_LENGTH

    args = arguments()

    words: list = await open_wordlist(args.wordlist)

    print('#' * 45)
    print(f'# [{BLUE}INFO{RESET}] TARGET = {args.url}')
    print(f'# [{BLUE}INFO{RESET}] WORD-COUNT = {len(words)}')
    print(f'# [{BLUE}INFO{RESET}] TIMEOUT = {args.timeout}')
    print(f'# [{BLUE}INFO{RESET}] WILDCARD DETECTION = {args.detectWildCard}')
    print('#' * 45)

    async with aiohttp.ClientSession() as session:

        # 🔍 wildcard detection
        if args.detectWildCard:
            baseline = await detect_wild_card(args.url, session)

            print(f"[{YELLOW}INFO{RESET}] Random response → {baseline['status']} (len={baseline['length']})")

            choice = input("Use wildcard filtering? [Y/n]: ").lower()

            if choice in ['y', 'yes', '']:
                USE_BASELINE = True
                BASELINE_LENGTH = baseline['length']
                print(f"[{YELLOW}INFO{RESET}] Filtering ENABLED")
            else:
                print(f"[{YELLOW}INFO{RESET}] Filtering DISABLED")

        tasks = [
            time_and_exec(
                session,
                f"{args.url.rstrip('/')}/{word.lstrip('/')}",
                args.timeout
            )
            for word in words
        ]

        await asyncio.gather(*tasks)

    # results
    if not FOUND_URLS:
        print('(result) Found Nothing')
    else:
        for url in FOUND_URLS:
            print(f"# {url}")

    print("#" * 45)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    asyncio.run(main())