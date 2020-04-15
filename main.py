import os
import time

from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import networkx.algorithms.shortest_paths.weighted as algos

from path import Path
from utils import get_points, get_all_data, get_best_route


def get_meeting_directions(DG, my_df, stops, start_coord, drive_coords):
	'''
	Given the drive_coord list of possible coordinates at which to meet
	the driver, finds the coordinate that is the fastest to get to,
	and the instructions fro how to get to it.
	'''
	print(50*'-')
	print('Finding optimal meeting location.')
	best_time = float('inf')
	for end_coord in tqdm(drive_coords):
		path = get_best_route(DG, my_df, stops, start_coord, end_coord, 8)
		if path.travel_time < best_time:
			best_time = path.travel_time
			best_path = path
	best_path.print_instructions(stops, trip_names)

def get_meeting_location(DG, my_df, stops, start_coord, 
						 drive_coords, trip_names):
	best_time = float('inf')
	for end_coord in tqdm(drive_coords):
		path = get_best_route(DG, my_df, stops, start_coord, end_coord, 8)
		if path.travel_time < best_time:
			best_time = path.travel_time
			best_path = path
	return best_path.get_meetup_location(stops, trip_names)

def command_line_version():
	my_df, stops, trip_names, DG = get_all_data()
	polies, start_coord = get_use_type()
	get_meeting_directions(DG, my_df, stops, start_coord, polies[::20])


if __name__ == "__main__":
	my_df, stops, trip_names, DG = get_all_data()
	polies, start_coord = get_points()
	meetup_location = get_meeting_location(
		DG, my_df, stops, start_coord, polies[::20])
	print(meetup_location)


# pearson airport. 317 harvie ave. scotiabank arena