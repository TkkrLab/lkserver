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

import math
import time
from PIDController import *

class MovementController(object):
	def __init__(self,P=1.0,I=0.0,D=0.0):
		self.currentLocation = (0.0, 0.0, 0.0)
		self.targetLocation = (0.0, 0.0, 0.0)
		
		self.pid = ( 
			PIDController(P,I,D),
			PIDController(P,I,D),
			PIDController(P,I,D)
			)
		
		self.pid[0].setDebug("X")
		
		self.currentTime = time.time()
		self.previousTime = self.currentTime
		self.startTime = 0.0
		self.remainingTime = 0.0
		self.exceededTime = False
		
		self.currentError = 0.0
		
		self.velocityMax = [5.0, 5.0, 4*math.pi]
		
		self.angleError = 0.0
		self.angleMultiplier = 1.0
		
		self.IL = 20.0
		
	def setAngleVelocityMultiplier(self, m):
		self.angleMultiplier = m
		
	def setTimeRemaining(self, t):
		self.startTime = time.time()
		self.remainingTime = t
		self.exceededTime = False
	
	def _calcNewVelocity(self):
		currentError = (
				self.pid[0].step(self.currentLocation[0]),
				self.pid[1].step(self.currentLocation[1]),
				self.pid[2].step(self.currentLocation[2])
				)
		
		#print("currentError",currentError)
		
		newVelocityAxisX = currentError[0]/(self.remainingTime*1000)
		newVelocityAxisY = currentError[1]/(self.remainingTime*1000)
		newVelocityR = currentError[2]*self.angleMultiplier #/self.remainingTime
		
		robotAngle = self.currentLocation[2]
		angleError = math.atan2(newVelocityAxisY,newVelocityAxisX)
						
		angle = angleError - robotAngle
		
		self.angleError = angleError
				
		newVelocityX = abs(newVelocityAxisX) * math.cos(angle)
		newVelocityY = abs(newVelocityAxisY) * math.sin(angle)
		
		#print("ErrorAngle",round(angleError,3),round(robotAngle,3),round(angle,3),"Velocity",newVelocityX, newVelocityY)
		
		#newVelocityR = angle/self.remainingTime
		
		#print("currentError",currentError)
		
		if newVelocityX > self.velocityMax[0]:
			print("Warning: X velocity limited",newVelocityX,self.velocityMax[0])
			newVelocityX = self.velocityMax[0]
			
		if newVelocityX < -self.velocityMax[0]:
			print("Warning: X velocity limited",newVelocityX,-self.velocityMax[0])
			newVelocityX = -self.velocityMax[0]	
		
		if newVelocityY > self.velocityMax[1]:
			print("Warning: Y velocity limited",newVelocityY,self.velocityMax[1])
			newVelocityY = self.velocityMax[1]
			
		if newVelocityY < -self.velocityMax[1]:
			print("Warning: Y velocity limited",newVelocityY,-self.velocityMax[1])
			newVelocityY = -self.velocityMax[1]
			
		if newVelocityR > self.velocityMax[2]:
			print("Warning: R velocity limited",newVelocityR,self.velocityMax[2])
			newVelocityR = self.velocityMax[2]
			
		if newVelocityR < -self.velocityMax[2]:
			print("Warning: R velocity limited",newVelocityR,-self.velocityMax[2])
			newVelocityR = -self.velocityMax[2]
			
		return newVelocityX,newVelocityY,newVelocityR
	
	def ilimit(self, val):
		self.IL = val
	
	def getErrorRMS(self):
		le = self.pid[0].result,self.pid[1].result,self.pid[2].result
		return math.sqrt(pow(le[0],2)+pow(le[1],2))
	
	def move(self,newTargetLocation,maxDuration):
		self.targetLocation = newTargetLocation
		self.pid[0].reset()
		self.pid[1].reset()
		self.pid[2].reset()
		self.pid[0].setTarget(self.targetLocation[0])
		self.pid[1].setTarget(self.targetLocation[1])
		self.pid[2].setTarget(self.targetLocation[2])
		self.pid[0].setLimitI(self.IL)
		self.pid[1].setLimitI(self.IL)
		self.startTime = time.time()
		self.remainingTime = maxDuration
		self.exceededTime= False
		self.previousTime = self.startTime
		
	def setTargetAngle(self,angle):
		self.targetLocation = self.targetLocation[0],self.targetLocation[1],angle
		self.pid[2].setTarget(angle)
	
	def configureXY(self, p, i, d):
			self.pid[0].setKp(p)
			self.pid[0].setKi(i)
			self.pid[0].setKd(d)
			self.pid[1].setKp(p)
			self.pid[1].setKi(i)
			self.pid[1].setKd(d)
			
	def configureR(self, p, i, d):
			self.pid[2].setKp(p)
			self.pid[2].setKi(i)
			self.pid[2].setKd(d)
	
	def step(self, newCurrentLocation):
		self.currentLocation = newCurrentLocation
		currentStepTime = time.time()
		timeSinceLastStep = currentStepTime-self.previousTime
		self.previousTime = currentStepTime
		#print("stepTime",timeSinceLastStep)
		self.remainingTime -= timeSinceLastStep
		#print("Time: "+str(self.remainingTime))
		if self.remainingTime < 0.1:
			self.exceededTime= True
			self.remainingTime = 0.1
		return self._calcNewVelocity()
	
	def getTimeLeft(self):
		return self.remainingTime
	
	def getExceeded(self):
		return self.exceededTime
	
	def setMaxVelocity(self,x,y,r):
		self.velocityMax[0] = x
		self.velocityMax[1] = y
		self.velocityMax[2] = r

