#!/usr/bin/python

import hashlib
import time
import base64
import re
import urllib2
import sys
import os
from datetime import datetime
from datetime import timedelta
import time
import getopt
import requests
import json

COMMANDS = ['acc_check', 'get_chart', 'context', 'service_config', 'createSecureToken', 'oauth']
#ROOT_URL = 'https://main-cherry.musicqubed.com/'
#ROOT_URL = 'https://mtv.musicqubed.com/'
ROOT_URL = 'https://main-kiwi.musicqubed.com/'
TRANSPORT_PATH = 'transport/service/mtv1/8.0/'
XUSERAGENT = 'mtv-tracks/3.12 (Android; mtv1)'


def make_url(path, query_params=None):
	url = ROOT_URL + path
	if query_params != None and query_params != '':
		url = url + '?' + query_params
	return url




def ExecuteServiceConfig(command, salt, installation_id, transport_token):
 	doExecuteServiceConfig(command)

def ExecuteCreateSecureToken(command, salt, installation_id, transport_token):
 	doExecuteCreateSecureToken(salt, installation_id, transport_token)

def ExecuteOAuth(command, salt, installation_id, transport_token):
 	doExecuteOAuth(command, installation_id, transport_token)

def ExecuteAccCheck(command, salt, installation_id, transport_token):
	executeCommand(command, salt, installation_id, transport_token, 'post')
	
def ExecuteGetChart(command, salt, installation_id, transport_token):
	executeCommand(command, salt, installation_id, transport_token, 'get', 'WIDTHXHEIGHT', '480x800')

def ExecuteContext(command, salt, installation_id, transport_token):
	executeCommand(command, salt, installation_id, transport_token, 'get')
	

def main(argv):

	functionHash = {}
	functionHash[COMMANDS[0]] = ExecuteAccCheck
	functionHash[COMMANDS[1]] = ExecuteGetChart
	functionHash[COMMANDS[2]] = ExecuteContext
	functionHash[COMMANDS[3]] = ExecuteServiceConfig
	functionHash[COMMANDS[4]] = ExecuteCreateSecureToken
	functionHash[COMMANDS[5]] = ExecuteOAuth
   
	transportToken = ''
	salt = ''
	command = ''
	installation_id = ''

	try:
	  opts, args = getopt.getopt(argv,"ht:s:c:i:")
	except getopt.GetoptError, error:
	  	print_options_manual()
	  	sys.exit(2)

	for opt, arg in opts:
	  if opt == '-h':
	     print_options_manual()
	     sys.exit()
	  elif opt == "-s":
	     salt = arg
	  elif opt == "-t":
	     transportToken = arg
	  elif opt == "-i":
		 installation_id = arg
	  elif opt == "-c":
	  	 command = arg
	  	 # check if supported command
	  	 if command not in COMMANDS:
	  	 	print 'unrecognized command ' + command
	  	 	command = ''

	
	if command == '':
		 print_options_manual()
		 sys.exit(2)

	

	functionHash[command](command, salt, installation_id, transportToken)


def print_options_manual():
	print 'transport_tester.py -s <salt> -t <transport token> -c <transportcommand> -i <installation_id>'
	print '      E.g. transport_tester.py -s 123456 -t 8abf12b67282 -c acc_check -i c-11e6-aa53-7b672e93e9a'
	print '      E.g. For create secureToken either use -i or -t'
	print '      Supported commands are ' + str(COMMANDS)
	

def generateSecureToken(salt, id):

	# salt value is written in my MQ Useful Info
	# id is either installationID (when used with POST /installations) or transportToken (when used with other transport APIs)

	unix_now = int(time.time())
	hash_object = hashlib.md5(salt + id + salt + str(unix_now) + salt)

	return hash_object.hexdigest(), unix_now


def executeCommand(command, salt, installation_id, transport_token, method, customParamKey = None, customParamVal = None):

	if salt == None or salt == '':
	    print 'missing salt'
	    print_options_manual()
	    sys.exit(2)

	if installation_id == None or installation_id == '':
	    print 'missing installation_id'
	    print_options_manual()
	    sys.exit(2)
	if transport_token == None or transport_token == '':
	    print 'missing transport token'
	    print_options_manual()
	    sys.exit(2)

	secureToken, timestamp = generateSecureToken(salt, transport_token)	

	url = ROOT_URL + TRANSPORT_PATH + command.upper()

	headers = {"Accept" : "application/json", 'X-User-Agent' : XUSERAGENT}
	urlparams = {'USER_NAME':installation_id,'USER_TOKEN':secureToken, 'TIMESTAMP':timestamp}
	if customParamKey != None:
		urlparams[customParamKey] = customParamVal
	if method == 'post':
 		r = requests.post(url, headers = headers, params = urlparams)
 	else:
 		r = requests.get(url, headers = headers, params = urlparams)
 	print r.url
 	print r.status_code
 	try:
		js = r.json()
		print json.dumps(js,indent = 2, sort_keys=True, separators=(',', ': ')).encode('utf8')
 	except Exception, error:
 		print r.text.encode('utf8')

def doExecuteCreateSecureToken(salt, installation_id, transport_token):
	id =''
	id_field = ''
	if installation_id != '':
		id = installation_id
		id_field = 'installation_id'
	else:
		id = transport_token
		id_field = 'transport_token'
	secureToken, timestamp = generateSecureToken(salt, id)
	js = {id_field : id, 'timestamp' : timestamp, 'secureToken' : secureToken}
	print json.dumps(js,indent = 2, sort_keys=True, separators=(',', ': ')).encode('utf8')

def doExecuteServiceConfig(command):
	url = ROOT_URL + TRANSPORT_PATH + command.upper()
	headers = {"Accept": "application/json", 'X-User-Agent': XUSERAGENT}
 	r = requests.get(url, headers=headers)
 	print r.status_code
 	try:
		print json.dumps(r.json(),indent = 2, sort_keys=True, separators=(',', ': ')).encode('utf8')
 	except Exception, error:
 		print error
 	return

def doExecuteOAuth(command, installation_id, transport_token):
	url = ROOT_URL + 'transport/oauth/token'
	headers = {"Accept": "application/json", 'X-User-Agent': XUSERAGENT}
	urlparams = {'grant_type': 'client_credentials','client_id':installation_id, 'client_secret':transport_token}
 	r = requests.post(url, headers = headers, params = urlparams)
 	print r.status_code
 	try:
		print json.dumps(r.json(),indent = 2, sort_keys=True, separators=(',', ': ')).encode('utf8')
 	except Exception, error:
 		print error
 	return

if __name__ == "__main__":
   main(sys.argv[1:])
