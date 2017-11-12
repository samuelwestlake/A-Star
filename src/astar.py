#!/usr/bin/env python

import numpy as np
from sys import argv
from math import sqrt
from time import time
import matplotlib.pyplot as plt
from heapq import heappush, heappop, heapify


def pythagoras(a, b):
	return sqrt(a ** 2 + b ** 2 )


def heap_remove(heap, index):
	heap[index] = heap[-1] 	
	heap.pop()
	heapify(heap)


def heap_index(heap, nb):
	i = 0 																# Find index of a node in a heap
	for item in heap:
		if item.nb == nb: 												# If the node numbers match
			return i
		i += 1


class AStar(object):

	def __init__(self):
		self.graph = None
		self.source = None
		self.sink = None
		self.open_list = []
		self.closed_list = []

	def get_set(self, graph, source, sink):
		self.graph = graph
		self.source = source
		self.sink = sink
		self.open_list = []
		self.closed_list = []

	def set_heuristic(self, heuristic, d):
		for node in self.graph:								
			i, j = node.pos
			si, sj = self.graph[self.sink].pos
			if heuristic == "manhatten":
				dx = abs(node.pos[0] - si)
				dy = abs(node.pos[1] - sj)
				node.h = (dx + dy) * d
			elif heuristic == "diagonal":
				dx = abs(node.pos[0] - si)
				dy = abs(node.pos[1] - sj)
				node.h = d * (dx + dy) + (sqrt(2) - 2 * d) * min(dx, dy)
			elif heuristic == "euclidian":
				node.h = pythagoras(i - si, j - sj)	* d
			else:
				print("Error: unknown method: " + str(heuristic))
				print("Options are:\tmanhatten\n\t\teuclidian\n\t\tdiagonal")
				return False
		return True

	def find_open_nodes(self):
		parent = self.closed_list[-1]
		for neighbour, cost in parent.neighbours.iteritems():
			n = int(neighbour)
			if self.graph[n].status == "open":							# If node is aleady open
				self.parent_check(self.graph[n], parent, cost) 			# Check if new closed node is a better parent
			elif self.graph[n].status is None:							# If node has not been given a status yet
				self.make_open(n, parent, cost)							# Make node open

	def find_close_nodes(self):
		if self.open_list:												# If there are open nodes
			node = heappop(self.open_list)								# Pop off the first one
			self.make_closed(node.nb)									# Close it												# Return False to indicate no more steps can be taken

	def parent_check(self, node, alt_parent, cost):
		alt_g = alt_parent.g + cost 									# Alternative g cost
		if alt_g < node.g:												# If alternative cost is less
			node.parent = alt_parent.nb 								# Re-assign parent
			node.g = alt_g 												# Re-assign g 
			node.f = node.g + node.h 									# Re-assign f
			i = heap_index(self.open_list, node.nb)						# Find index of node in heap
			heap_remove(self.open_list, i)								# Remove from open_list
			heappush(self.open_list, node)								# Re-add node to openlist

	def make_open(self, n, parent, cost):
		self.graph[n].status = "open"									# Set status to open
		self.graph[n].g = parent.g + cost 								# Calculate g
		self.graph[n].f = self.graph[n].g + self.graph[n].h 			# Calculate f
		self.graph[n].parent = parent.nb 								# Assign parent
		heappush(self.open_list, self.graph[n])							# Add to heap

	def make_closed(self, n):
		self.graph[n].status = "closed"									# Set status to closed
		self.closed_list.append(self.graph[n]) 							# Append to closed list

	def get_path(self):
		path = []
		node = self.sink 												# Start at the sink
		while True:	 
			path.append(self.graph[node].pos) 							# Append the current node's position
			node = self.graph[node].parent 								# Change current node to current node's parent
			if path[-1] == self.graph[self.source].pos: 				# If at the source
				break
			if node is None:
				return path
		return path[::-1]	 											# Reverse the order

	def solve(self, graph, source, sink, heuristic="manhatten", d=1):
		start_time = time()
		self.get_set(graph, source, sink)								# Empty all lists and heaps
		if self.set_heuristic(heuristic, d):							# Calclate heuristic
			self.make_closed(source)									# Close the source node
			while self.closed_list[-1].nb != sink:						# While the sink node has not been closed
				self.find_open_nodes() 									# Find new nodes to open
				self.find_close_nodes() 								# Close a node
				if len(self.open_list) == 0:
					break
		path = self.get_path()
		return path

if __name__=="__main__":
	AStar()
  