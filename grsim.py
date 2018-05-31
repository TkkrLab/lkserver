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

from LionKing.RobotCommunication import *
import time
import sys

# Translation program that forwards robot commands to grSimSendCommand

isTeamYellow = False #Set to true to be team yellow

if len(sys.argv)!=2:
	print("Usage: "+sys.argv[0]+" <team: blue or yellow>")
	exit()
	
if (sys.argv[1]=="yellow"):
	isTeamYellow = True

if isTeamYellow:
	print("Yellow!")
else:
	print("Blue!")

comm = RobotCommunication()
receiveAddress = ('127.0.0.1', comm.grsimPort)

while True:
	robotData = comm.receive("ssh", True)
	if (len(robotData)>0):
		for i in range(0,len(robotData)):
			robotData[i].setYellow(isTeamYellow)
			print( str(robotData[i].getId())+": "+
			"X="+str(robotData[i].getVelocity()[0])+" m/s "+
			"Y="+str(robotData[i].getVelocity()[1])+" m/s "+
			"R="+str(robotData[i].getVelocity()[2])+" rad/s "+
			"K="+str(robotData[i].getKick())+" m/s "+
			"C="+str(robotData[i].getChip())+" m/s "+
			"D="+str(round(robotData[i].getDribble()*100))+"%"
			)
			robotData[i].setAddress(receiveAddress)
		comm.send("grsim", robotData)
