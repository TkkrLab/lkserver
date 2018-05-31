# This library helps with parsing packets from ssl-vision

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

from UDPHelper import *
from protobuf import messages_robocup_ssl_wrapper_pb2 as pbVisionWrapper

class VisionBall(object):
	def __init__(self):
		pass

class VisionRobot(object):
	id = -1
	rawData = []
	
	x = 0.0
	y = 0.0
	orientation = 0.0
	confidence = 0.0
	
	renzesConfidence = 0
	
	def __init__(self, robot_id):
		self.id = robot_id
	
	def stateReset(self):
		self.rawData = []
		
	
	def stateAdd(self, data):
		self.rawData.append(data)
	
	def stateParse(self):
		newX = 0.0
		newY = 0.0
		newOrientation = 0.0
		
		xyConfidence = 0.0
		orientationConfidence = 0.0
		
		xyCount = 0
		orientationCount = 0
		
		#print("Robot #"+str(self.id)+":")
		for location in self.rawData:
			newX += location.x * location.confidence
			newY += location.y * location.confidence
			xyConfidence += location.confidence
			xyCount += 1
			if location.HasField("orientation"):
				newOrientation += location.orientation * location.confidence
				orientationConfidence += location.confidence
				orientationCount += 1
			
			#print(" - "+str(location.x)+", "+str(location.y))
				
		if xyConfidence > 0.0 and xyCount > 0:
			newX = newX / xyConfidence
			newY = newY / xyConfidence
			self.x = newX
			self.y = newY
			self.renzesConfidence = 100
			#print(" = "+str(newX)+", "+str(newY))
		else:
			if self.renzesConfidence>0:
				self.renzesConfidence -= 1
		if orientationConfidence > 0.0 and orientationCount > 0:
			newOrientation = newOrientation / orientationConfidence
			self.orientation = newOrientation
		
		if len(self.rawData)>0:
			self.confidence = xyConfidence / len(self.rawData)
		else:
			self.confidence = 0.0

class VisionClient(object):
	socket = None			#UDP socket used for receiving data
	fieldData = None		#Raw field data
	calibData = None		#Raw calibration data
	
	cameras = []			#Detection data per camera
	
	robotsBlue = []
	robotsYellow = []
	
	balls = []
	estimatedBallLocation = None
	
	def __init__(self, addr='224.5.23.2', port=10006):
		self.socket = createUdpSocket(addr, port, True, True, False, True, True)
		self.socket.setblocking(False)
		
	def _receivePacket(self):
		data = self.socket.recv(4096)
		wrapper = pbVisionWrapper.SSL_WrapperPacket()
		wrapper.ParseFromString(data)
		return wrapper
		
	def _updateCameras(self, data):
		while len(self.cameras)<(data.camera_id+1):
			self.cameras.append(None)
		if self.cameras[data.camera_id] is None or self.cameras[data.camera_id].frame_number < data.frame_number:
			self.cameras[data.camera_id] = data
			return True
		return False
	
	def _sortRobots(self, state, data):
		for robot in state:
			robot.stateReset()
		for robot in data:
			if robot.HasField("robot_id"):
				while len(state)<(robot.robot_id+1):
					state.append(VisionRobot(len(state)))
				state[robot.robot_id].stateAdd(robot)
		for robot in state:
			robot.stateParse()
		return state
	
	def _updateRobots(self):
		unsortedRobotsBlue = []
		unsortedRobotsYellow = []
		
		for camera in self.cameras:
			if not camera is None:
				for robot in camera.robots_blue:
					unsortedRobotsBlue.append(robot)
				for robot in camera.robots_yellow:
					unsortedRobotsYellow.append(robot)
		
		self.robotsBlue = self._sortRobots(self.robotsBlue, unsortedRobotsBlue)
		self.robotsYellow = self._sortRobots(self.robotsYellow, unsortedRobotsYellow)
		return True #For now always update...
	
	def _updateBalls(self):
		self.balls = []
		
		for camera in self.cameras:
			if not camera is None:
				for ball in camera.balls:
					self.balls.append(ball)
		
		return True
		
	def update(self):
		newFieldData = None
		newCalibData = None
		hasUpdated = False
		
		try:
			visionData = self._receivePacket()
			if visionData.HasField("geometry"):
				newFieldData = visionData.geometry.field
				newCalibData = visionData.geometry.calib
				self.fieldData = newFieldData
				self.calibData = newCalibData
				hasUpdated = True
			if visionData.HasField("detection"):
				if self._updateCameras(visionData.detection):
					haveRobotsUpdated = self._updateRobots()
					haveBallsUpdate = self._updateBalls()
					hasUpdated = haveRobotsUpdated or haveBallsUpdate
		except socket.error:
			return False
		return hasUpdated
	
	def getRawField(self):
		return self.fieldData
	
	def getRawCalib(self):
		return self.calibData
	
	def getRobots(self, yellow=False):
		if yellow:
			return self.robotsYellow
		else:
			return self.robotsBlue
		
	def getRobot(self, robot_id, yellow=False):
		if yellow:
			robots = self.robotsYellow
		#else:
			robots = self.robotsBlue
		if len(robots)<=robot_id:
			return None
		return robots[robot_id]
	
	def getBalls(self):
		return self.balls
	
	def getEstimatedBallLocation(self):
		if len(self.balls)>0:
			avX = 0.0
			avY = 0.0
			totalConfidence = 0.0
			for ball in self.balls:
				avX += ball.x * ball.confidence
				avY += ball.y * ball.confidence
				totalConfidence += ball.confidence
			avX = avX / totalConfidence
			avY = avY / totalConfidence
			avC = totalConfidence / len(self.balls)
			self.estimatedBallLocation = avX,avY,avC
		return self.estimatedBallLocation

#test = VisionClient()
#while True:
#	test.update()
