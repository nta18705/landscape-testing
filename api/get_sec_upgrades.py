#! /usr/bin/python3

import os, json, sys
from prettytable import prettytable
from termcolor import colored
from landscape_api.base import API, HTTPError
from private import config


def get_sec_patches(api, hostname):
    return api.get_packages(query="hostname:" + hostname, upgrade="true")

def print_vulns(patches):
    headers = ["Name", "Version", "USN", "USN Summary"]
    table = prettytable.PrettyTable(headers)
    for patch in patches:
        if "usn" in patch:
            usn = patch["usn"]["name"]
            summary = patch["usn"]["summary"]
            row = [
                patch["name"],
                patch["version"],
                usn,
                summary
            ]
            table.add_row(row)
    print(colored(table.get_string(title="Security Patches"), "white", attrs=['bold']))

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
    print(colored("[*] There are " + str(len(computers)) + " machines with outstanding security upgrades:", "blue"))
    for computer in computers:
        print("ID: ", computer["id"], "Hostname: ", computer["hostname"])
        patches = get_sec_patches(api, computer["hostname"])
        print_vulns(patches)
        if computer["reboot_required_flag"]:
            print(colored(computer["hostname"] + " requires reboot!", "red", attrs=['bold']))
print(colored("[*] All done!", "green", attrs=['bold']))