#!/usr/bin/env python3
#SparkPost example - manage scheduled transmissions via command-line
#Copyright  2017 SparkPost

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

#
# Author: Steve Tuck (March 2017)
#

from __future__ import print_function
import configparser, time, json, sys, os, csv
from datetime import datetime,timedelta
#from sparkpost import SparkPost
#from sparkpost.exceptions import SparkPostAPIException
from pprint import pformat

T = 20                  # Global timeout value for API requests

import requests

# Strip initial and final quotes from strings, if present
def stripQuotes(s):
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    return s

def printHelp():
    progName = sys.argv[0]
    shortProgName = os.path.basename(progName)
    print('\nNAME')
    print('   ' + progName)
    print('   SparkPost Service Provider tool for creating subaccounts, and creating and deleting subaccount domains.\n')
    print('SYNOPSIS')
    print('  ./' + shortProgName + ' action [files]\n')
    print('MANDATORY PARAMETERS')
    print('    action               -createsub subfile_in')
    print('    action               -deletesub      ** currently unsupported in Sparkpost')
    print('    action               -createdomains domfile_in bindfile_out ')
    print('    action               -deletedomains domfile_in')
    print('')
    print('    subfile_in           .csv format file, each line containing subaccount name')
    print('    domfile_in           .csv format file, each line containing subaccount_id, [domain1, domain2, ..]')
    print('')
    print('USAGE')
    print('    The first step is to create the subaccounts, if you do not already have them set up.')
    print('    The -createsub option is used for this.  The output is a list of numeric subaccount IDs.  Put these')
    print('    numeric IDs in a second file used to create the domains, then use the -createdomain option.')
    print('')
    print('    This two-step approach is used, because you may already have existing subaccounts; and it\'s not')
    print('    currently possible to delete subaccounts in SparkPost')
    print('')
    print('    An arbitrary number of domains may be given for each subaccount.')
    print('    Whitespace from the input files is ignored.')
    print('    The -createdomains option takes a second filename. BIND format DNS entries are written to it.')

# Get all the current subaccounts, and return as a Python dict object
def getAllSubAccounts(uri, apiKey):
    #print('To', str(len(recipBatch)).rjust(5, ' '), 'recips: template "' + template + '" binding "' + binding + '" campaign "' + campaign + '" start_time ' + startTime + ' : ', end='', flush=True)

    startT = time.time()
    try:
        path = uri+'/api/v1/subaccounts'
        h = {'Authorization': apiKey, 'Accept': 'application/json'}
        response = requests.get(path, timeout=T, headers=h)
        endT = time.time()
        if(response.status_code == 200):
            return response.json()
        else:
            print('Error:', response.status_code, ':', pformat(response.json()), 'in', round(endT - startT, 3), 'seconds')
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        exit(1)

# Create a named subaccount, returning Python object data
def createSubAccount(uri, apiKey, subAccount):
    startT = time.time()
    try:
        path = uri+'/api/v1/subaccounts'
        h = {'Authorization': apiKey, 'Accept': 'application/json'}
        d = {
            'name' : subAccount,
            'key_label': 'key_'+subAccount,
            'key_grants': ['smtp/inject', 'sending_domains/manage', 'message_events/view', 'suppression_lists/manage'],
        }
        response = requests.post(path, timeout=T, headers=h, data=d)
        endT = time.time()
        if(response.status_code == 200):
            return response.json()
        else:
            print('Error:', response.status_code, ':', pformat(response.json()), 'in', round(endT - startT, 3), 'seconds')
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        return None

# Attach a single sending domain to a numbered subaccount
def createSendingDomain(uri, apiKey, subID, sd):
    startT = time.time()
    try:
        path = uri + '/api/v1/sending-domains'

        #TODO: assign sending domain specifically to the subaccount using a header

        h = {'Authorization': apiKey, 'Accept': 'application/json', 'Content-Type': 'application/json',
             'X-MSYS-SUBACCOUNT': subID}
        d = {
            'domain': sd,
            'generate_dkim': True
        }

        response = requests.post(path, timeout=T, headers=h, data=json.dumps(d) )
        endT = time.time()
        if (response.status_code == 200):
            return response.json()
        else:
            print('Error:', response.status_code, ':', pformat(response.json()), 'in', round(endT - startT, 3), 'seconds')
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        return None

# Delete a single sending domain to a numbered subaccount
def deleteSendingDomain(uri, apiKey, subID, sd):
    startT = time.time()
    try:
        path = uri + '/api/v1/sending-domains' + '/' + sd
        h = {'Authorization': apiKey, 'Accept': 'application/json',
             'X-MSYS-SUBACCOUNT': subID}

        response = requests.delete(path, timeout=T, headers=h)
        endT = time.time()
        if (response.status_code == 204):           # NOTE valid response is not 200
            return True
        else:
            print('Error:', response.status_code, ':', pformat(response.json()), 'in', round(endT - startT, 3),
                  'seconds')
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        return None


# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
# Get parameters from .ini file
# Get connection parameters from .ini file
config = configparser.ConfigParser()
config.read('sparkpost.ini')

try:
    uri = stripQuotes(config['SparkPost']['Host'])
    uri = 'https://' + uri
except:
    uri = 'https://api.sparkpost.com'

# After validation, tore those parameters neatly in a dict structure
p = {
    'apiKey': stripQuotes(config['SparkPost']['Authorization']),
    'uri': uri
}

# Get the command, and file name from the command-line
# Check argument count and validate command-line input.  If a file cannot be opened, then Python will raise an exception
if len(sys.argv) >= 3:
    cmd = str.lower(sys.argv[1])                                        # treat as case-insensitive
    if(cmd == '-view'):
        rq = getAllSubAccounts(p['uri'], p['apiKey'])
        print(json.dumps(rq, indent=4))
        exit(0)

    elif(cmd == '-createsub'):
        print(cmd,':')
        try:
            # Get the list of subaccounts
            f = csv.reader(open(sys.argv[2]))
            for r in f:
                # ONLY column is the subaccount name
                subAccountName = r[0].strip()
                res = createSubAccount(p['uri'], p['apiKey'], subAccountName)
                print(json.dumps(res))
            exit(0)

        except FileNotFoundError as Err:
            print('Error opening file', Err.filename, ':', Err.strerror)
            exit(1)

    elif(cmd == '-deletesub'):
        print('DeleteSub : sorry this is currently unsupported in SparkPost.')

    elif(cmd == '-createdomains'):
        print(cmd,':')
        try:
            # Get the list of subaccounts
            f = csv.reader(open(sys.argv[2]))
            dnsFile = open(sys.argv[3], 'w')
            print('Writing DNS entries in', sys.argv[3])
            for r in f:
                # First column is the subaccount ID, remaining columns are sending domain(s)
                subID = r[0].strip()
                sendingDomains = [i.strip() for i in r[1:] ]            # strip whitespace
                sendingDomains = list(filter(None, sendingDomains))     # strip blank file entries which may be caused e.g. by erroneous trailing commas
                for sd in sendingDomains:
                    print('Create subaccount=', subID, 'domain=', sd, ': ',end='')
                    res = createSendingDomain(p['uri'], p['apiKey'], subID, sd)
                    # Output data in format specifically for Kieran
                    if(res):
                        print(res['results']['message'])
                        dk = res['results']['dkim']
                        dnsFile.write(dk['selector'] + '.' + dk[
                            'signing_domain'] + '.' + ' IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=' + dk['public'] + '"' + '\n')
                    else:
                        print(json.dumps(res))
                        dnsFile.write('*** Error processing '+sd)
            dnsFile.close()
            exit(0)

        except FileNotFoundError as Err:
            print('Error opening file', Err.filename, ':', Err.strerror)
            exit(1)

    elif (cmd == '-deletedomains'):
        print(cmd,':')
        try:
            # Get the list of subaccounts
            f = csv.reader(open(sys.argv[2]))
            for r in f:
                # First column is the subaccount ID, remaining columns are sending domain(s)
                subID = r[0].strip()
                sendingDomains = [i.strip() for i in r[1:] ]            # strip whitespace
                sendingDomains = list(filter(None, sendingDomains))     # strip blank file entries which may be caused e.g. by erroneous trailing commas
                for sd in sendingDomains:
                    print('Delete subaccount=', subID, 'domain=', sd, ': ',end='')
                    res = deleteSendingDomain(p['uri'], p['apiKey'], subID, sd)
                    if(res):
                        print('done')
                    else:
                        print()
            exit(0)

        except FileNotFoundError as Err:
            print('Error opening file', Err.filename, ':', Err.strerror)
            exit(1)

    else:
        printHelp()
        exit(0)

else:
    printHelp()
    exit(0)