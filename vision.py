# This program receives all geometry and detection data from ssl-vision
# and displays it graphically

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

from LionKing.VisionClient import *
import os
import sys
import time
import pygame
from pygame.locals import *
from math import pi

COLOR_BACKGROUND = 0,0,0
COLOR_FIELD = 90,255,61
COLOR_BOUNDARY = 62,175,42
COLOR_GOAL = 22,202,218
COLOR_LINE = 255,255,255
COLOR_ARC = 255,255,255
COLOR_ROBOT_BLUE = 0,0,255
COLOR_ROBOT_YELLOW = 204,198,12
COLOR_BALLS = 255,170,0
COLOR_ESTBALL = 255,0,255

pygame.font.init()
FONT = pygame.font.Font(None, 18)
	
def scaleField(size, field):
	total_width = field.boundary_width*2+field.field_width
	total_height = field.boundary_width*2+field.field_length
	xscale = float(size[0])/float(total_width)
	yscale = float(size[1])/float(total_height)
	if (yscale<xscale):
		xscale=yscale
	return xscale

def drawField(screen, field, scale):
	global COLOR_FIELD, COLOR_BOUNDARY, COLOR_GOAL, COLOR_LINE, COLOR_ARC
	
	# Boundary
	boundary_width = field.boundary_width*scale
	boundary_height = field.boundary_width*scale
	
	# Field
	field_width = field.field_width*scale
	field_height = field.field_length*scale
	
	# Goal
	goal_width = field.goal_width*scale
	goal_height = field.goal_depth*scale
	
	# Field location
	field_location = boundary_width, boundary_height, field_width, field_height
	
	# Boundary locations
	boundary1_location = 0, 0, boundary_width*2+field_width, boundary_height
	boundary2_location = 0, 0, boundary_width, boundary_height*2+field_height
	boundary3_location = 0, boundary_height+field_height-1, boundary_width*2+field_width, boundary_height+2
	boundary4_location = boundary_width+field_width-1, 0, boundary_width+2, boundary_height*2+field_height
	
	# Goal locations
	goal1_location = boundary_width+(field_width/2)-(goal_width/2),boundary_height-goal_height,goal_width,goal_height
	goal2_location = boundary_width+(field_width/2)-(goal_width/2),boundary_height+field_height-1,goal_width,goal_height
	
	# Draw static elements
	pygame.draw.rect(screen, COLOR_FIELD, field_location,0) #Field
	pygame.draw.rect(screen, COLOR_BOUNDARY, boundary1_location,0) #Boundary 1
	pygame.draw.rect(screen, COLOR_BOUNDARY, boundary2_location,0) #Boundary 2
	pygame.draw.rect(screen, COLOR_BOUNDARY, boundary3_location,0) #Boundary 3
	pygame.draw.rect(screen, COLOR_BOUNDARY, boundary4_location,0) #Boundary 4
	pygame.draw.rect(screen, COLOR_GOAL, goal1_location, 0) # Goal 1
	pygame.draw.rect(screen, COLOR_GOAL, goal2_location, 0) # Goal 2
	
	#Lines
	for field_line in field.field_lines:
		point_a = [field_line.p1.y*scale+field_width/2.0+boundary_width,field_line.p1.x*scale+field_height/2.0+boundary_height]
		point_b = [field_line.p2.y*scale+field_width/2.0+boundary_width,field_line.p2.x*scale+field_height/2.0+boundary_height]
		line_width = field_line.thickness*scale
		line_height =field_line.thickness*scale
		
		#print(field_line.name+": "+str(point_a[0])+", "+str(point_a[1])+", "+str(point_b[0])+", "+str(point_b[1]))
				
		if (point_a[0]==point_b[0]):
			point_a[0] -= line_width/2.0;
			point_b[0] += line_width/2.0;
			
		if (point_a[1]==point_b[1]):
			point_a[1] -= line_height/2.0;
			point_b[1] += line_height/2.0;
			
		line_location = point_a[0],point_a[1],point_b[0]-point_a[0],point_b[1]-point_a[1]
				
		pygame.draw.rect(screen, COLOR_LINE, line_location, 0)
		
	#Arcs
	for field_arc in field.field_arcs:
		center = [field_arc.center.y*scale+field_width/2.0+boundary_width,field_arc.center.x*scale+field_height/2.0+boundary_height]
		radius = field_arc.radius*scale
		arc_location = center[0]-radius,center[1]-radius,radius*2,radius*2
		
		start_angle = field_arc.a1 -pi/2
		end_angle = field_arc.a2 -pi/2
		width = int(field_arc.thickness*scale)
		if width<1:
			width = 1
		
		pygame.draw.arc(screen, COLOR_ARC, arc_location, start_angle, end_angle, width)
	
def drawRobots(screen, robots, field, color, scale, team):
	global FONT
		
	boundary_width = field.boundary_width*scale
	boundary_height = field.boundary_width*scale
	field_width = field.field_width*scale
	field_height = field.field_length*scale
	
	# Robots
	for i in range(0, len(robots)):
		pos_x = robots[i].y*scale + boundary_width + field_width/2
		pos_y = robots[i].x*scale + boundary_height + field_height/2
		pos_r = robots[i].orientation
		location = int(pos_x),int(pos_y)
		label_location = int(pos_x-4),int(pos_y-5)
		start_angle = pos_r-(pi/8)-pi/2
		end_angle = pos_r+(pi/8)-pi/2
		box = int(pos_x)-8,int(pos_y)-8,16,16
		if robots[i].renzesConfidence>0:
			pygame.draw.circle(screen, color, location, 8,0)
		else:
			pygame.draw.circle(screen, (40,40,40), location, 8,0)
		pygame.draw.arc(screen, (255,0,0), box, start_angle, end_angle, 3)
		label = FONT.render(str(i), 1, (255,255,255))
		screen.blit(label, label_location)
	
def drawBalls(screen, balls, field, color, scale):
	for i in range(0, len(balls)):
		ball = balls[i]
		location = ball.x, ball.y, ball.confidence
		drawBall(screen, location, field, color, scale)
		
def drawBall(screen, location, field, color, scale):
	boundary_width = field.boundary_width*scale
	boundary_height = field.boundary_width*scale
	field_width = field.field_width*scale
	field_height = field.field_length*scale
	pos_x = location[1]*scale + boundary_width + field_width/2
	pos_y = location[0]*scale + boundary_height + field_height/2
	label_location = int(pos_x-2),int(pos_y-2)
	pygame.draw.circle(screen, color, (int(pos_x),int(pos_y)), 5,0)
	start_angle = 0-pi/2
	end_angle = (location[2]*2*pi)-pi/2
	box = int(pos_x)-5,int(pos_y)-5,10,10
	pygame.draw.arc(screen, (255,0,0), box, start_angle, end_angle, 3)

def main():
	visionClient = VisionClient()
	
	clock = pygame.time.Clock()
	size = width, height = 548, 800
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption("SmallSizeHolland visual monitor")
	pygame.init()
	
	global COLOR_BACKGROUND
	global COLOR_ROBOT_BLUE
	global COLOR_ROBOT_YELLOW
	global COLOR_BALLS
	global COLOR_ESTBALL
	
	scale = 1
		
	running=True
	while running:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.display.quit()
				sys.exit(0)
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				pygame.display.quit()
				sys.exit(0)
		if visionClient.update():
			screen.fill(COLOR_BACKGROUND)
			field = visionClient.getRawField()
			if not field is None:
				scale = scaleField(size, field)
				drawField(screen, field, scale)
				blueRobots = visionClient.getRobots(False)
				yellowRobots = visionClient.getRobots(True)
				balls = visionClient.getBalls()
				estimatedBallLocation = visionClient.getEstimatedBallLocation()
				if len(blueRobots)>0:
					drawRobots(screen, blueRobots, field, COLOR_ROBOT_BLUE, scale, "Blue")
				if len(yellowRobots)>0:
					drawRobots(screen, yellowRobots, field, COLOR_ROBOT_YELLOW, scale, "Yellow")
				if len(balls)>0:
					drawBalls(screen, balls, field, COLOR_BALLS, scale)
				if not estimatedBallLocation is None:
					drawBall(screen, estimatedBallLocation, field, COLOR_ESTBALL, scale)
				
			pygame.display.flip()
			#print(str(clock.get_fps()))
			clock.tick(240)

if __name__ == "__main__":
	main()
