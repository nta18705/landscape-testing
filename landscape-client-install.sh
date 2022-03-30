#! /usr/bin/bash

## landscape_setup.sh
## Neil Anderson - neil@bastion-networks.com
##
## Configures the client for connection to an on-prem landscape server

if [ $# != "1" ]; then
    echo "Usage: $0 [server]"
    exit 0
fi

server_name = $1

sudo apt-get update
sudo apt-get install -y landscape-client
sudo cp landscape_server_ca.crt /etc/landscape/server.pem
sudo landscape-config --computer-title=$HOSTNAME --account-name=standalone --url=https://$server_name/message-system --ping-url=http://$server_name/ping --ssl-public-key=/etc/landscape/server.pem --silent