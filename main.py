import os
import time

from tqdm import tqdm
import matplotlib.pyplot as plt
import networkx.algorithms.shortest_paths.weighted as algos

from graphing import (get_graph, show_graph, 
					  add_temp_stops, remove_temp_stops)
from dataframe import (get_df, get_stops, get_trip_names, 
					   get_stops_within, get_closest_stops)
from path import Path
from utils import get_travel_time, plot_temp, get_use_type

WAIT_TIME = 7*60

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