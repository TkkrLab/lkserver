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
import time, datetime

comm = RobotCommunication()

state = [None]*8

def update():
	global state
	global robotLastSeen
	data = comm.receive("ssh", False)
	if len(data)<1:
		return False
	for robot in data:
		while len(state) <= robot.getId():
			state.append(None)
		state[robot.getId()] = (time.time(), robot)
	return True
	
def display():
	global state
	now = time.time()
	nowstr = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
	print(u"\u001b[0;0H\u001b[1;43;44m\u001b[0;0KSmallSizeHolland - Robot data monitor - "+nowstr+u"\u001b[0;37;40m") # Header
	print(u"ID | STATUS  | V forward | V left    | V Rotation  | Kicker    | Chipper   | Dribbler |")
	print(u"---|---------|-----------|-----------|-------------|-----------|-----------|----------|")
	for i in range(0,len(state)):
		data = state[i]
		if (data == None):
			line = u"\u001b[0;33;40mUNKNOWN"
			info = u"          |           |             |           |           |          |"
		else:
			(lastSeen, robot) = data
			if lastSeen < (now - 2):
				line = u"\u001b[5;31;40mOFFLINE"
			else:
				line = u"\u001b[0;32;40mRUNNING"
			velocity = robot.getVelocity()
			info = (
				u""+"{:5.2f}".format(velocity[0])+" m/s | "+
				u""+"{:5.2f}".format(velocity[1])+" m/s | "+
				u""+"{:5.2f}".format(velocity[2])+" rad/s | "+
				u""+"{:5.2f}".format(robot.getKick())+" m/s | "+
				u""+"{:5.2f}".format(robot.getChip())+" m/s | "+
				u""+"{:7.2f}".format(robot.getDribble()*100)+"% |")
			
		print(u"\u001b[K"+format(i, '02d')+" | "+line+u"\u001b[0;37;40m | "+info)

def main():
	print(u"\u001b[2J")
	while True:
		while update():
			pass
		display()
		time.sleep(0.01)

if __name__ == "__main__":
	main()
