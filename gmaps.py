import os
import pickle

import googlemaps
import polyline

from path import Path

def get_gmaps_route(A=None, B=None, saving=False, example=False):
	temp_file = 'data/example.pickle'
	if example:
		result = pickle.load(open(temp_file, 'rb'))
	else:
		assert os.path.exists('keys.py') , 'Need Google API key. See README.'
		from keys import API_KEY
		gmaps = googlemaps.Client(key=API_KEY)
		result = gmaps.directions(A, B, mode='driving', units='metric')

	if saving:
		pickle.dump(result, open(temp_file, 'wb'))

	polies = []
	points = []
	for i, step in enumerate(result[0]['legs'][0]['steps']):
		polies.extend(polyline.decode(step['polyline']['points']))
		lat = step['start_location']['lat']
		lon = step['start_location']['lng']
		points.append((lat, lon))

	points.append((step['end_location']['lat'], step['end_location']['lng']))
	legs = result[0]['legs']
	start_address = legs[0]['start_address']
	end_address = legs[-1]['end_address']
	return start_address, end_address, polies, points