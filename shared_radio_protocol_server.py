# Simple translation program following the specifications described
# in the shared protocol challenge document of Robocup 2015
# Allows other teams to control our robots
# http://wiki.robocup.org/Small_Size_League/RoboCup_2015/Technical_Challenges

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

import LionKing

rstSocket = LionKing.createRobotSocket(10010)	#Socket for receiving shared radio protocol commands
serverSocket = LionKing.createServerSocket()		#Socket for broadcasting SSH robot commands

print("Started.")
while True:
    officialCommands = LionKing.officialRobotReceiveCommands(rstSocket) #Receive commands...
    for command in officialCommands: #... and each command...
		id = command.robot_id
		x = command.velocity_x		#Desired forward drive velocity in m/s
		y = command.velocity_y		#Desired left drive velocity in m/s
		r = command.velocity_r		#Desired angular velocity in rad/s
		k = command.flat_kick		#(optional) Desired flat kick speed in m/s
		c = command.chip_kick		#(optional) Desired chip kick speed in m/s
		d = command.dribbler_spin	#(optional) Dribbler spin, from -1 to 1, where -1 is the maximum reverse spin, and +1 is the maximum forward-spin
		
		# Random hint: optional fields of type float default to 0.00
		
		print( str(id)+": "+
		  "X="+str(x)+" m/s "+
		  "Y="+str(y)+" m/s "+
		  "R="+str(r)+" rad/s "+
		  "K="+str(k)+" m/s "+
		  "C="+str(c)+" m/s "+
		  "D="+str(round(d*100))+"%"
		 )
		LionKing.robotBroadcastCommand(serverSocket,id,x,y,r,k,c,d) #...is sent to our robots!
