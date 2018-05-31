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

class PIDController(object):
	def __init__(self,P=1.0,I=0.0,D=0.0):
		self.Kp = P
		self.Ki = I
		self.Kd = D
		self.limitI = 20.0
		self.debug = False
		self.reset()
	
	def setDebug(self, d):
		self.debug = d
	
	def setKp(self, p):
		self.Kp = p
	
	def setKi(self, i):
		self.Ki = i
	
	def setKd(self, d):
		self.Kd = d
		
	def setLimitI(self, m):
		self.maxI = m
		
	def setTarget(self, target):
		self.targetValue = target
	
	def reset(self):
		self.previousValue = 0.0
		self.currentValue = 0.0
		self.targetValue = 0.0
		
		self.currentTime = time.time()
		self.previousTime = self.currentTime
		
		self.currentError = 0.0
		self.previousError = 0.0
						
		self.stateP = 0.0
		self.stateI = 0.0
		self.stateD = 0.0
		
		self.result = 0.0
				
	def step(self, value):
		self.previousValue = self.currentValue
		self.currentValue = value
		
		self.previousTime = self.currentTime
		self.currentTime = time.time()
		
		self.previousError = self.currentError
		self.currentError = self.targetValue - self.currentValue
		
		deltaTime = (self.currentTime - self.previousTime)
		deltaError = self.currentError - self.previousError
		
		self.stateP = self.currentError
		self.stateI += self.currentError * deltaTime
		if self.stateI < -self.limitI:
			self.stateI = -self.limitI
			#print("stateI limited MIN")
		if self.stateI > self.limitI:
			self.stateI = self.limitI
			#print("stateI limited MAX")
		self.stateD = 0.0
		if deltaTime != 0:
			self.stateD = deltaError / deltaTime
		else:
			print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		self.result = (self.Kp * self.stateP) + (self.Ki * self.stateI) + (self.Kd * self.stateD)
		#print("DSTATE",deltaError,deltaTime,self.Kd,self.stateD)
		if self.debug!=False:
			#print("I", self.Ki, self.stateI, (self.Ki * self.stateI))
			print(self.debug,self.previousError,self.currentError,"D",deltaError, deltaTime, self.stateD)
		
		return self.result
