# Regulus UDP abstraction layer

#   Copyright (C) 2018 Renze Nicolai

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import socket

def createUdpSocket(UDP_IP='0.0.0.0', UDP_PORT=0, bind=False, reuse=False, broadcast=False, multicast=False, blocking=True):
	### Creates an UDP socket (called by the wrappers below this function)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	if (reuse):
		try:
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except AttributeError:
			pass
	if (multicast): #1/2
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
	if (bind):
		sock.bind((UDP_IP, UDP_PORT))
	if (broadcast):
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	if (multicast): #2/2
		host = socket.gethostbyname(socket.gethostname())
		sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
		sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(UDP_IP) + socket.inet_aton(host))
	if not blocking:
		sock.setblocking(False)
	return sock

### SOCKET CREATION

def createRobotSocket(port=10001):
	### Creates a socket that listens like a robot
	return createUdpSocket('0.0.0.0', port, True, True, False, False, True)

def createServerSocket(port=10001):
	### Creates a socket to talk (broadcast) to the robots
	return createUdpSocket('255.255.255.255', port, False, True, True, False, True)

def createVisionSocket(port=10002):
	### Creates a socket that subscribes (multicast) to server messages from ssl-vision
	return createUdpSocket('224.5.23.2', port, True, True, False, True, True)

def createVisionGeometrySocket():
	return createVisionSocket(10006)

### DATA PROCESSING

def receive(sock):
	### Waits for data, returns data once packet is received
	return sock.recv(4096)

def transmit(sock, server, port, cmd):
	### Sends data to a specified server (for interoperability between teams)
	sock.sendto(cmd, (server, port))
	
def broadcast(sock, data, port=10001):
	### Broadcasts data to all robots
	sock.sendto(data, ('255.255.255.255', port))
