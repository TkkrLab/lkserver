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

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

class Path(object):
	matrix = []
	matrix_width = 0
	matrix_height = 0
	division = 200
	start_x = 0
	start_y = 0
	end_x = 0
	end_y = 0
	grid = None
	result = None
	runs = 0
	
	def __init__(self, field_width, field_height, div):
		self.division = div
		self.matrix_width = int(field_width/self.division)
		self.matrix_height = int(field_height/self.division)
		self.clear()
	
	def clear(self):
		self.matrix = [[0 for x in range(0,self.matrix_height)] for j in range(0,self.matrix_width)]
	
	def _addPoint(self, point_x, point_y, t=1):
		if point_x>=0 and point_x<len(self.matrix):
			if point_y>=0 and point_y<len(self.matrix[0]):
				self.matrix[point_x][point_y] = t
	
	def addObject(self, object_x, object_y, around=False):
		matrix_x = int(object_x/self.division)
		matrix_y = int(object_y/self.division)
		self._addPoint(matrix_x, matrix_y)
		
		if around:
			self._addPoint(matrix_x-1, matrix_y)
			self._addPoint(matrix_x, matrix_y-1)
			self._addPoint(matrix_x+1, matrix_y)
			self._addPoint(matrix_x, matrix_y+1)
			self._addPoint(matrix_x-1, matrix_y-1)
			self._addPoint(matrix_x+1, matrix_y+1)
		
	def setStart(self, sx, sy):
		self.start_x = int(sx/self.division)
		self.start_y = int(sy/self.division)
		
	def setEnd(self, sx, sy):
		self.end_x = int(sx/self.division)
		self.end_y = int(sy/self.division)		
		
	def calculate(self):
		self.grid = Grid(matrix=self.matrix)
		start = self.grid.node(self.start_y, self.start_x)
		end = self.grid.node(self.end_y, self.end_x)
		
		finder = AStarFinder(diagonal_movement=DiagonalMovement.only_when_no_obstacle)
		self.result, self.runs = finder.find_path(start, end, self.grid)
		
		print('operations:', self.runs, 'path length:', len(self.result))	
		
	def getNextWaypoint(self):
		if len(self.result)<1:
			return None
		else:
			l = self.result[len(self.result)-1]
			return l[0]*self.division,l[1]*self.division
		
	def getLastWaypoint(self):
		if len(self.result)<1:
			return None
		else:
			l = self.result[0]
			return l[0]*self.division,l[1]*self.division
	
	def getWaypointCount(self):
		return len(self.result)

	def debug(self):
		return self.grid.grid_str(path=self.result, start=(self.start_x,self.start_y), end=(self.end_x,self.end_y))
