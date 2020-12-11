#!/bin/sh
cd frontend
ng build --prod --build-optimizer --base-href /static/
docker build --tag recipefinder:1.0 ..
docker run -d -p 80:80 --name recipefinder recipefinder:1.0
