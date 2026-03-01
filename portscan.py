import socket
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from sys import stdout
from colorama import Fore , Style , init
import argparse


# global
init(autoreset=True)
open_ports = []
lock = Lock()

# colors
red = Fore.RED
green = Fore.GREEN
yellow = Fore.YELLOW


# logic
def scan(ip , port_range , timeout) -> None:
    print(f'{yellow} info : this a basic portscanner')
    print(f'{yellow} info : note that will be easily blocked by firewalls')

    with socket( socket.AF_INET , socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)

        try:
            for port  in range(port_range):
                if sock.connect_ex(( ip , port )) == 0:
                    with lock:
                        open_ports.append(port)

                with lock:
                    stdout.write(f"reached : {port}")
                    stdout.flush()

        except Exception as exp:
            print(f"{red} error : {exp}")


def id_services():
    print(f"{green} service identification ")
    print(f"{yellow} info : this a basic service recognition , its unreliable") # for a robust recon , we might use payload based recon

    lports = open_ports # reducing the scope

    if not lports:
        print(f"{yellow} info : No ports open")
        exit(1)

    for port in lports:
        try:
            service = socket.getservbyport(port)

        except OSError:
            service = "-"

        finally:
            print(f"{green} port : {port} | service {service}")


def main() -> None:
    parser = argparse.ArgumentParser(description="a basic portscanner ")

    parser.add_argument('-i' ,  type=str , default='127.0.0.1' ,  help="specify the target ip address")
    parser.add_argument('-p' ,  type=int , default=1024 , help=" set the port range ( default is 1024 )")
    parser.add_argument('-t' , '--timeout' , type=float , default=0.5 , help="set a timeout ( default is 0.5 )")
    parser.add_argument('-w' , '-workers' , type=int , default=25 , help="set the thread count ( default is 25 )")

    args = parser.parse_args()


    print('\t \t INFO')
    print("#" * 50)
    print(f"Target : {args.i}")
    print(f"Port-Range : {args.p}")
    print(f"Timeout : {args.timeout}")
    print(f"Thread-Count : {args.w}")
    print("#" * 50)

    sleep(1)

    print("#" * 50)
    with ThreadPoolExecutor(max_workers=args.w) as executor:
        executor.submit(scan , args.i , args.p , args.timeout)

    sleep(1)
    id_services()

if __name__ == "__main__":
        main()
