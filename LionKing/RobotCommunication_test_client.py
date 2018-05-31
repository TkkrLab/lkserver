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

robotSocket = RobotCommunication.createRobotSocket()

print("Started.")
while True:
    cmd = RobotCommunication.robotReceiveCommand(robotSocket)
    print( str(cmd.id)+": "+
		  "X="+str(cmd.move.x)+" m/s "+
		  "Y="+str(cmd.move.y)+" m/s "+
		  "R="+str(cmd.move.r)+" rad/s "+
		  "K="+str(cmd.action.kick)+" m/s "+
		  "C="+str(cmd.action.chip)+" m/s "+
		  "D="+str(round(cmd.action.dribble*100))+"%"
		 )
