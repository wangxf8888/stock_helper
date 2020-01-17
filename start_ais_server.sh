#!/bin/bash

while true
do
    sleep 1
    COUNT=`ps afux | grep python | grep -v  grep  | grep ais_server.py | wc -l`;
    if [ "$COUNT" == "0" ]
    then
        nohup python ./ais_server.py  8000 0.0.0.0 >> ais_server.nohup &
    fi
done
