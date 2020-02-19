import os
from datetime import datetime, timedelta, date

from tqdm import tqdm
import numpy as np
import pandas as pd
import geopy.distance
from scipy.spatial.distance import cdist

def get_closest_stops(my_df, coords, k=1):
	'''
	Find the k nearest stop_ids that have unique route_ids
	Returns stop_ids, route_id, direction_id
	'''
	lat, lon = coords
	# fast way to get order approximated by euclidean distance
	approx_order = cdist([[lat, lon]], 
					my_df[['stop_lat', 'stop_lon']]).argsort()[0,:]
	# assume k closest points will be in first 10*k indices of approx
	approx_df = my_df.iloc[approx_order[:10*k], :]
	order = np.apply_along_axis(
		lambda row: geopy.distance.distance(coords, row).km, 1, 
		approx_df[['stop_lat', 'stop_lon']].values).argsort()
	# order will include indices of rows with same stop_id, different route
	# and direction
	ordered_df = approx_df.iloc[order, :][
		['stop_id', 'route_id', 'direction_id']].values
	lines_seen = set()
	closest_stop_ids = []
	for stop_id, route_id, direction_id in ordered_df:
		if ((route_id, direction_id) not in lines_seen 
				and stop_id not in closest_stop_ids):
			closest_stop_ids.append(stop_id)
			lines_seen.add((route_id, direction_id))
		if len(closest_stop_ids) >= k:
			break
	return closest_stop_ids

def get_stops_within(my_df, stop_id, max_dist):
	stops = my_df[['stop_id', 'stop_lat', 'stop_lon']].drop_duplicates()
	lat, lon = stops.loc[
		stops['stop_id'] == stop_id][['stop_lat', 'stop_lon']].iloc[0].values
	order = cdist([[lat, lon]],
					stops[['stop_lat', 'stop_lon']]).argsort()[0,:]
	idxs = []
	for i in order:
		point = tuple(stops.iloc[i][['stop_lat', 'stop_lon']].values)
		if geopy.distance.distance((lat, lon), point).km > max_dist:
			break
		idxs.append(i)
	return stops.iloc[idxs]['stop_id'].values

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

def get_stops():
	stops_filepath = 'OpenData_TTC_Schedules/stops.txt'
	return pd.read_csv(
		stops_filepath)[
			['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
			].set_index('stop_id')

def get_trip_names():
	trips_filepath = 'OpenData_TTC_Schedules/trips.txt'
	return pd.read_csv(trips_filepath)[
		['route_id', 'direction_id', 'trip_headsign']
		].drop_duplicates().set_index('route_id')

def get_df(saving=True):
	folder = 'OpenData_TTC_Schedules/'
	my_df_filepath = 'data/my_df.csv'
	if saving and os.path.exists(my_df_filepath):
		print('Loading dataframe from file.')
		df = pd.read_csv(my_df_filepath)
		df['time'] = df['time'].map(lambda x : to_datetime(x).time())
		return df
	print('Constructing and saving dataframe. Should take a few seconds.')
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
	
	for route_id, direction_id in tqdm(route_direction_pairs):
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