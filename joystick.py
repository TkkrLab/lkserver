# Joystick controlled server for our robots
# In this version all values are scaled to reflect actual speeds in m/s and rad/s

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
import pygame, os

comm = RobotCommunication()

#Make pygame work without video output
os.environ['SDL_VIDEODRIVER'] = 'dummy'

clock = pygame.time.Clock()
pygame.init()
pygame.display.set_mode((1,1))
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
	
if (joystick_count<1):
	print("No joysticks found. Stop.")
	exit()

print("Number of joysticks: "+str(joystick_count))

joysticks = [None] * joystick_count
d_hacky_bugfix = [True] * joystick_count #Hack to read corret value from right trigger
kc_hacky_bugfix = [True] * joystick_count #Hack to read correct value from left trigger

for i in range(joystick_count):
	joystick = pygame.joystick.Joystick(i)
	joystick.init()
	print("Joystick #"+str(i)+": "+joystick.get_name())
	
	axis_count = joystick.get_numaxes()
	if (axis_count!=6):
		print("Not an xbox controller (axis: "+str(axis_count)+").")
		continue
	button_count = joystick.get_numbuttons()
	if (button_count!=15):
		print("Not an xbox controller (buttons: "+str(button_count)+").")
		continue
	joysticks[i] = joystick


done=False
while done==False:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done=True
	
	for i in range(joystick_count):
		joysticks[i].init()
		
		multiplierA = 2 #X and Y
		multiplierB = 2 #R
		
		if joysticks[i].get_button(9): #Left stick (FAST)
			multiplierA = 4
		
		if joysticks[i].get_button(10): #Right stick (FAST)
			multiplierB = 4
			
		if joysticks[i].get_button(2): #X (SLOW)
			multiplierA = 0.5
			multiplierB = 0.5
			
		#if joysticks[i].get_button(6): #Back (do not uncomment, dangerous)
		#	multiplierA = 8
		#	multiplierB = 8
				
		#Movement
		x = -joysticks[i].get_axis(1)*multiplierA #Left stick: X (gives values from -1 to 1, so multiplied by 2 for max 18 km/h) FORWARD
		y = -joysticks[i].get_axis(0)*multiplierA #Left stick: Y (gives values from -1 to 1, so multiplied by 2 for max 18 km/h) LEFT
		r = -joysticks[i].get_axis(3)*multiplierB #Right stick: X (gives values from -1 to 1, so multiplied by 2 for max 5 rad/s) ROTATE
		
		# Dead zone for crappy controllers
		if (abs(x)<0.2):
			x = 0;
		if (abs(y)<0.2):
			y = 0;
		if (abs(r)<0.2):
			r = 0;
					
		#Dribbler
		d = (joysticks[i].get_axis(5)+1)/2 #Right trigger (mapped from -1>1 to 0>1)
		
		if (d_hacky_bugfix[i]): #Axis starts at 0.00 but jumps to -1.00 once touched... This prevents the dribbler from starting when the right trigger has not been touched.
			if (d!=0.5): #Not default value
				d_hacky_bugfix[i] = False
			else:
				d = 0
		
		#Kicker / chipper power
		kc_power = ((joysticks[i].get_axis(2)+1)/2)*9 + 1 #Left trigger (gives values from -1 to 1, mapped to be 1 to 10 m/s)
		
		if (kc_hacky_bugfix[i]): #Axis starts at 0.00 but jumps to -1.00 once touched... This prevents the kick/chip power from being too high when the left trigger has not been touched.
			if (kc_power!=0.55): #Not default value
				kc_hacky_bugfix[i] = False
			else:
				kc_power = 0.1
		
		#Kicker
		k = 0
		if (joysticks[i].get_button(0)): #A
			#k = 1
			k = kc_power
			
		#Chipper
		c = 0
		if (joysticks[i].get_button(1)): #B
			c = kc_power
		
		
		print("#"+str(i)+": X="+str(x)+" m/s Y="+str(y)+" m/s R="+str(r)+" rad/s K="+str(k)+" m/s C="+str(c)+" m/s D="+str(round(d*100))+"%")
		
		data = RobotData()
		data.setId(i)
		data.setVelocity((x,y,r))
		data.setKick(k)
		data.setChip(c)
		data.setDribble(d)
		comm.send("ssh",[data])
		
	clock.tick(60)
