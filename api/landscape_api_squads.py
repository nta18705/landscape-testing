#! /usr/bin/python3

"""
This script is desinged to do mass tagging of hosts in landscape based on CSV files containing hostnames.
It currently adds tags for squads associated with hosts, but will be made more generic over time.  Store 
your data files in a directory called data/.  The following values should be set in private/config.py:

	uri = [the uri to connect to your landscapeserver]
	key = [landscape API key]
	secret = [landscape API secret]
	ca = [path to the CA certificate used to sign the server's certificate]
	squads = [a list of tags/filenames that are used to read data about hosts and tag them]

You need to ensure that you have the CA certificate that was used to sign the server's cert. This may be
a self-signed cert.

The script produces two output files:
	
	untagged_hosts.txt: a list of hostnames that aren't properly tagged
	missing_hosts.txt: a list of hostnames that appeared in the input data but were not found in landscape.

"""

import os, json, sys, csv
from termcolor import colored
from landscape_api.base import API, HTTPError
from private import config


def load_data(data_path, squad):
# Takes a path to the data store and the squad we want to read and returns a list of host names
	hostnames = []
	with open(data_path + squad + ".csv") as input_file:
		reader = csv.reader(input_file, delimiter=",")
		count = 0
		for row in reader:
			if count > 0:
				hostnames.append(row[0])
			count += 1
	input_file.close()
	print (colored(str(count) + " hosts for " + squad, "green"))
	return hostnames

def do_query (api, hostname):
# Runs a query on landscape using the hostname as the query
# Should return 1 result - no checking yet :/
	try:
		result = api.get_computers(query=hostname)
	except HTTPError as e:
		error_string = ("[*] Server returned an error:\n"
				"Code: %d\n"
				"Message: %s\n") % (e.code, e.message)
		print(colored(error_string, "red", attrs=['bold'])) 
		sys.exit(-1)
	return result

def set_tags (api, hostname, tag):
# Sets a new tag for hostname based on the tag parameter
	print(colored("Setting tag " + tag + "for host " + hostname, "blue"))
	try:
		result = api.add_tags_to_computers(query=hostname, tags=tag)
	except HTTPError as e:
		error_string = ("[*] Server returned an error:\n"
				"Code: %d\n"
				"Message: %s\n") % (e.code, e.message)
		print(colored(error_string, "red", attrs=['bold'])) 
		sys.exit(-1)
	return result

def get_tags (api, hostname):
# For a given hostname, get a list of the tags associated with it
	record = do_query(api, hostname)
	#print(record)
	if len(record) < 1:
		print(colored(hostname + " not in landscape!", "red"))
		return None
	if len(record) == 1:
		return record[0]["tags"]
	else:
		print(colored("Found multiple records for " + hostname + "!", "red"))
		return None


def main():
	missing_hosts = []
	untagged_hosts = []
	api = API(config.uri, config.key, config.secret, config.ca)
	for squad in config.squads:
		print(colored("Reading data for " + squad, "blue", attrs=['bold']))
		hosts = load_data("data/", squad)
		print("Hosts for Squad: ", squad)
		for host in hosts:
			tags = get_tags(api, host)
			if tags is not None:
				print(host + ": " + str(tags))
				if squad not in tags:
					print(colored(host + " missing squad tag: " + squad, "blue"))
					set_tags(api, host, squad)
				if len(tags) <= 1:
					untagged_hosts.append(host + "," + squad)
			else:
				missing_hosts.append(host + "," + squad)

	# Now write a file containing hosts we think may be missing tags
	# At the moment, we assume that all hosts must have at least one tag.
	print(colored("The following hosts have missing tags:", "green"))
	with open("untagged_hosts.txt", "w") as untagged_file:
		for untagged_host in untagged_hosts:
			print(colored(untagged_host, "green"))
			untagged_file.write(untagged_host + "\n")
	untagged_file.close()

	# Now write a file containing the hostnames of any hosts we think are missing
	# from landscape.
	print(colored("The following hosts are missing in landscape:", "yellow"))
	with open("missing_hosts.txt", "w") as missing_file:
		for missing_host in missing_hosts:
			print(colored(missing_host, "yellow"))
			missing_file.write(missing_host + "\n")
	missing_file.close()

if __name__ == '__main__':
    main()