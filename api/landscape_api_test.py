#! /usr/bin/python3

import os, json, sys
from termcolor import colored
from landscape_api.base import API, HTTPError
from private import config

api = API(config.uri, config.key, config.secret, config.ca)
try:
	computers = api.get_computers(query="alert:security-upgrades")
except HTTPError as e:
	error_string = ("[*] Server returned an error:\n"
				"Code: %d\n"
				"Message: %s\n") % (e.code, e.message)
	print(colored(error_string, "red", attrs=['bold'])) 
	sys.exit(-1)
if len(computers) == 0:
	print(colored("[*] There are no machines with outstanding security upgrades.", "green"))
else:
	print(colored("[*] There are machines with outstanding security upgrades:", "blue"))
	for computer in computers:
		print("ID: ", computer["id"])
		print("Title: ", computer["title"])
		print("Hostname: ", computer["hostname"])
		print("Last ping: ", computer["last_ping_time"])
		if computer["reboot_required_flag"]:
			print(colored(computer["hostname"] + " requires reboot!", "red", attrs=['bold']))
print(colored("[*] All done!", "green", attrs=['bold']))