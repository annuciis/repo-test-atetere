import requests
import json
import datetime
import time
import yaml

from datetime import datetime
from configparser import ConfigParser
print('Asteroid processing service')

# Initiating and reading config values
print('Loading configuration from file')


try:
	config = ConfigParser()
	config.read('config.ini')

	nasa_api_key = config.get('nasa', 'api_key')
	nasa_api_url = config.get('nasa', 'api_url')
except:
	logger.exception('')
print('DONE')


# Getting todays date
dt = datetime.now()
request_date = str(dt.year) + "-" + str(dt.month).zfill(2) + "-" + str(dt.day).zfill(2)  
print("Generated today's date: " + str(request_date))

# requesting info from nasa api
print("Request url: " + str(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key))
r = requests.get(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key)

# printing nasa request response data
print("Response status code: " + str(r.status_code))
print("Response headers: " + str(r.headers))
print("Response content: " + str(r.text))

# checking if response status is 200
if r.status_code == 200:

	# putting response text in variable
	json_data = json.loads(r.text)

	ast_safe = []
	ast_hazardous = []

	# checking if element_count is in response data
	if 'element_count' in json_data:
		# giving number of astroids in variable and printing it
		ast_count = int(json_data['element_count'])
		print("Asteroid count today: " + str(ast_count))

		# checking if astroids are more than 0
		if ast_count > 0:
			# checking each value in near_earth_objects data
			for val in json_data['near_earth_objects'][request_date]:
				# checking if the value that was got from data has all giving variables
				if 'name' and 'nasa_jpl_url' and 'estimated_diameter' and 'is_potentially_hazardous_asteroid' and 'close_approach_data' in val:
					# assingning variables with astroid name and url
					tmp_ast_name = val['name']
					tmp_ast_nasa_jpl_url = val['nasa_jpl_url']
					# checking if there are kilometers written in diameter value
					if 'kilometers' in val['estimated_diameter']:
						# checking if given varuables are included in value
						if 'estimated_diameter_min' and 'estimated_diameter_max' in val['estimated_diameter']['kilometers']:
							# assigning astroid minimal and maximal diameter variables with numbers that were got
							tmp_ast_diam_min = round(val['estimated_diameter']['kilometers']['estimated_diameter_min'], 3)
							tmp_ast_diam_max = round(val['estimated_diameter']['kilometers']['estimated_diameter_max'], 3)
						# if there is no diameter written we assign that diameter are these values	
						else:
							tmp_ast_diam_min = -2
							tmp_ast_diam_max = -2
					# if there is no name and url and diameter and if it is potentially hazardous asteroid and close approach data then we put this diameter		
					else:
						tmp_ast_diam_min = -1
						tmp_ast_diam_max = -1
					# we assign variable with data that we got
					tmp_ast_hazardous = val['is_potentially_hazardous_asteroid']

					# we are checking if there are close approach data
					if len(val['close_approach_data']) > 0:
						# we are checking if the data includes following variables
						if 'epoch_date_close_approach' and 'relative_velocity' and 'miss_distance' in val['close_approach_data'][0]:
							# we are assigning close approach data variables with data
							tmp_ast_close_appr_ts = int(val['close_approach_data'][0]['epoch_date_close_approach']/1000)
							tmp_ast_close_appr_dt_utc = datetime.utcfromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							tmp_ast_close_appr_dt = datetime.fromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')

							# we are checking if there is kilometers per hour written in the data
							if 'kilometers_per_hour' in val['close_approach_data'][0]['relative_velocity']:
								# then we write the result and we assign to variable
								tmp_ast_speed = int(float(val['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))
							# if there are no kilometers per hour then we set the speed to -1
							else:
								tmp_ast_speed = -1
							# we are checking if there is kilometers written in the data
							if 'kilometers' in val['close_approach_data'][0]['miss_distance']:
								# then we write the result and we assign to variable
								tmp_ast_miss_dist = round(float(val['close_approach_data'][0]['miss_distance']['kilometers']), 3)
							# if there are no kilometers then we set the distance variable to -1
							else:
								tmp_ast_miss_dist = -1
						# if there are no epoch_date_close_approach, relative_velocity and miss_distance data, we set the constant values and assign them to variables
						else:
							tmp_ast_close_appr_ts = -1
							tmp_ast_close_appr_dt_utc = "1969-12-31 23:59:59"
							tmp_ast_close_appr_dt = "1969-12-31 23:59:59"
					# if there are no close approach data we print that there are no close approach data in meesage and assign variables to given values
					else:
						print("No close approach data in message")
						tmp_ast_close_appr_ts = 0
						tmp_ast_close_appr_dt_utc = "1970-01-01 00:00:00"
						tmp_ast_close_appr_dt = "1970-01-01 00:00:00"
						tmp_ast_speed = -1
						tmp_ast_miss_dist = -1
					# printing astroid name, close approach ts and spped
					print("------------------------------------------------------- >>")
					print("Asteroid name: " + str(tmp_ast_name) + " | INFO: " + str(tmp_ast_nasa_jpl_url) + " | Diameter: " + str(tmp_ast_diam_min) + " - " + str(tmp_ast_diam_max) + " km | Hazardous: " + str(tmp_ast_hazardous))
					print("Close approach TS: " + str(tmp_ast_close_appr_ts) + " | Date/time UTC TZ: " + str(tmp_ast_close_appr_dt_utc) + " | Local TZ: " + str(tmp_ast_close_appr_dt))
					print("Speed: " + str(tmp_ast_speed) + " km/h" + " | MISS distance: " + str(tmp_ast_miss_dist) + " km")
					
					# Adding asteroid data to the corresponding array
					if tmp_ast_hazardous == True:
						ast_hazardous.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
					else:
						ast_safe.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
		# if there are no data, we print that there are no asteroids
		else:
			print("No asteroids are going to hit earth today")
	
	# printing how mant hazardous asteroids there are and how many safe asteroids there are
	print("Hazardous asteorids: " + str(len(ast_hazardous)) + " | Safe asteroids: " + str(len(ast_safe)))

	# checking if there are hazardous asteroids
	if len(ast_hazardous) > 0:

		ast_hazardous.sort(key = lambda x: x[4], reverse=False)

		# printing today's possible apocalypse times
		print("Today's possible apocalypse (asteroid impact on earth) times:")
		for asteroid in ast_hazardous:
			print(str(asteroid[6]) + " " + str(asteroid[0]) + " " + " | more info: " + str(asteroid[1]))

		ast_hazardous.sort(key = lambda x: x[8], reverse=False)
		# printing closes passing distance and at which km and more info
		print("Closest passing distance is for: " + str(ast_hazardous[0][0]) + " at: " + str(int(ast_hazardous[0][8])) + " km | more info: " + str(ast_hazardous[0][1]))
	# if there is no asteroids close passing earth today
	else:
		# we print following statement
		print("No asteroids close passing earth today")

else:
	# printing this if we don't get response from API
	print("Unable to get response from API. Response code: " + str(r.status_code) + " | content: " + str(r.text))
