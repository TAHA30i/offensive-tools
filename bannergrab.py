import socket
import argparse
from colorama import Fore , Style , init

# global
init(autoreset=True)
red = Fore.RED
green  = Fore.GREEN
yellow  = Fore.YELLOW


# tui
def box(text):
    width = len(text) + 2
    print("┌" + "─" * width + "┐")
    print("│ " + text + " │")
    print("└" + "─" * width + "┘")



# logic
def grab(ip , port , timeout , reply_size) -> None:
	with socket.socket(socket.AF_INET , socket.SOCK_STREAM) as sock:
		sock.settimeout( timeout )

		try:
			if sock.connect_ex(( ip , port )) == 0:

				print(f"{green}[success] connection established")
				print(f"{yellow}[info] sending a 'Hello World' in order to not receive a blank")
				sock.sendall('hello world'.encode())


				data = sock.recv(reply_size).decode()
				print(f"{yellow}[info] received a buffer with the size = {len(data)}")

				print("─" * len(data) + '\n' )
				print(data)
				print("─" * len(data))

		except Exception as exp:
			print(f"{red}[error] failed to continue due to {exp}")


		finally:
			sock.close()

def grab_http(ip , port , timeout , reply_size) -> None:
	with socket.socket(socket.AF_INET , socket.SOCK_STREAM) as sock:
		sock.settimeout( timeout )

		try:
			REQ = f""" 

			GET / HTTP/1.1\r\n
			Host: {ip}\r\n
			Connection: close\r\n\r\n

			"""


			if sock.connect_ex(( ip , port )) == 0:

				print(f"{green}[success] connection established")
				print(f"{yellow}[info] sending a 'GET REQUEST' in order to not receive a blank")
				sock.sendall(REQ.encode())


				data = sock.recv(reply_size).decode()
				print(f"{yellow}[info] received a buffer with the size = {len(data)}")

				print("─" * len(data))
				print(data)
				print("─" * len(data))

		except Exception as exp:
			print(f"{red}[error] failed to continue due to {exp}")

		finally:
			sock.close()

def grab_ftp(ip , port , timeout , reply_size) -> None:
	with socket.socket(socket.AF_INET , socket.SOCK_STREAM) as sock:
		sock.settimeout( timeout )

		try:
			REQ = "USER ANONYMOUS"


			if sock.connect_ex(( ip , port )) == 0:

				print(f"{green}[success] connection established")
				print(f"{yellow}[info] sending a 'USER ANONYMOUS' in order to not receive a blank")
				sock.sendall(REQ.encode())


				data = sock.recv(reply_size).decode().split()
				print(f"{yellow}[info] received a buffer with the size = {len(data)}")

				print("─" * len(data))
				print(data)
				print("─" * len(data))

		except Exception as exp:
			print(f"{red}[error] failed to continue due to {exp}")

		finally:
			sock.close()

def main() -> None:
	parser = argparse.ArgumentParser(description="a simple Bannergraber ( supported protocols : FTP , HTTP , TCP )")

	parser.add_argument('-i' , '--ip' , required=True , type=str , help="specify the target ip")
	parser.add_argument('-p' , "--port" , required=True , type=int , help="specify the port number")
	parser.add_argument('--proto' , type=str , default="tcp" , help="specify the protocol (default is TCP )")
	parser.add_argument('-t' , '--timeout' , type=float , default=5.0 , help="specify the timeout (default is 5 seconds )")
	parser.add_argument("-s" , "--size" , type=int , default=1024 , help="specify the reply size ( default is 1024 ")

	args = parser.parse_args()



	match(args.proto.lower()):
		case "http":
			grab_http(args.ip , args.port , args.timeout , args.size)
		case "ftp":
			grab_ftp(args.ip , args.port , args.timeout , args.size)
		case _:
			grab(args.ip , args.port , args.timeout , args.size)



main()
