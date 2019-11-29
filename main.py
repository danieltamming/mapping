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
import geopy.distance

from graphing import get_graph, show_graph, set_wait_time
from dataframe import (get_df, get_stops, get_trip_names, 
					   get_stops_within, get_closest_stops)
from path import Path

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

def get_travel_time(p1, p2, km_per_min=5/60):
	'''
	Calculates time to walk from p1 to p2, 
	where both points are latitude longitude pairs
	'''
	km_per_sec = km_per_min/60
	dist = geopy.distance.distance(p1, p2).km
	return dist/km_per_sec

def get_best_between_stops(stop_id_A, stop_id_B):
	nodes_A = [key for key in DG.nodes.keys() if key[0] == stop_id_A]
	nodes_B = [key for key in DG.nodes.keys() if key[0] == stop_id_B]
	assert nodes_A and nodes_B , 'Invalid stop ID.'
	shortest_time = float('inf')
	for source in nodes_A:
		for target in nodes_B:
			result = algos.dijkstra_path(DG, source, target, weight='weight')
			path = Path(DG, result)
			if path.travel_time < shortest_time:
				# < to prefer earlier suggest paths (therefore nearest stop)
				shortest_path = path
				shortest_time = path.travel_time
	return shortest_path

def get_best_between_coordinates(start_coord, end_coord, num_stops):
	start_stop_ids = get_closest_stops(my_df, start_coord, num_stops)
	end_stop_ids = get_closest_stops(my_df, end_coord, num_stops)
	shortest_time = float('inf')
	for stop_id_A in start_stop_ids:
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

def stuff():
	stop_times = pd.read_csv('OpenData_TTC_Schedules/stop_times.txt').dropna(axis=1, how='all')
	trip_id = 39168089
	trip = stop_times.loc[stop_times['trip_id'] == trip_id]
	print(trip[['stop_id', 'arrival_time']])
	print(len(trip))

if __name__ == "__main__":
	# stuff()
	# exit()

	my_df = get_df(saving=True)
	# route_id = 58692
	# direction_id = 1
	# trip = my_df.loc[(my_df['route_id'] == route_id) & (my_df['direction_id'] == direction_id)]
	# print(trip)
	# exit()
	stops = get_stops()
	trip_names = get_trip_names()
	DG = get_graph(my_df, saving=True)
	DG = set_wait_time(DG, 7*60)

	start_coord = (43.685988, -79.453486)
	end_coord = (43.650104, -79.419555)
	start_time = time.time()
	path = get_best_between_coordinates(start_coord, end_coord, 3)
	path.print_instructions(stops, trip_names)
	print(path.travel_time/60)
	exit()

	stop_id_A = 6619
	stop_id_B = 367
	path = get_best_between_stops(stop_id_A, stop_id_B)
	path._get_segments()
	# path.print_instructions()
	exit()
	
	# result, points, polies = get_route_info()
	lat, lon = 43.686298, -79.454210
	closest = get_closest_stops(my_df, lat, lon, k=6)
	print(closest)