import os
import time

from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import networkx.algorithms.shortest_paths.weighted as algos

from graphing import (get_graph, show_graph, 
					  add_temp_stops, remove_temp_stops)
from dataframe import (get_df, get_stops, get_trip_names, 
					   get_stops_within, get_closest_stops)
from path import Path
from utils import get_travel_time, plot_temp, get_use_type

WAIT_TIME = 7*60

def get_calc_time(my_df, DG, stops):
	# coordinates that form an approximate bounding box around Toronto
	top = 43.716832
	left = -79.543279
	bottom = 43.665441
	right = -79.331792
	num_points = 5
	lats = np.linspace(bottom, top, num=num_points)
	lons = np.linspace(left, right, num=num_points)
	count = 0
	start_time = time.time()
	for i in range(len(lats)-1):
		for j in range(len(lons)-1):
			for k in range(i+1, len(lats)):
				for l in range(j+1, len(lons)):
					A = (lats[i], lons[j])
					B = (lats[k], lons[l])
					get_best_route(DG, my_df, stops, A, B, 8)
					get_best_route(DG, my_df, stops, B, A, 8)
					count += 2
	delta_time = time.time() - start_time
	print(count)
	print(round(delta_time, 2))
	print(round(delta_time/count, 2))

def get_best_route(DG, my_df, stops, start_coord, end_coord, num_stops):
	'''
	New approach: add 0 weight directed edge to all A nodes,
				  and 0 weight directed edge from all B nodes
				  then remove them when done
	'''
	start_stop_ids = get_closest_stops(my_df, start_coord, num_stops)
	end_stop_ids = get_closest_stops(my_df, end_coord, num_stops)
	to_remove = add_temp_stops(DG, stops, start_stop_ids, end_stop_ids,
							   start_coord, end_coord)
	result = algos.dijkstra_path(DG, 'temp start', 
								'temp end', weight='weight')
	assert (isinstance(result[0], str) and isinstance(result[-1], str)
			and result[1][1] == -1 and result[-2][1] == -1)
	path = Path(DG, result, WAIT_TIME)
	remove_temp_stops(DG, to_remove)
	return path

def get_meeting_directions(DG, my_df, stops, start_coord, drive_coords):
	print(50*'-')
	print('Finding optimal meeting location.')
	best_time = float('inf')
	for end_coord in tqdm(drive_coords):
		path = get_best_route(DG, my_df, stops, start_coord, end_coord, 8)
		if path.travel_time < best_time:
			best_time = path.travel_time
			best_path = path
	best_path.print_instructions(stops, trip_names)

if __name__ == "__main__":
	my_df = get_df(saving=True)
	stops = get_stops()
	trip_names = get_trip_names()
	DG = get_graph(my_df, saving=True)
	polies, start_coord = get_use_type()
	drive_coords = polies[::20]
	get_meeting_directions(DG, my_df, stops, start_coord, drive_coords)
	
	# get_calc_time(my_df, DG, stops)