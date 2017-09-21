#!/usr/bin/env bash


echo "Starting to test Grafana"

# Create sqlite as the file is not created at setup
/etc/init.d/grafana-server start
sleep 1
/etc/init.d/grafana-server stop

# We need an API key, insert it
echo "Creating the API key into th SQLITE database"
sqlite3 /var/lib/grafana/grafana.db "INSERT INTO 'api_key' VALUES(1,1,'OpsBro','6799edffb8d523e4cbbbc7cea83269576689aeffdd7a88aa775622bacf8ac0bd653a333b94a525d4394a34c9ee1f41bbab25','Admin','2017-09-15 20:00:37','2017-09-15 20:00:37');"

if [ $? != 0 ]; then
    echo "ERROR: the grafana connector test did fail, sqlite did fail"
    exit 2
fi


/etc/init.d/grafana-server start

sleep 1

echo "Checking for authentification"
curl -s -H "Authorization: Bearer eyJrIjoibmhIR0FuRnB0MTN6dFBMTlNMZDZKWjJXakFuR0I2Wk4iLCJuIjoiT3BzQnJvIiwiaWQiOjF9" http://localhost:3000/api/dashboards/home |grep --color timepicker

if [ $? != 0 ]; then
    echo "ERROR: the grafana connector is not OK"
    exit 2
fi


/etc/init.d/opsbro start


sleep 5

echo "Checking if the data source is created, with NAME--opsbro--NODE_UUID as name"

curl -s -H "Authorization: Bearer eyJrIjoibmhIR0FuRnB0MTN6dFBMTlNMZDZKWjJXakFuR0I2Wk4iLCJuIjoiT3BzQnJvIiwiaWQiOjF9" http://localhost:3000/api/datasources | grep --color opsbro
if [ $? != 0 ]; then
    echo "ERROR: the grafana connector is not OK on data source insert"
    exit 2
fi




echo "OK:  grafana export is working"