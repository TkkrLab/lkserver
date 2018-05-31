# Simple translation program following the specifications described
# in the shared protocol challenge document of Robocup 2015
# Allows us to control robots from other teams

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
import time

robotSocket = LionKing.createRobotSocket()
socket = LionKing.createUdpSocket()

print("Started.")
while True:
	cmd = LionKing.robotReceiveCommand(robotSocket)
	print( str(cmd.id)+": "+
		  "X="+str(cmd.move.x)+" m/s "+
		  "Y="+str(cmd.move.y)+" m/s "+
		  "R="+str(cmd.move.r)+" rad/s "+
		  "K="+str(cmd.action.kick)+" m/s "+
		  "C="+str(cmd.action.chip)+" m/s "+
		  "D="+str(round(cmd.action.dribble*100))+"%"
		 )
	LionKing.officialRobotTransmitCommand(socket,'127.0.0.1', 10010, cmd.id, cmd.move.x, cmd.move.y, cmd.move.r, cmd.action.kick, cmd.action.chip, cmd.action.dribble)
