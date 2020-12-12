#!/bin/sh
docker build --tag recipefinder:1.0 .
docker run -d -p 80:80 --name recipefinder recipefinder:1.0
