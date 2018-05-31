# LionKing server (LKserver)
A small server for use with SSL robots written in Python.
Includes a set of tools for converting between different Protobuf formats on-the-fly.

# Requirements
Debian: ```sudo apt-get install python-pygame python-protobuf```

Arch: ```sudo pacman -Sy python2-pygame python2-protobuf```

# Included applications

## grsim.py
```grsim.py``` translates our protocol to that of grSim so that our servers can control virtual robots (works with both LionKing server and Zosma)

## shared_radio_protocol_client.py
```shared_radio_protocol_client.py``` is a simple translation program that converts our protocol to the protocol described in the shared protocol challenge document of Robocup 2015. Allows us to control robots from other teams.

## shared_radio_protocol_server.py
```shared_radio_protocol_servr.py``` is a simple translation program that converts robot commands sent following the specifications described
in the shared protocol challenge document of Robocup 2015 into our robot commands. Allows other teams to control our robots.

## monitor.py
```monitor.py``` displays commands sent to our robots in a nice CLI interface.

## joystick.py
```joystick.py``` allows for testing the robots by using Xbox 360 controllers.
Usage: connect as many controllers as you need, then start the application. The first controller will control robot 0, the second controller robot 1 and so on...

## vision.py
```vision.py``` shows a graphical representation of the field as received from the ```ssl-vision``` server and interpreted by the VisionClient class bundled with LionKing.

## controller_ball_follower.py
```controller_ball_follower.py``` demonstrates the MovementController and VisionClient libraries by following the ball. Work in progress, eats kittens.

## controller_plot.py
```controller_plot.py``` is used to debug the MovementController. It moves the robot only over the X-axis and once the target has been reached the process will display a plot showing the motion over the X-axis. Ment to be used to find initial PID values manually.

# Libraries

## RobotCommunication
### RobotData
RobotData is a class ment to be an universal container for robot command data.

| Function     | Arguments                                   | Units                                                      | Description                                          |
|--------------|---------------------------------------------|------------------------------------------------------------|------------------------------------------------------|
| (init)       | id, velocity, kick, chip, dribble, yellow   | integer, (m/s, m/s, rad/s), m/s, m/s, -1.0 to 1.0, boolean | Creation of the object (all parameters are optional) |
| setAddress   | (ip, port)                                  | (IP address, port)                                         | Set the address of the robot as tuple                |
| getAddress   |                                             |                                                            | Get the address of the robot as tuple                |
| clearAddress |                                             |                                                            | Clears the address of the robot (to broadcast)       |
| setId        | id                                          | integer                                                    | Set the robot identification number                  |
| getId        |                                             |                                                            | Get the robot identification number                  |
| setVelocity  | (velocity_x, velocity_y, velocity_r)        | (m/s, m/s, rad/s)                                          | Set the robot velocity as tuple                      |
| getVelocity  |                                             |                                                            | Get the robot velocity as tuple                      |
| setKick      | kick                                        | m/s                                                        | Set the kicking speed                                |
| getKick      |                                             |                                                            | Get the kicking speed                                |
| setChip      | chip                                        | m/s                                                        | Set the chipping speed                               |
| getChip      |                                             |                                                            | Get the chipping speed                               |
| setDribble   | dribble                                     | -1.0 to 1.0                                                | Set the dribbler speed                               |
| getDribble   |                                             |                                                            | Get the dribbler speed                               |

### RobotCommunication
RobotCommuncation is a class defining functions for sending or receiving data from robots in various formats

| Function     | Arguments                                   | Units                                                      | Description                                          |
|--------------|---------------------------------------------|------------------------------------------------------------|------------------------------------------------------|
| (init)       |                                             |                                                            | Creation of the object                               |
| receive      | style, blocking                             | style, boolean                                             | Receive data: returns list of RobotData objects      |
| send         | style, data                                 | style, list of RobotData objects                           | Transmit data: sends list of RobotData objects       |

The following formats (styles) are supported:

| Style    | Description                                |
|----------|--------------------------------------------|
| ssh      | The SmallSizeHolland robot protobuf format |
| official | The official robot protobuf format         |
| grsim    | The Grsim robot protobuf format            |

## UDPHelper (depricated)
A simple abstraction layer for easy use of UDP sockets in Python.

## VisionClient
A library implementing a full client for ```ssl-vision```. Currently uses weighted averaging to determine locations.

## PIDController
A full implementation of the PID controller algorythm in Python.

## MovementController
A class that implements the controller which translates requests to move to a certain coordinate into velocities, using a PID controller.

## Path
A class that provides pathfinding functionality.

# License

LionKing - Copyright 2018 Renze Nicolai

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
