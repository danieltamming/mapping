import geopy.distance

from gmaps import get_gmaps_route

def get_travel_time(p1, p2, km_per_min=5/60):
	'''
	Calculates time to walk from p1 to p2, 
	where both points are latitude longitude pairs
	'''
	km_per_sec = km_per_min/60
	dist = geopy.distance.distance(p1, p2).km
	return int(dist/km_per_sec)

def plot_temp(polies):
	ys = [pol[0] for pol in polies]
	xs = [pol[1] for pol in polies]
	plt.scatter(xs, ys)
	plt.show()

def get_user_input():
	lat = input('Enter pedestrian latitude coordinate: ')
	lon = input('Enter pedestrian longitude coordinate: ')
	start_coord = (lat, lon)
	print('\nDriver locations may be entered in any format acceptable'
		  ' by Google Maps (e.g. Pearson Airport).')
	start_drive = input('Enter driver starting location: ')
	end_drive = input('Enter ending location: ')
	return (lat, lon), start_drive, end_drive

def get_example():
	start_coord = (43.655900, -79.492757)
	(start_address, end_address, polies, 
		_) = get_gmaps_route(example=True)
	print('Driver\'s starting address: ' + start_address)
	print('Pedestrian\'s starting coordinates: {}'.format(start_coord))
	print('Joint ending address: ' + end_address)
	return polies, start_coord

def get_custom():
	approved = False
	while not approved:
		start_coord, start_drive, end_drive = get_user_input()
		(start_address, end_address, polies, 
			points) = get_gmaps_route(A=start_drive, B=end_drive, saving=True)
		usr_input = input('Correct driver start? (Y/N) ' 
			+ start_address + '\n').lower()
		if usr_input != 'y':
			print('\nRestarting input process.')
			continue
		usr_input = input('Correct driver end? (Y/N) ' 
			+ end_address + '\n').lower()
		if usr_input != 'y':
			print('\nRestarting input process.')
			continue
		approved = True
	return polies, start_coord

def get_use_type():
	usr_input = 0
	while usr_input not in [1, 2]:
		usr_input = input('Enter 1 for an example, or 2 for custom input: ')
		if usr_input.isdigit():
			usr_input = int(usr_input)
	if usr_input == 1:
		return get_example()
	else:
		return get_custom()

def get_calc_time(my_df, DG, stops):
	'''
	Used in computation time testing. Calculates the average 
	time it takes to find optimal routes between various points
	'''

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