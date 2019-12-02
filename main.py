import os
import time
from datetime import datetime, timedelta, date
import pickle

from tqdm import tqdm
import numpy as np
import pandas as pd
import googlemaps
import polyline
import networkx as nx
import networkx.algorithms.shortest_paths.weighted as algos

from graphing import get_graph, show_graph, set_wait_time
from dataframe import (get_df, get_stops, get_trip_names, 
					   get_stops_within, get_closest_stops)
from path import Path
from utils import get_travel_time

if os.path.exists('keys.py'): from keys import API_KEY

def get_route_info(verbose=False):
	temp_file = 'data/example.pickle'
	gmaps = googlemaps.Client(key=API_KEY)
	A = '443 Arlington Ave, York, ON M6C 3A2'
	B = 'Pearson Airport Terminal 1, Mississauga, ON'
	if not os.path.exists(temp_file):
		result = gmaps.directions(A, B, mode='driving', units='metric')
		pickle.dump(result, open(temp_file, 'wb'))
	else:
		result = pickle.load(open(temp_file, 'rb'))
	if verbose:
		print(result[0]['legs'][0]['steps'][0].keys())
		print()
	polies = []
	points = []
	for i, step in enumerate(result[0]['legs'][0]['steps']):
		polies.extend(polyline.decode(step['polyline']['points']))
		points.append((step['start_location']['lat'], step['start_location']['lng']))
		if verbose:
			print(step['start_location'])
			if False:
				print(i)
				print(step['start_location'])
				print(step['end_location'])
				print(step['distance'])
				print(step['duration'])
				print(step['polyline'])
				print()
			if i == 7:
				print(step['start_location'])
				print(step['end_location'])
				print(polyline.decode(step['polyline']['points']))
	points.append((step['end_location']['lat'], step['end_location']['lng']))

	return result, points, polies

def get_best_between_stops(stop_id_A, stop_id_B):
	'''
	New approach: add 0 weight directed edge to all A nodes,
				  and 0 weight directed edge from all B nodes
				  then remove them when done
	'''
	nodes_A = [key for key in DG.nodes.keys() if key[0] == stop_id_A]
	temp_node_A = (nodes_A[0][0], -1)
	nodes_B = [key for key in DG.nodes.keys() if key[0] == stop_id_B]
	temp_node_B = (nodes_B[0][0], -1)
	for node_A in nodes_A:
		DG.add_edge(temp_node_A, node_A, weight=0)
	for node_B in nodes_B:
		DG.add_edge(node_B, temp_node_B, weight=0)
	result = algos.dijkstra_path(DG, temp_node_A, temp_node_B, weight='weight')
	# skip the temp edges
	path = Path(DG, result[1:-1], WAIT_TIME)

	DG.remove_node(temp_node_A)
	DG.remove_node(temp_node_B)
	return path

def get_best_between_coordinates(start_coord, end_coord, num_stops):
	start_stop_ids = get_closest_stops(my_df, start_coord, num_stops)
	end_stop_ids = get_closest_stops(my_df, end_coord, num_stops)

	shortest_time = float('inf')
	for stop_id_A in tqdm(start_stop_ids):
		stop_coord_A = stops.loc[stop_id_A][['stop_lat', 'stop_lon']]
		for stop_id_B in end_stop_ids:
			stop_coord_B = stops.loc[stop_id_B][['stop_lat', 'stop_lon']]
			
			first_mile_time = get_travel_time(start_coord, stop_coord_A)
			path = get_best_between_stops(stop_id_A, stop_id_B)
			last_mile_time = get_travel_time(stop_coord_B, end_coord)
			total_time = first_mile_time + path.travel_time + last_mile_time
			if total_time < shortest_time:
				shortest_path = path
				shortest_time = total_time
	return shortest_path

def get_best_route(start_coord, end_coord, num_stops):
	'''
	New approach: add 0 weight directed edge to all A nodes,
				  and 0 weight directed edge from all B nodes
				  then remove them when done
	'''
	start_stop_ids = get_closest_stops(my_df, start_coord, num_stops)
	end_stop_ids = get_closest_stops(my_df, end_coord, num_stops)
	
	to_remove = ['temp start', 'temp end']
	for stop_id_A in start_stop_ids:
		nodes_A = [key for key in DG.nodes.keys() if key[0] == stop_id_A]
		temp_node_A = (stop_id_A, -1)
		for node_A in nodes_A:
			DG.add_edge(temp_node_A, node_A, weight=0)
		stop_coord_A = stops.loc[stop_id_A][['stop_lat', 'stop_lon']].values
		walk_time = get_travel_time(start_coord, stop_coord_A)
		DG.add_edge('temp start', temp_node_A, weight=walk_time)
		to_remove.append(temp_node_A)
	for stop_id_B in end_stop_ids:
		nodes_B = [key for key in DG.nodes.keys() if key[0] == stop_id_B]
		temp_node_B = (stop_id_B, -1)
		for node_B in nodes_B:
			DG.add_edge(node_B, temp_node_B, weight=0)
		stop_coord_B = stops.loc[stop_id_B][['stop_lat', 'stop_lon']].values
		walk_time = get_travel_time(stop_coord_B, end_coord)
		DG.add_edge(temp_node_B, 'temp end', weight=walk_time)
		to_remove.append(temp_node_B)

	result = algos.dijkstra_path(DG, 'temp start', 'temp end', weight='weight')
	# skip the temp edges
	assert isinstance(result[0], str) and isinstance(result[-1], str)
	assert result[1][1] == -1 and result[-2][1] == -1
	result = result[2:-2]
	path = Path(DG, result, WAIT_TIME)
	for node in to_remove:
		DG.remove_node(node)
	return path

# def get_best_between_coordinates(start_coord, end_coord, num_stops):
# 	start_stop_ids = get_closest_stops(my_df, start_coord, num_stops)
# 	end_stop_ids = get_closest_stops(my_df, end_coord, num_stops)
# 	for start_stop_id in start_stop_ids:
# 		walk_time = get_travel_time(
# 			start_coord, stops.loc[start_stop_id][['stop_lat', 'stop_lon']])
# 		DG.add_edge('temp_node_start', start_stop_id, weight=walk_time)
# 	for
# 	return path

if __name__ == "__main__":
	# stuff()
	# exit()
	WAIT_TIME = 7*60

	my_df = get_df(saving=True)
	stops = get_stops()
	trip_names = get_trip_names()
	DG = get_graph(my_df, saving=True)
	# DG = set_wait_time(DG, 7*60)

	start_coord = (43.676473, -79.544826)
	end_coord = (43.705379, -79.358229)
	# path = get_best_between_coordinates(start_coord, end_coord, 6)
	# print(path.travel_time/60)
	path = get_best_route(start_coord, end_coord, 30)
	path.print_instructions(stops, trip_names)
	print(path.travel_time/60)
	path.plot_route(stops)