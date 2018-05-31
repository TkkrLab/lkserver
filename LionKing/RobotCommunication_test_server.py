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

import RobotCommunication
import time

# Simple server that controls our robots

serverSocket = RobotCommunication.createServerSocket()
	
counter = 0

RobotCommunication.robotBroadcastCommand(serverSocket, 1, 0, 0, 2, 0, 0, 0)

while 1:
	print("Sending message #"+str(counter)+"...")
	RobotCommunication.robotBroadcastCommand(serverSocket, 0, 2, 0, 0, 0, 0, 0)
	#(socket, robot id, x, y, r, kick, chip, dribbler)
	# With this example robot should rotate with 0.5 rad/s
	time.sleep(0.05)
	counter+=1
