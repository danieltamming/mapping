#!/bin/bash

# downloads the transit data from the TTC
wget http://opendata.toronto.ca/TTC/routes/OpenData_TTC_Schedules.zip
unzip OpenData_TTC_Schedules.zip -d OpenData_TTC_Schedules
rm OpenData_TTC_Schedules.zip
# create a virtualenvironment with the required packages installed
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
# saves your google maps api key
printf "\nEnter your Google Maps API key.\n"
read api_key
echo "API_KEY=\"$api_key\"" > keys.py