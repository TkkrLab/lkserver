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

import LionKing.UDPHelper as UDPHelper
import LionKing.RobotCommunication as RobotCommunication
from LionKing.VisionClient import VisionClient
from LionKing.MovementController import MovementController
import os
import sys
import time

import math

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import spline

def plot(time_list,feedback_list,target_list):
	plt.plot(time_list, target_list)
	plt.plot(time_list, feedback_list)
	plt.xlim((0, len(time_list)))
	plt.ylim((min(feedback_list)-100, max(feedback_list)+100))
	plt.xlabel('time (s)')
	plt.ylabel('')
	plt.title('Result')
	plt.grid(True)
	plt.show()
	
def main():
	serverSocket = UDPHelper.createServerSocket()
	visionClient = VisionClient()
	movementController = MovementController()
	
	#This sets the speed limits:
	movementController.setMaxVelocity(4.0,4.0,1.0*math.pi)
	
	#This is used to make the robot face towards the ball (not important):
	movementController.setAngleVelocityMultiplier(2)
	
	#This sets the PID values for the controller:
	movementController.configureXY(0.25,0.2,0.02)
	movementController.configureR(0.0,0.0,0.0)
	
	movementController.ilimit(100.0)
		
	#The robot:
	myRobotId = 0
	
	#Stop when done:
	doneWhenRmsLowerThan = 100 #RMS of XY error needs to be lower than this value
	
	#The target is always the ball
	
	previousTarget = 0.0, 0.0, 0.0
	
	target = 0.0, 0.0, 0.0
	
	movementController.move(target,0)
	
	time_list = []
	feedback_list = []
	target_list = []
	counter = 0
	
	followBall = False # Enable to follow ball, disable to test PID
	
	timeDone = time.time()+20 #20 seconds
			
	while 1:
		if visionClient.update():
			field = visionClient.getRawField()
			
			if not field is None:			
				blueRobots = visionClient.getRobots(False)
				
				myCurrentX = 0.0
				myCurrentY = 0.0
				myCurrentR = 0.0
				
				targetR = 0.0
				
				robotVisible = False
				
				for robot in blueRobots:
					if robot.id == myRobotId: #It's the robot we are controlling!
						myCurrentX = robot.x
						myCurrentY = robot.y
						myCurrentR = robot.orientation
						robotVisible = True
					
				balls = visionClient.getBalls()
				estimatedBallLocation = visionClient.getEstimatedBallLocation()
				
				if not estimatedBallLocation is None:
					if followBall:
						target = estimatedBallLocation[0], estimatedBallLocation[1], myCurrentR
						if (round(target[0],1) != round(previousTarget[0],1)) or (round(target[1],1) != round(previousTarget[1],1)):
							#if (len(feedback_list)>0):
							#	plot(time_list,feedback_list,target_list)
							time_list = []
							feedback_list = []
							target_list = []
							counter = 0
							previousTarget = target
							movementController.move(target,0)
							print("Target updated",target)
								
				if not followBall and (time.time()>timeDone):
					plot(time_list,feedback_list,target_list)
					exit(0)
					
				rms = movementController.getErrorRMS()
				velocity = movementController.step((myCurrentX,myCurrentY,myCurrentR))
							
				if followBall:
					if rms < doneWhenRmsLowerThan:
						print("Done ("+str(rms)+")")
						velocity = 0.0,0.0,0.0
					else:
						if not robotVisible:
							print("Robot not visible!")
							velocity = 0.0,0.0,0.0
						
				if followBall:
					movementController.setTargetAngle(movementController.angleError)

				
				time_list.append(counter)
				target_list.append(movementController.pid[0].targetValue)
				feedback_list.append(myCurrentX)
				
				RobotCommunication.robotBroadcastCommand(serverSocket, myRobotId, velocity[0], velocity[1], velocity[2], 0, 0, 0)
				
				counter+=1
				
				#RobotCommunication.robotBroadcastCommand(serverSocket, myRobotId, velocity[0], 0, 0, 0, 0, 0)
				#print("X",velocity[0])
				
				#print("Velocity and state",round(velocity[0],2),round(velocity[1],2),round(velocity[2],2),round(movementController.getTimeLeft(),2),movementController.getExceeded(),movementController.angleError)

if __name__ == "__main__":
	main()
