import os
import time
from datetime import datetime, timedelta, date
import pickle

from tqdm import tqdm
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import googlemaps
import polyline
import networkx as nx

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

def get_closest_stop(my_df, lat, lon, k=1):
	order = cdist([[lat, lon]], 
				   my_df[['stop_lat', 'stop_lon']]).argsort()[0,:]
	idxs = []
	routes_seen = set()
	for i in order:
		if my_df.iloc[i]['route_id'] not in routes_seen:
			routes_seen.add(my_df.iloc[i]['route_id'])
			idxs.append(i)
			if len(idxs) >= k:
				break
	return my_df.iloc[idxs][['stop_lat', 'stop_lon']]

def to_datetime(s):
	arr = s.split(':')
	add_day = False
	if int(arr[0]) >= 24:
		arr[0] = str(int(arr[0]) - 24)
		add_day = True
	dtime = datetime.strptime(':'.join(arr), '%H:%M:%S')
	if add_day:
		dtime = dtime + timedelta(days=1)
	return dtime

def get_df(saving=True):
	folder = 'OpenData_TTC_Schedules/'
	my_df_filepath = 'data/my_df.csv'
	if saving and os.path.exists(my_df_filepath):
		print('Extracting my_df from file.')
		df = pd.read_csv(my_df_filepath)
		df['time'] = df['time'].map(lambda x : to_datetime(x).time())
		return df
	print('Constructing my_df.')
	stop_times = pd.read_csv(
		folder+'stop_times.txt').dropna(axis=1, how='all')
	stops = pd.read_csv(folder+'stops.txt').dropna(axis=1, how='all')
	trips = pd.read_csv(folder+'trips.txt').dropna(axis=1, how='all')
	df0 = pd.merge(stop_times[['trip_id', 'arrival_time', 'stop_id']], 
				   trips[['trip_id', 'route_id', 'direction_id']], 
				   on='trip_id')
	longest_trip_ids = []

	route_direction_pairs = set(
		tuple(L) for L in df0[['route_id', 'direction_id']].values.tolist())
	
	for route_id, direction_id in route_direction_pairs:
		this_route = df0.loc[(df0['route_id'] == route_id)
							 & (df0['direction_id'] == direction_id)]
		longest_trip_ids.append(this_route.trip_id.mode().values[0])
		
	'''
	t0 = datetime.strptime('15', '%H')
	t0_trip_ids = []
	for route_id in tqdm(set(df0['route_id'].values.tolist())):
		this_route = df0.loc[df0['route_id'] == route_id]
		distances = this_route['arrival_time'].map(
			lambda x : abs((to_datetime(x) - t0).total_seconds()))
		min_row = this_route.loc[distances.idxmin()]
		t0_trip_ids.append(min_row['trip_id'])
	t0_trips = pd.Series(data=t0_trip_ids, name='trip_id')
	'''
	df1 = pd.merge(df0, 
		pd.Series(data=longest_trip_ids, 
				  name='trip_id')).drop('trip_id', axis=1)
	my_stops = stops[['stop_id', 'stop_lat', 'stop_lon']]
	df2 = pd.merge(df1, my_stops).rename(columns={'arrival_time' : 'time'})
	df2['time'] = df2['time'].map(lambda x : to_datetime(x).time())
	df2['stop_lat'] = df2['stop_lat'].map(lambda x : round(x, 6))
	df2['stop_lon'] = df2['stop_lon'].map(lambda x : round(x, 6))
	df2 = df2.sort_values(['route_id', 'time']).reset_index(drop=True)
	if saving: df2.to_csv(my_df_filepath)
	return df2

def create_graph(my_df):
	print('Constructing graph.')
	DG = nx.DiGraph()
	route_direction_pairs = set(
		tuple(L) for L in my_df[['route_id', 'direction_id']].values.tolist())
	for route_id, direction_id in tqdm(route_direction_pairs):
		this_route = my_df.loc[(my_df['route_id'] == route_id)
							 & (my_df['direction_id'] == direction_id)]
		travel_times = this_route['time'].map(
			lambda x : datetime.combine(date.min, x)).diff().map(
				lambda x : x.total_seconds()).values
		route_info = this_route[['stop_id', 'stop_lat', 'stop_lon']].values

		prev_stop_id, stop_lat, stop_lon = route_info[0]
		if not DG.has_node(prev_stop_id):
			DG.add_node(prev_stop_id, pos=(stop_lon, stop_lat))
		for end_idx in range(1, len(travel_times)):
			cur_stop_id, stop_lat, stop_lon = route_info[end_idx]
			travel_time = travel_times[end_idx]
			if not DG.has_node(cur_stop_id):
				DG.add_node(cur_stop_id, pos=(stop_lon, stop_lat))
			if DG.has_edge(prev_stop_id, cur_stop_id):
				DG.edges[
					(prev_stop_id, cur_stop_id)][
					'path'].append((route_id, direction_id))
			else:
				DG.add_edge(prev_stop_id, cur_stop_id, weight=travel_time, 
							path=[(route_id, direction_id)])
			prev_stop_id = cur_stop_id
	nx.draw(DG, nx.get_node_attributes(DG, 'pos'), 
			node_size=5, node_color='r', width=1, edge_color='b', arrowsize=8)
	plt.show()
	return DG

if __name__ == "__main__":
	# result, points, polies = get_route_info()
	my_df = get_df(saving=True)
	DG = create_graph(my_df)
	exit()
	
	lat, lon = 43.686298, -79.454210
	closest = get_closest_stop(my_df, lat, lon, k=6)
	print(closest)