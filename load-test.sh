#!/bin/bash
while true; do
    seq 1 10000 | xargs -n1 -P 1000 curl -s http://localhost:5001/api/hello > /dev/null
done