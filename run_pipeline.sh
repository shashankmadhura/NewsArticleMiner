#!/bin/bash
# my sql setup buffer
sleep 5

python3 setupmysql.py

python3 pipeline.py

