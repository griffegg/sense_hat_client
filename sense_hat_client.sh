#!/bin/sh
sleep 10
cd /home/pi/projects/sense_hat_client
sudo wifi connect MountainView
sudo python sense_hat_client.py
