!/bin/bash

wget http://opendata.toronto.ca/TTC/routes/OpenData_TTC_Schedules.zip
unzip OpenData_TTC_Schedules.zip -d OpenData_TTC_Schedules
rm OpenData_TTC_Schedules.zip
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
mkdir data