import requests
import argparse
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from colorama import Fore, Style, init

init(autoreset=True)

found = []
lock = Lock()

# Stats
total_checked = 0
start_time = None


def banner():
    print(Fore.CYAN + r"""

             ____  _      _     
 _ __  _   _|  _ \(_)_ __| |__  
| '_ \| | | | | | | | '__| '_ \ 
| |_) | |_| | |_| | | |  | |_) |
| .__/ \__, |____/|_|_|  |_.__/ 
|_|    |___/    

    Threaded Dir Scanner (Lab Use Only)
""" + Style.RESET_ALL)


def scan(base_url, path, timeout):
    global total_checked

    url = f"{base_url}/{path.strip()}"

    try:
        r = requests.get(url, timeout=timeout)

        with lock:
            total_checked += 1

        if r.status_code != 404:
            with lock:
                found.append((path.strip(), r.status_code))

                if 200 <= r.status_code < 300:
                    color = Fore.GREEN
                elif 300 <= r.status_code < 400:
                    color = Fore.YELLOW
                else:
                    color = Fore.RED

                print(f"{color}[{r.status_code}] {path.strip()}")

    except requests.RequestException:
        with lock:
            total_checked += 1


def progress(total_words):
    while total_checked < total_words:
        elapsed = time.time() - start_time
        rps = total_checked / elapsed if elapsed > 0 else 0

        sys.stdout.write(
            f"\rChecked: {total_checked}/{total_words} | "
            f"Speed: {rps:.2f} req/s"
        )
        sys.stdout.flush()
        time.sleep(0.2)


def main():
    global start_time

    parser = argparse.ArgumentParser(description="Threaded Dir Scanner (Lab Only)")
    parser.add_argument("-u", "--url", required=True)
    parser.add_argument("-w", "--wordlist", required=True)
    parser.add_argument("-t", "--threads", type=int, default=30)
    parser.add_argument("--timeout", type=float, default=3.0)

    args = parser.parse_args()

    banner()

    with open(args.wordlist, "r") as f:
        words = f.readlines()

    total_words = len(words)
    start_time = time.time()

    from threading import Thread
    prog_thread = Thread(target=progress, args=(total_words,))
    prog_thread.start()



    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for word in words:
            executor.submit(scan, args.url.rstrip("/"), word, args.timeout)

    prog_thread.join()

    elapsed = time.time() - start_time

    print("\n\n" + Fore.CYAN + "=" * 50)
    print(Fore.CYAN + "Scan Finished")
    print(f"Time: {elapsed:.2f} seconds")
    print(f"Total Checked: {total_checked}")
    print(f"Found: {len(found)}")
    print("=" * 50)

    for path, code in sorted(found):
        print(f"{path} -> {code}")


if __name__ == "__main__":
    main()
