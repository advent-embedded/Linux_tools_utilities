#!/bin/bash
sudo dpkg -r chemsw-provision
sudo rm chemsw-provision-1.0.deb 
dpkg-deb --build chemsw-provision-1.0/
sudo dpkg -i chemsw-provision-1.0.deb 
sudo dpkg-reconfigure chemsw-provision
