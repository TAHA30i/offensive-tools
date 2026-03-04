import socket
import selectors
from sys import stdout
import errno
import argparse
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

# ---------------- GLOBALS ----------------
found_ports = []
lock = Lock()
# colors
init(autoreset=True)
red = Fore.RED
green = Fore.GREEN
yellow = Fore.YELLOW

# ---------------- SCAN LOGIC ----------------
def scan(ip, port, timeout) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)

    try:
        attempt = sock.connect_ex((ip, port))

        if attempt == 0:
            with lock:
                found_ports.append(port)

        elif attempt == errno.EINPROGRESS:
            sel = selectors.DefaultSelector()
            sel.register(sock, selectors.EVENT_WRITE)

            events = sel.select(timeout=timeout)
            for key, mask in events:
                sock_obj = key.fileobj
                if mask & selectors.EVENT_WRITE:
                    sock_opt = sock_obj.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                    if sock_opt == 0:
                        with lock:
                            found_ports.append(port)
        else:
            pass

    except Exception as exp:
        stdout.write(f"\r{red}Error  at port {port} :  {exp}")
        stdout.flush()

    finally:
        sock.close()
        sel.close()

#--------- SERVICE IDENTIFICATION -----

def id_service():
	print(f"\n{yellow}[info] Scanning finished")
	print(f"{yellow}[info] beware service identification may be inaccurate")
	print("-" * (len(found_ports) + 10) + ' Results ' + "-" * (len(found_ports) + 10))

	lports = sorted(found_ports)

	for port in lports:
		try:
			service = (socket.getservbyport(port)).upper()

		except OSError:
			service = "TCP"

		finally:
			print(f"\t{port} \t\t{service}")

#--------------------------------------


# ---------------- MAIN ----------------
def main() -> None:
    parser = argparse.ArgumentParser(description="A simple BannerGrabber (supported protocols: FTP, HTTP, TCP)")
    parser.add_argument('-i', '--ip', required=True, type=str, help="Specify the target IP")
    parser.add_argument('-p', '--port', required=True, type=int, help="Specify the max port number")
    parser.add_argument('-t', '--timeout', type=float, default=5.0, help="Specify timeout in seconds (default: 5)")
    parser.add_argument('-th', '--threads', type=int, default=25, help="Specify number of threads (default: 25)")
    args = parser.parse_args()

    print(f'{green}[info] if you see this the tool is working\n[info] if you see a "to many open files" error  , relax! it just mean that you reached the file limit that your os gave you ')

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for port in range(1, args.port + 1):
            executor.submit(scan, args.ip, port, args.timeout)


    id_service()


if __name__ == "__main__":
    main()
