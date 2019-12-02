import time

import matplotlib.pyplot as plt
import osmnx as ox
import networkx as nx
from networkx.classes.graphviews import subgraph_view

class Path:
	def __init__(self, DG, path, wait_time):
		self.DG = DG
		self.wait_time = wait_time
		self.path = path
		self.segments = self.process_path(self.path)
		self.travel_time = self._get_travel_time()

	def _get_travel_time(self):
		return sum([seg['travel_time'] for seg in self.segments])

	def _get_start_walk_segment(self, path):
		if self.DG.edges[(path[0], path[1])]['path'] != (-1, -1):
			return path, None
		seg = {'start' : path[0], 'line' : (-1, -1), 'travel_time' : 0}
		while (len(path) >= 2 
				and self.DG.edges[(path[0], path[1])]['path'] == (-1, -1)):
			seg['travel_time'] += (self.DG.edges[(path[0], path[1])]['weight']
								   - self.wait_time)
			assert seg['travel_time'] >= 0
			path = path[1:]
		seg['end'] = path[0]
		assert len(path) >= 2
		return path, seg

	def _get_end_walk_segment(self, path):
		if self.DG.edges[(path[0], path[1])]['path'] != (-1, -1):
			return path, None
		idx = len(path) - 2
		seg = {'end' : -1, 'line' : (-1, -1), 'travel_time' : 0}
		while self.DG.edges[(path[idx], path[idx+1])]['path'] == (-1, -1):
			seg['travel_time'] += (self.DG.edges[(path[idx], path[idx+1])]['weight']
								   - self.wait_time)
			assert seg['travel_time'] >= 0
			idx -= 1
		seg['start'] = path[idx]
		path = path[:idx+1]
		return path, seg

	def _get_middle_segments(self, path):
		segments = []
		first_line = self.DG.edges[(path[0], path[1])]['path']
		seg = {'start' : path[0], 'line' : first_line, 'travel_time' : 0}
		prev_line = None
		for edge in zip(path[1:-1], path[2:]):
			line = self.DG.edges[edge]['path']
			travel_time = self.DG.edges[edge]['weight']
			if line == (-1, -1):
				seg['end'] = edge[0]
				segments.append(seg)
				segments.append({'start' : edge[0], 
								 'line': (-1, -1),
								 'travel_time' : travel_time,
								 'end' : edge[1]})
			elif prev_line == (-1, -1):
				assert line != (-1, -1)
				seg = {'start' : edge[0], 'line' : line, 'travel_time' : travel_time}
			else:
				seg['travel_time'] += travel_time
			prev_line = line
		seg['end'] = path[-1]
		segments.append(seg)
		return segments


	def process_path(self, path):
		# these three functions must be called in this order
		path, start_walk_seg = self._get_start_walk_segment(path)
		path, end_walk_seg = self._get_end_walk_segment(path)
		segments = self._get_middle_segments(path)
		if start_walk_seg is not None:
			segments.insert(0, start_walk_seg)
		if end_walk_seg is not None:
			segments.append(end_walk_seg)
		return segments

	def print_instructions(self, stops, trip_names):
		for seg in self.segments:
			# print(seg)
			# continue

			start_stop_id = seg['start'][0]
			start_stop_name = stops.loc[start_stop_id]['stop_name']
			end_stop_id = seg['end'][0]
			end_stop_name = stops.loc[end_stop_id]['stop_name']
			if seg['line'] == (-1, -1):
				print('Walk from: \n\t' + start_stop_name)
				print('to: \n\t' + end_stop_name)
				print('should take: \n\t' 
					  + str(round(seg['travel_time']/60, 2)) + ' mins.\n')
				continue
			route_id, direction_id = seg['line']
			trips = trip_names.loc[route_id]
			trip_headsigns = trips.loc[
				trips['direction_id'] == direction_id]['trip_headsign'].values

			print('At stop: \n\t' + start_stop_name)
			if len(trip_headsigns) == 1:
				print('get on: \n\t' + trip_headsigns[0])
			else:
				print('get on one of:')
				for headsign in trip_headsigns:
					print('\t' + headsign)
			print('and ride until: \n\t' + end_stop_name)
			print('should take: \n\t' + str(round(seg['travel_time']/60, 2)) 
				  + ' mins\n')

	def plot_route(self, stops):
		nodes = set(self.path)

		edges = list(zip(self.path[:-1], self.path[1:]))
		sub_DG = subgraph_view(
			self.DG, lambda n : n in nodes, lambda n1, n2 : (n1, n2) in edges)

		sub_DG = nx.MultiDiGraph()
		north = east = float('-inf')
		south = west = float('inf')
		for node_key in nodes:
			x, y  = self.DG.nodes[node_key]['pos']
			sub_DG.add_node(node_key, x=x, y=y)
			north = max(north, y)
			south = min(south, y)
			east = max(east, x)
			west = min(west, x)
		for u, v in edges:
			attr = self.DG.edges[(u, v)]
			sub_DG.add_edge(u, v, weight=attr['weight'], path=attr['path'])

		cushion = 0.001
		bbox = [north+cushion, south-cushion, east+cushion, west-cushion]
		# G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
		# G_projected = ox.project_graph(G)
		# fig, ax = ox.plot_graph(G_projected, show=False)
		# print(time.time() - start_time)
		ox.plot_graph(sub_DG, bbox=bbox, margin=0, equal_aspect=True)