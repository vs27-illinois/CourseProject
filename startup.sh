#!/bin/sh
docker build --tag recipefinder:1.0 .
docker run -d -p 3000:3000 --name recipefinder recipefinder:1.0
