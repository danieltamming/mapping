

class Path:
	def __init__(self, DG, path):
		self.DG = DG
		self.path = self._clean_path(path)
		self.num_stops = len(self.path)
		self.travel_time = self._get_travel_time()
		self.segments = self._get_segments()

	def _clean_path(self, path, verbose=False):
		if self.DG.edges[(path[0], path[1])]['path'] == (-1, -1):
			path = path[1:]
			if verbose:
				print('FIRST trip WAS walking.')
		elif verbose:
			print('FIRST trip WAS NOT walking.')
		if self.DG.edges[(path[-2], path[-1])]['path'] == (-1, -1):
			path = path[:-1]
			if verbose:
				print('LAST trip WAS walking')
		elif verbose:
			print('LAST trip WAS NOT walking.')
		return path

	def _get_travel_time(self):
		travel_time = 0
		for edge in zip(self.path[:-1], self.path[1:]):
			travel_time += self.DG.edges[edge]['weight']
		return travel_time

	def _get_segments(self):
		first_line = self.DG.edges[(self.path[1], self.path[2])]['path']
		segments = []
		seg = {'start' : self.path[0], 'line' : first_line, 'travel_time' : 0}
		prev_line = None
		for edge in zip(self.path[1:-1], self.path[2:]):
			line = self.DG.edges[edge]['path']
			travel_time = self.DG.edges[edge]['weight']
			if line == (-1, -1):
				seg['end'] = edge[0]
				segments.append(seg)
				assert travel_time == 7*60
				# don't add this travel time since its walking
			elif prev_line == (-1, -1):
				seg = {'start' : edge[0], 'line' : line, 'travel_time' : 0}
			else:
				seg['travel_time'] += travel_time
			prev_line = line
		seg['end'] = self.path[-1]
		segments.append(seg)
		return segments

	def print_instructions(self, stops, trip_names):
		for seg in self.segments:
			start_stop_id = seg['start'][0]
			start_stop_name = stops.loc[start_stop_id]['stop_name']
			route_id, direction_id = seg['line']
			trips = trip_names.loc[route_id]
			trip_headsigns = trips.loc[
				trips['direction_id'] == direction_id]['trip_headsign'].values
			end_stop_id = seg['end'][0]
			end_stop_name = stops.loc[end_stop_id]['stop_name']

			print('At stop: \n\t' + start_stop_name)
			if len(trip_headsigns) == 1:
				print('get on: \n\t' + trip_headsigns[0])
			else:
				print('get on one of:')
				for headsign in trip_headsigns:
					print('\t' + headsign)
			print('and ride until: \n\t' + end_stop_name)
			print('should take: \n\t' + str(round(seg['travel_time']/60, 2)) 
				  + ' mins')
			print(start_stop_id)
			print(end_stop_id)
			print()