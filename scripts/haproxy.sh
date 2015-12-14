#!/bin/sh
python3 /bootstrap/bootstrap.py && haproxy -f /bootstrap/haproxy.cfg
