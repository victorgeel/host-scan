#!/usr/bin/env python3

from colorama import Fore, Back, Style
import socket, os, sys, struct, concurrent.futures, subprocess
import signal
import os

def handler(say, frame):
    os.system("clear")
    print(Fore.RED+Style.DIM+"\n\n[+] Saliendo...\n"+Fore.WHITE+Style.NORMAL)
    sys.exit(1)

signal.signal(signal.SIGINT, handler)

# Create two empty lists to store open TCP and UDP ports
tcp_ports = []
udp_ports = []

def scan_tcp(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1) # Reduce timeout to 0.1 seconds
    try:
        s.connect((host, port))
        print(Fore.BLUE+Style.DIM+f"[+] El puerto {port} TCP está abierto")
        # Add the port to the TCP list
        tcp_ports.append(str(port))
        s.close()
    except:
        pass

def scan_udp(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0.1) # Reduce timeout to 0.1 seconds
    if port == 53: # If the port is 53, send a DNS query
        data = struct.pack("!HHHHHH", 1, 0, 1, 0, 0, 0) # ID = 1, flags = 0, QDCOUNT = 1, ANCOUNT = 0, NSCOUNT = 0, ARCOUNT = 0
        data += b"\x03www\x07example\x03com\x00" # QNAME = www.example.com in tag format
        data += struct.pack("!HH", 1, 1) # QTYPE = A (1), QCLASS = IN (1)
    else: # If port is not 53, send an empty message
        data = b""
    s.sendto(data, (host, port))
    try:
        data, addr = s.recvfrom(1024)
        print(Fore.YELLOW+f"[+] El puerto {port} UDP está abierto")
        # Add the port to the UDP list
        udp_ports.append(str(port))
        s.close()
    except socket.timeout:
        pass
    except socket.error as e:
        print(f"Error en el puerto {port} UDP: {e}")
        pass

if __name__ == '__main__':
    
    os.system("clear && figlet Host Scan | lolcat")
    
    host = input(Fore.MAGENTA+Style.BRIGHT+"Introduce la IP a analizar: "+Fore.WHITE+Style.NORMAL)
    print("\n")
    
    # Modify the maximum threads that can run on the system
    os.system("ulimit -n 5100")
    
    # Create a thread pool with a maximum of 5000
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5000)

    # Use the map method to assign each port to a thread in the pool
    executor.map(scan_tcp, [host]*65535, range(1,65536))
    print("\n")
    executor.map(scan_udp, [host]*65535, range(1,65536))

    # Wait for all threads to finish
    executor.shutdown(wait=True)

    print(Fore.LIGHTCYAN_EX+Style.BRIGHT+"\n[+] ¡El escaneo ha terminado!")

    # Ask the user if they want to copy the TCP ports
    tcp_response = input(Fore.LIGHTMAGENTA_EX+Style.NORMAL+"\nCopy TCP ports? (y/n): ")

    if respuesta_tcp == "y":
        # Convert the list of TCP ports to a comma-separated string
        tcp_ports_str = ",".join(tcp_ports)
        # Run the xclip command with TCP ports as standard input
        subprocess.run(["xclip", "-sel", "clip"], input=tcp_ports_str.encode(), check=True)
        print(Fore.GREEN+Style.BRIGHT+"\n[+] ¡Puertos TCP copiados al portapapeles!")
    else:
        pass

    # Ask the user if they want to copy the UDP ports
    udp_response = input(Fore.LIGHTMAGENTA_EX+Style.NORMAL+"\nDo you want to copy the UDP ports? (y/n): ")

    if respuesta_udp == "y":
        # Convert the list of UDP ports to a comma-separated string
        udp_ports_str = ",".join(udp_ports)
        # Run the xclip command with UDP ports as standard input
        subprocess.run(["xclip", "-sel", "clip"], input=udp_ports_str.encode(), check=True)
        print(Fore.LIGHTGREEN_EX+Style.BRIGHT+"\n[+] ¡Puertos UDP copiados al portapapeles!\n"+Fore.WHITE+Style.NORMAL)
    else:
        print(Fore.RED+Style.DIM+"\n[-] No se copian los puertos UDP\n"+Style.NORMAL+Fore.WHITE)
