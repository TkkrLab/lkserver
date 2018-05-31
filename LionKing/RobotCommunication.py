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

from protobuf import robot_pb2 as pbRobotSsh #This is "our" SSH radio protocol
from protobuf import radio_protocol_wrapper_pb2 as pbRobotOfficialWrapper #This is the "official" SSL radio protocol (wrapper)
from protobuf import radio_protocol_command_pb2 as pbRobotOfficialCommand #This is the "official" SSL radio protocol (command)
from protobuf import grSim_Packet_pb2 as pbGrSim
from UDPHelper import * #Udp functions
import UDPHelper

import socket
import time

class RobotData(object):
	def __init__(self, id=0, velocity=(0.0,0.0,0.0), kick=0.0, chip=0.0, dribble=0.0, yellow=False):
		#Network parameters
		self.address = None
		
		#Robot parameters (official)
		self.id = id
		self.velocity = velocity
		self.kick = kick
		self.chip = chip
		self.dribble = dribble
		
		#Robot parameters (extra)
		self.yellow = yellow
		
	def setAddress(self, addr):
		self.address = addr
				
	def getAddress(self):
		return self.address
	
	def clearAddress(self):
		self.address = None
	
	def setId(self, id):
		self.id = id
		
	def getId(self):
		return self.id
		
	def setVelocity(self, v):
		self.velocity = v
	
	def getVelocity(self):
		return self.velocity
	
	def setKick(self, k):
		self.kick = k
	
	def getKick(self):
		return self.kick
	
	def setChip(self, c):
		self.chip = c
		
	def getChip(self):
		return self.chip
	
	def setDribble(self, d):
		self.dribble = d
	
	def getDribble(self):
		return self.dribble
	
	def setYellow(self, y):
		self.yellow = y
	
	def getYellow(self):
		return self.yellow
		

class RobotCommunication(object):
	# Public functions
	def __init__(self):
		# SSH robot protocol
		self.sshSocket			= None
		self.sshListening		= False
		self.sshPort			= 10001
		
		# Official robot protocol
		self.officialSocket		= None
		self.officialListening	= False
		self.officialPort		= 10010
		
		# Grsim robot protocol
		self.grsimSocket		= None
		self.grsimListening		= False
		self.grsimPort			= 20011
				
	def receive(self, style, blocking=False):
		if style=="ssh":
			#SmallSizeHolland protocol
			self.__setSshBlocking(blocking)
			return self.__receiveSshCommands()
		elif style=="grsim":
			#Grsim protocol
			self.__setGrsimBlocking(blocking)
			return self.__receiveGrsimCommands()
		elif style=="official":
			#Official protocol
			self.__setOfficialBlocking(blocking)
			return self.__receiveOfficialCommands()
		else:
			print("Fatal error: Invalid protocol style "+style+".")
			print("Supported styles are 'ssh', 'grsim' and 'official'.")
			exit(1)
			
	def send(self, style, robots):
		if style=="ssh":
			#SmallSizeHolland protocol
			return self.__sendSshCommands(robots)
		elif style=="grsim":
			#Grsim protocol
			return self.__sendGrsimCommands(robots)
		elif style=="official":
			#Official protocol
			return self.__sendOfficialCommands(robots)
		else:
			print("Fatal error: Invalid protocol style "+style+".")
			print("Supported styles are 'ssh', 'grsim' and 'official'.")
			exit(1)
	
	# SSH robot protocol
	def __getSshSocket(self, listen=False):
		if self.sshSocket is None:
			self.sshSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sshSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Allow multiple applications to bind the port
			self.sshSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #Enable broadcasting
			self.sshSocket.setblocking(False) #Set non-blocking
		if listen and not self.sshListening:
			self.sshListening = True
			self.sshSocket.bind(('0.0.0.0', self.sshPort))
		return self.sshSocket
	
	def __setSshBlocking(self, blocking):
		self.__getSshSocket(False).setblocking(blocking)
			
	def __receiveSshCommands(self):
		sock = self.__getSshSocket(True)
		robots = []
		try:
			data, addr = sock.recvfrom(4096)
			cmd = pbRobotSsh.Command()
			cmd.ParseFromString(data)
			if not cmd is None:
				robot = RobotData()
				robot.setAddress(addr)
				robot.setId(cmd.id)
				robot.setVelocity((cmd.move.x, cmd.move.y, cmd.move.r))
				robot.setKick(cmd.action.kick)
				robot.setChip(cmd.action.chip)
				robot.setDribble(cmd.action.dribble)
				robots.append(robot)
		except socket.error:
			pass
		return robots
	
	def __sendSshCommands(self, robots):
		for robot in robots:
			sock = self.__getSshSocket(False)
			cmd = pbRobotSsh.Command()
			cmd.id = robot.id
			velocity = robot.getVelocity()
			cmd.move.x = velocity[0]
			cmd.move.y = velocity[1]
			cmd.move.r = velocity[2]
			cmd.action.kick = robot.getKick()
			cmd.action.chip = robot.getChip()
			cmd.action.dribble = robot.getDribble()
			data = cmd.SerializeToString()
			if robot.address is None:
				robot.address = ('255.255.255.255',self.sshPort)
			sock.sendto(data, robot.address)

	# Official robot protocol

	def __getOfficialSocket(self, listen=False):
		if self.officialSocket is None:
			self.officialSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.officialSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Allow multiple applications to bind the port
			self.officialSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #Enable broadcasting
			self.officialSocket.setblocking(False) #Set non-blocking
		if listen and not self.officialListening:
			self.officialListening = True
			self.officialSocket.bind(('0.0.0.0', self.officialPort))
		return self.officialSocket
	
	def __setOfficialBlocking(self, blocking):
		self.__getOfficialSocket(False).setblocking(blocking)
					
	def __receiveOfficialCommands(self):
		sock = self.__getOfficialSocket(True)
		robots = []
		try:
			data, addr = sock.recvfrom(4096)
			wrapper = pbRobotOfficialWrapper.RadioProtocolWrapper()
			wrapper.ParseFromString(data)
			for data in wrapper.command:
				robot = RobotData()
				robot.setAddress(addr)
				robot.setId(data.robot_id)
				robot.setVelocity(data.velocity_x, data.velocity_y, data.velocity_r)
				robot.setKick(data.flat_kick)
				robot.setChip(data.chip_kick)
				robot.setDribble(data.dribbler_spin)
				robots.append(robot)
		except socket.error:
			pass
		return robots
	
	def __sendOfficialCommands(self, robots):
		sock = self.__getOfficialSocket(False)
		for robot in robots:
			wrapper = pbRobotOfficialWrapper.RadioProtocolWrapper()
			cmd = wrapper.command.add()
			cmd.robot_id = robot.getId()
			velocity = robot.getVelocity()
			cmd.velocity_x = velocity[0]
			cmd.velocity_y = velocity[1]
			cmd.velocity_r = velocity[2]
			cmd.flat_kick = robot.getKick()
			cmd.chip_kick = robot.getChip()
			cmd.dribbler_spin = robot.getDribble()
			data = wrapper.SerializeToString()
			if robot.address is None: #Broadcast
				robot.address = ('255.255.255.255', self.officialPort)
			sock.sendto(data, robot.address)
	
	# Grsim robot protocol
	
	def __getGrsimSocket(self, listen):
		if self.grsimSocket is None:
			self.grsimSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.grsimSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Allow multiple applications to bind the port
			self.grsimSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #Enable broadcasting
			self.grsimSocket.setblocking(False) #Set non-blocking
		if listen and not self.grsimListening:
			self.grsimListening = True
			self.grsimSocket.bind(('0.0.0.0', self.grsimPort))
		return self.grsimSocket
		
	def __setGrsimBlocking(self, blocking):
		self.__getGrsimSocket(False).setblocking(blocking)
	
	def __receiveGrsimCommands(self):
		sock = self.__getGrsimSocket(True)
		robots = []
		try:
			data, addr = sock.recvfrom(4096)
			packet = pbGrSim.grSim_Packet()
			packet.ParseFromString(data)
			for cmd in packet.commands.robot_commands:
				robot = RobotData()
				robot.setId(cmd.id)
				robot.setVelocity(cmd.veltangent, cmd.velnormal, cmd.velangular)
				robot.setKick(cmd.kickspeedx)
				robot.setChip(cmd.chipspeedz)
				dribble = 0.0
				if cmd.spinner:
					dribble = 1.0
				robot.setDribble(dribble)
				robot.setAddress(addr)
				robot.setYellow(packet.commands.isteamyellow)
				robots.append(robot)
		except socket.error:
			pass			
		return robots
	
	def __sendGrsimCommands(self, robots):
		sock = self.__getGrsimSocket(False)
		packet = pbGrSim.grSim_Packet()
		for robot in robots:
			packet.commands.timestamp = time.time()
			packet.commands.isteamyellow = robot.getYellow()
			command = packet.commands.robot_commands.add()
			command.id = robot.getId()
			velocity = robot.getVelocity()
			command.veltangent = velocity[0]
			command.velnormal = velocity[1]
			command.velangular = velocity[2]
			command.kickspeedx = robot.getKick()
			command.kickspeedz = robot.getChip()
			dBool = False
			if (robot.getDribble()>0.00):
				dBool = True
			command.spinner = dBool
			command.wheelsspeed = 0
			data = packet.SerializeToString()
			if robot.address is None: #Broadcast
				robot.address = ('255.255.255.255',self.grsimPort)
			sock.sendto(data, robot.address)
	






### OLD FUNCTIONS
def robotReceiveCommand(sock):
	### Waits for data, then decodes and returns it
	data = receive(sock)
	cmd = pbRobotSsh.Command()
	cmd.ParseFromString(data)
	return cmd

def robotBroadcastCommand(sock,id,x,y,r,k,c,d):
	### Broadcasts a command to all robots
	cmd = pbRobotSsh.Command()
	cmd.id = id #Robot identifier
	cmd.move.x = x	#Desired forward drive velocity in m/s
	cmd.move.y = y	#Desired left drive velocity in m/s
	cmd.move.r = r	#Desired angular velocity in rad/s
	cmd.action.kick = k	#Desired flat kick speed in m/s
	cmd.action.chip = c	#Desired chip kick speed in m/s
	cmd.action.dribble = d #Dribbler spin, from -1 to 1, where -1 is the maximum reverse spin, and +1 is the maximum forward-spin
	broadcast(sock, cmd.SerializeToString())

### COMMUNICATION WITH OFFICIAL ROBOTS
def officialRobotReceiveCommands(sock): #Yes, commands: a list
	### Waits for a set of commands following official specs to be received, then decodes it and returns it
	data = receive(sock)
	wrapper = pbRobotOfficialWrapper.RadioProtocolWrapper()
	wrapper.ParseFromString(data)
	return wrapper.command

def officialRobotTransmitCommand(sock,server,port,id,x,y,r,k,c,d):
	### Sends a command following official specs to a specified server
	wrapper = pbRobotOfficialWrapper.RadioProtocolWrapper()
	cmd = wrapper.command.add()
	cmd.robot_id = id
	cmd.velocity_x = x
	cmd.velocity_y = y
	cmd.velocity_r = r
	cmd.flat_kick = k
	cmd.chip_kick = c
	cmd.dribbler_spin = d
	data = wrapper.SerializeToString()
	transmit(sock,server,port,data)

### COMMUNICATION WITH GRSIM
def grSimSendCommand(sock,server,port,yellow,id,x,y,r,k,c,d):
	packet = pbGrSim.grSim_Packet()
	packet.commands.timestamp = time.time()
	packet.commands.isteamyellow = yellow
	command = packet.commands.robot_commands.add()
	command.id = id
	command.kickspeedx = k
	command.kickspeedz = c
	command.veltangent = x
	command.velnormal = y
	command.velangular = r
	dBool = False
	if (d>0.00):
		dBool = True
	command.spinner = dBool
	command.wheelsspeed = 0
	data = packet.SerializeToString()
	transmit(sock,server,port,data)
