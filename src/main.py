#!/usr/bin/env python

import numpy as np
import pygame 
import yaml
from colors import white, slate_gray, black, green
from astar import AStar
from math import sqrt


def pythagoras(a, b):
	return sqrt(a ** 2 + b ** 2 )


def grid2graph(grid): 
	graph = []
	nj, ni = grid.shape	 																# Get size of array
	for j in range(nj):																	# Iterate through rows
		for i in range(ni):																# Iterate through columns
			nb = ni * j + i																# Calculate the number of the node
			pos = (i, j)																# Position of current node
			neighbours = {}																# Initialise dictionary of neighbours
			if grid[j][i] != -1:														# If the node can have neighbours
				for dy in range(-1, 2):													# For all adjacent positions in x direction
					for dx in range(- 1, 2):											# For all adjacent positions in y direction
						x, y = i + dx, j + dy 											# Coordinates of adjacet node
						if 0 <= x < ni and 0 <= y < nj:									# If adjacent node is on in the grid
							if grid[y][x] != -1:										# If the adjacent node can be visited
								if x != i or y != j:									# If the node is not itself
									if grid[j][x] != -1 and grid[y][i] != -1: 			# Check shared adjacent is traversable
										neighbour_nb = ni * y + x						# Work out name of the neighbour
										cost = (grid[j][i] + grid[y][x])/ 2.0			# Cost is the average cost of both nodes
										dist = pythagoras((i - x), (j - y))				# Work out distance from neighbour
										neighbours[str(neighbour_nb)] = dist * cost 	# Add neighbour and cost to the dictionary
			graph.append(Node(nb, pos=pos, neighbours=neighbours))						# Append node to node list
	return graph


class Node(object):

	def __init__(self, nb, pos=(0, 0), neighbours={}, parent=None):
		self.nb = nb
		self.pos = pos
		self.parent = None
		self.status = None
		self.f = 0
		self.g = 0
		self.h = 0
		self.neighbours = neighbours

	def __cmp__(self, other):
		return cmp(self.f, other.f)

	def reset(self):
		self.status = None
		self.parent = None
		self.f = 0
		self.g = 0
		self.h = 0


class AStarGUI(object):

	def __init__(self):
		# Display
		# pygame.init()
		self.size = (1000, 1000)									# Set window size
		self.scale = 2												# Number of cm per pixel
		self.window = pygame.display.set_mode(self.size)			# Initialise window for app	
		self.fps = 50												# Frame rate of app

		# Event set up (keyboard and mouse)						
		self.cur_pos = (0, 0) 										# Initialise mouse position
		self.read_key_dict("src/keyboard.json")							# Get keyboard dictionary (defines keypress events)
		self.init_keys()											# Initialise status of each key (none being pressed)
		self.quit = False											# App will quit when quit is True

		# TODO
		self.world = np.loadtxt("mazes/maze3.csv", delimiter=",")			# Import 2D array from file
		self.buggy_pos = (10, 10) 									# Buggy position (make buggy object)

		self.main()													# Run main

	def read_key_dict(self, json_file):
		# Reads a json file and composes a dictionary of keypresses and their correspoding event ints
		json_data = open(json_file)
		self.key_dict = yaml.safe_load(json_data)					# yaml imports as str, json imports as unicode

	def init_keys(self):
		# Fills the key_status dictionary with keys and their corresponsing status (False)
		self.key_status = {}										# Initialise key_status
		for key in self.key_dict:									# For every key in the dictionary
			self.key_status.update({key: False})					# Add to dictionary and initialises as False

	def event_handler(self):
		# Checks key events and writes to key_status dictionary
		for event in pygame.event.get():							# Get all pygame events
			if event.type == pygame.QUIT:							# If an event is of type quit
				self.quit = True								
			elif event.type == pygame.KEYDOWN:		
				for key, value in self.key_dict.iteritems():
					if event.key == value:
						self.key_status[key] = True					# Update key_status dictionary
						break
			elif event.type == pygame.KEYUP:
				for key, value in self.key_dict.iteritems():
					if event.key == value:
						self.key_status[key] = False				# Update key_status dictionary
						break
		self.cur_pos = pygame.mouse.get_pos()
	
	def draw_grid(self, size, color=(0, 0, 0)):
		unit = size * self.scale 									# Pixels per square = 100 * scale for 1 m squares
		win_x, win_y = self.window.get_size()						# Widow x and y size in pixels
		ni = win_x / unit + 1 										# Size of each square in pixels
		nj = win_y / unit + 1 
		for i in range(ni):
			pygame.draw.line(self.window, color, (i * unit, 0), (i * unit, win_y), 2) 
		for j in range(nj):
			pygame.draw.line(self.window, color, (0, j * unit), (win_x, j * unit), 2)

	def draw_world(self, res, color=(255, 0, 0)):
		nj, ni = self.world.shape
		for i in range(ni):
			for j in range(nj):
				if self.world[j][i] == -1:
					pygame.draw.rect(self.window, color, 
						(self.scale * res * i, self.scale * res * j, self.scale * res, self.scale * res))

	def draw_buggy(self):
		size = [16, 22]
		pygame.draw.rect(self.window, black, 
			((self.buggy_pos[0] - size[0] / 2) * self.scale, (self.buggy_pos[1] - size[1] / 2) * self.scale, size[0] * self.scale, size[1] * self.scale))
			 
	def update_window(self, path, res):
		# Draws GUI
		self.window.fill(white)	
		self.draw_world(res)
		self.draw_grid(res, slate_gray)
		self.draw_grid(100)
		self.draw_buggy()
		self.plot_path(path, res) 
		pygame.display.update()

	def node_nb(self, pos, scale):
		nj, ni = self.world.shape
		i = int(pos[0]) / scale
		j = int(pos[1]) / scale
		if i > ni - 1:
			i = ni - 1
		if j > nj -1:
			j = nj - 1
		return int(ni * j + i)
		
	def plot_path(self, path, res):
		if path:
			for i in range(len(path) - 1):
				p1 = [self.scale * res * (point + 0.5) for point in path[i]]
				p2 = [self.scale * res * (point + 0.5) for point in path[i + 1]]
				pygame.draw.line(self.window, green, (p1), (p2), 3)

	def main(self):
		clock = pygame.time.Clock() 										
		graph = grid2graph(self.world) 										# Convert grid into graph
		astar = AStar() 													# Initialise Astar
		res = 25   															# Resolution = cm per grid square
		while not self.quit:
			source = self.node_nb(self.buggy_pos, res)						# Source = buggy pos
			sink = self.node_nb(self.cur_pos, res * self.scale)       		# Sink = cursor pos
			[node.reset() for node in graph] 								# Reset every node
			path = astar.solve(graph, source, sink)							# Solve graph 
			self.event_handler()											# Put all keypress events into key_status dictionary
			self.update_window(path, res)									# Update display 
			clock.tick(self.fps)											# Restrict rate 
			

if __name__ == "__main__":
	AStarGUI()
