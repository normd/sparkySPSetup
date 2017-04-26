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

# file header formats
domfileHdr = ['X-MSYS-SUBACCOUNT', 'domain', 'tracking_domain', 'signing_domain', 'private', 'public', 'selector', 'headers']
trkfileHdr = ['X-MSYS-SUBACCOUNT', 'tracking_domain', 'port', 'secure', 'default']

# Express a Python list object as a comma-separated string
def stringify(l):
    return ','.join([str(i) for i in l])

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
    print('    action')
    print('         -createsub subfile_in')
    print('             subfile_in           text file, each line containing a subaccount name')
    print()
    print('         -deletesub               ** currently unsupported in Sparkpost')
    print()
    print('         -viewsub subfile_in      View the subaccounts (actually shows all of them - not just those in file)')
    print()
    print('         -createdomains domfile_in')
    print('             domfile_in           .csv format file (may have header on line 1) of format:')
    print('                                  '+stringify(domfileHdr) )
    print('                                      tracking_domain onwards are optional parameters.')
    print()
    print('         -deletedomains domfile_in')
    print()
    print('         -viewdomains domfile_in [bindfile_out]')
    print('                                  Check domains are set up to match the domfile_in and display them.')
    print('             bindfile_out         Optional output file, will be written with DNS BIND entries for the sending domains.')
    print()
    print('         -createtrack trkfile_in  Create subaccount-linked tracking domains')
    print('             trkfile_in           .csv format file (may have header on line 1) of format:')
    print('                                  '+stringify(trkfileHdr) )
    print('                                      port, secure (true/false) and default (true/false) are optional parameters.')
    print()
    print('         -deletetrack trkfile_in')
    print()
    print('         -viewtrack trkfile_in [cnamefile_out]')
    print('             cnamefile_out        Optional output file, will be written with DNS BIND entries for the tracking domains.')
    print()
    print('USAGE')
    print('    The first step is to create the subaccounts, if you do not already have them set up.')
    print('    The -createsub option is used for this.  The output is a list of numeric subaccount IDs.  Put these')
    print('    numeric IDs in a further file used to create the domains, then use the -createdomain option.')
    print()
    print('    This two-step approach is used, because you may already have existing subaccounts; and it\'s not')
    print('    currently possible to delete subaccounts in SparkPost.')
    print()
    print('    If you want custom tracking-domains for each sending-domain, then three steps are used:')
    print('      1. create subaccounts')
    print('      2. create custom tracking-domains for those subaccounts')
    print('      3. create sending-domains for those subaccounts')
    print()
    print('    Whitespace from the input files is ignored.')
    print()

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

# Get a specific numbered subaccount, returning Python data
def getSubAccount(uri, apiKey, subID):
    try:
        path = uri + '/api/v1/subaccounts' + '/' + subID
        h = {'Authorization': apiKey, 'Accept': 'application/json'}
        response = requests.get(path, timeout=T, headers=h)
        if response.status_code == 200:
            return response.json()
        else:
            print('Error:', response.status_code, ':', response.text)
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        exit(1)

# Get ALL subaccounts
def getAllSubAccounts(uri, apiKey):
    try:
        path = uri + '/api/v1/subaccounts'
        h = {'Authorization': apiKey, 'Accept': 'application/json'}
        response = requests.get(path, timeout=T, headers=h)
        if response.status_code == 200:
            return response.json()
        else:
            print('Error:', response.status_code, ':', response.text)
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        exit(1)

# -----------------------------------------------------------------------------------------

# Attach a single sending domain to a numbered subaccount.  Returns the JSON stanza if successful, None if error occurs.
#   takes variable parameters -
#       mandatory:  X-MSYS-SUBACCOUNT, domain
#       optional:   tracking_domain
#                   private,public,selector
#                       optional signing_domain,headers
#
def createSendingDomain(uri, apiKey, **kwargs):
    try:
        path = uri + '/api/v1/sending-domains'
        h = {'Authorization': apiKey, 'Accept': 'application/json', 'Content-Type': 'application/json', 'X-MSYS-SUBACCOUNT': kwargs.get('X-MSYS-SUBACCOUNT')}
        d = {'domain': kwargs.get('domain')}

        if 'tracking_domain' in kwargs:                 # Add Tracking Domain attribute only if param is non-blank
            d['tracking_domain'] = kwargs.get('tracking_domain')

        if 'private' in kwargs:
            # We have a predefined dkim key pair and selector (mandatory parts)
            d['generate_dkim'] =False
            d['dkim'] = {
                'private': kwargs.get('private'),
                'public': kwargs.get('public'),
                'selector': kwargs.get('selector')
            }
            # Now handle the optional parts
            if 'signing_domain' in kwargs:
                d['dkim']['signing_domain'] = kwargs.get('signing_domain')
            if 'headers' in kwargs:
                d['dkim']['headers'] = kwargs.get('headers')
        else:
            d['generate_dkim'] = True

        response = requests.post(path, timeout=T, headers=h, data=json.dumps(d) )
        if response.status_code == 200:
            return response.json()
        else:
            print('Error:', response.status_code, ':', response.text )
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        return None

# Delete a single sending domain to a numbered subaccount.  Returns True if successful, None if error occurs
def deleteSendingDomain(uri, apiKey, **kwargs):
    try:
        path = uri + '/api/v1/sending-domains' + '/' + kwargs.get('domain')
        h = {'Authorization': apiKey, 'Accept': 'application/json', 'X-MSYS-SUBACCOUNT': kwargs.get('X-MSYS-SUBACCOUNT')}

        response = requests.delete(path, timeout=T, headers=h)
        if response.status_code == 204:             # NOTE valid response is 204, not 200
            return True
        else:
            print('Error:', response.status_code, ':', response.text)
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        return None

# Get a single sending domain, returning the JSON stanza if domain is found, None if error occurs
def getSendingDomain(uri, apiKey, **kwargs):
    try:
        path = uri + '/api/v1/sending-domains' + '/' + kwargs.get('domain')
        h = {'Authorization': apiKey, 'Accept': 'application/json', 'X-MSYS-SUBACCOUNT': kwargs.get('X-MSYS-SUBACCOUNT')}

        response = requests.get(path, timeout=T, headers=h)
        if (response.status_code == 200):
            return response.json()
        else:
            print('Error:', response.status_code, ':', response.text)
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        return None

# -----------------------------------------------------------------------------------------

# Get a Tracking Domain
def getTrackingDomain(uri, apiKey, **kwargs):
    try:
        path = uri + '/api/v1/tracking-domains' + '/' + kwargs.get('tracking_domain')
        h = {'Authorization': apiKey, 'Accept': 'application/json', 'X-MSYS-SUBACCOUNT': kwargs.get('X-MSYS-SUBACCOUNT')}

        response = requests.get(path, timeout=T, headers=h)
        if (response.status_code == 200):  # NOTE valid response is not 200
            return response.json()
        else:
            print('Error:', response.status_code, ':', response.text)
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        return None

# Create a Tracking Domain.  Currently defaults to port 80 (http) access.  TODO add https access
def createTrackingDomain(uri, apiKey, **kwargs):
    try:
        path = uri + '/api/v1/tracking-domains'
        h = {'Authorization': apiKey, 'Accept': 'application/json', 'Content-Type': 'application/json', 'X-MSYS-SUBACCOUNT': kwargs.get('X-MSYS-SUBACCOUNT')}
        d = {'domain': kwargs.get('tracking_domain')}

        # add optional parameters.  Note care needed in converting string to bool
        if 'port' in kwargs:
            d['port'] = int(kwargs.get('port'))
        if 'secure' in kwargs:
            d['secure'] = kwargs.get('secure').lower() in ('true',1)
        if 'default' in kwargs:
            d['default'] = kwargs.get('default').lower() in ('true',1)

        response = requests.post(path, timeout=T, headers=h, data=json.dumps(d))
        if (response.status_code == 200):  # NOTE valid response is not 200
            return response.json()
        else:
            print('Error:', response.status_code, ':', response.text)
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        return None

# Delete a Tracking Domain
def deleteTrackingDomain(uri, apiKey, **kwargs):
    try:
        path = uri + '/api/v1/tracking-domains' + '/' + kwargs.get('tracking_domain')
        h = {'Authorization': apiKey, 'Accept': 'application/json', 'X-MSYS-SUBACCOUNT': kwargs.get('X-MSYS-SUBACCOUNT')}

        response = requests.delete(path, timeout=T, headers=h)
        if response.status_code == 204:             # NOTE valid response is not 200
            return True
        else:
            print('Error:', response.status_code, ':', response.text)
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

# After validation, store those parameters neatly in a dict structure
p = {
    'apiKey': stripQuotes(config['SparkPost']['Authorization']),
    'uri': uri
}

# Get the command, and file name from the command-line
# Check argument count and validate command-line input.  If a file cannot be opened, then Python will raise an exception
cmd=''
if len(sys.argv) >= 2:
    cmd = str.lower(sys.argv[1])                                        # treat as case-insensitive
    print(cmd, ':')

if len(sys.argv) >= 3:
    try:
        f = csv.reader(open(sys.argv[2]))                               # Get the input data
    except FileNotFoundError as Err:
        print('Error opening file', Err.filename, ':', Err.strerror)
        exit(1)

dnsFname = ''
if len(sys.argv) >= 4:                                                  # Param is optional
    dnsFname = sys.argv[3]
    try:
        dnsFile = open(dnsFname, 'w')
        print('Writing DNS entries in', dnsFname)
    except PermissionError as Err:
        print('Error opening file for writing', Err.filename, ':', Err.strerror)
        exit(1)

if cmd == '-createsub':
    for r in f:
        # ONLY column is the subaccount name
        subAccountName = r[0].strip()
        res = createSubAccount(p['uri'], p['apiKey'], subAccountName)
        print(json.dumps(res))

elif(cmd == '-deletesub'):
    print('DeleteSub : sorry this is currently unsupported in SparkPost.')

elif cmd == '-viewsub':
    res = getAllSubAccounts(p['uri'], p['apiKey'])
    for i in res['results']:
        print('id='+str(i['id']),'\tname="'+i['name']+'"','status='+i['status'],'compliance_status='+i['compliance_status'])

elif cmd == '-createdomains':
    for r in f:
        if f.line_num == 1:                         # Check if header row present
            if 'X-MSYS-SUBACCOUNT' in r:
                hdr = r
                continue
            else:
                hdr = domfileHdr                    # assume default header row
        thisR = {}
        for i,v in enumerate(r):                    # process this row as data
            if v:
                thisR[hdr[i]] = v.strip()
        print('Subaccount=', thisR.get('X-MSYS-SUBACCOUNT'), 'domain=', thisR.get('domain'), 'tracking domain=', thisR.get('tracking_domain'), ': ',end='',flush=True)
        res = createSendingDomain(p['uri'], p['apiKey'], **thisR)
        if(res):
            print(json.dumps(res['results']['message']) )

elif cmd == '-deletedomains':
    for r in f:
        if f.line_num == 1:                         # Check if header row present
            if 'X-MSYS-SUBACCOUNT' in r:
                hdr = r
                continue
            else:
                hdr = domfileHdr                    # assume default header row
        thisR = {}
        for i, v in enumerate(r):                   # process this row as data
            if v:
                thisR[hdr[i]] = v.strip()
        print('Subaccount=', thisR.get('X-MSYS-SUBACCOUNT'), 'domain=', thisR.get('domain'), ': ',end='',flush=True)
        res = deleteSendingDomain(p['uri'], p['apiKey'], **thisR)
        if(res):
            print('done')

elif cmd == '-viewdomains':
    for r in f:
        if f.line_num == 1:                         # Check if header row present
            if 'X-MSYS-SUBACCOUNT' in r:
                hdr = r
                continue
            else:
                hdr = domfileHdr                    # assume default header row
        thisR = {}
        for i, v in enumerate(r):                   # process this row as data
            if v:
                thisR[hdr[i]] = v.strip()
        print('Subaccount=', thisR.get('X-MSYS-SUBACCOUNT'), 'domain=', thisR.get('domain'), ': ',end='',flush=True)
        res = getSendingDomain(p['uri'], p['apiKey'], **thisR)
        if res:
            if res['results']['subaccount_id'] == int(thisR.get('X-MSYS-SUBACCOUNT')):
                print('Domain subaccount set correctly', res)
                # Output data in format specifically for BIND file entries
                if dnsFname:
                    dk = res['results']['dkim']
                    dnsFile.write(dk['selector'] + '._domainkey.' + thisR.get('domain') + '.' + ' IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=' + dk['public'] + '"' + '\n')
            else:
                print('subaccount mismatch:', res)

elif cmd == '-createtrack':
    for r in f:
        if f.line_num == 1:                         # Check if header row present
            if 'X-MSYS-SUBACCOUNT' in r:
                hdr = r
                continue
            else:
                hdr = trkfileHdr                    # assume default header row
        thisR = {}
        for i, v in enumerate(r):                   # process this row as data
            if v:
                thisR[hdr[i]] = v.strip()
        print('Subaccount=', thisR.get('X-MSYS-SUBACCOUNT'), 'tracking domain=', thisR.get('tracking_domain'), ': ', end='', flush=True)
        res = createTrackingDomain(p['uri'], p['apiKey'], **thisR)
        if res:
            print(json.dumps(res) )

elif cmd == '-deletetrack':
    for r in f:
        if f.line_num == 1:                         # Check if header row present
            if 'X-MSYS-SUBACCOUNT' in r:
                hdr = r
                continue
            else:
                hdr = trkfileHdr                    # assume default header row
        thisR = {}
        for i, v in enumerate(r):                   # process this row as data
            if v:
                thisR[hdr[i]] = v.strip()
        print('Subaccount=', thisR.get('X-MSYS-SUBACCOUNT'), 'tracking domain=', thisR.get('tracking_domain'), ': ', end='', flush=True)
        res = deleteTrackingDomain(p['uri'], p['apiKey'], **thisR)
        if res:
            print('done')

elif cmd == '-viewtrack':
    for r in f:
        if f.line_num == 1:                         # Check if header row present
            if 'X-MSYS-SUBACCOUNT' in r:
                hdr = r
                continue
            else:
                hdr = trkfileHdr                    # assume default header row
        thisR = {}
        for i, v in enumerate(r):                   # process this row as data
            if v:
                thisR[hdr[i]] = v.strip()
        print('Subaccount=', thisR.get('X-MSYS-SUBACCOUNT'), 'tracking domain=', thisR.get('tracking_domain'), ': ', end='', flush=True)

        res = getTrackingDomain(p['uri'], p['apiKey'], **thisR)
        print(res)
        if res:
            # Output data in format specifically for BIND file entries
            if dnsFname:
                trk = res['results']['domain']
                dnsFile.write(trk+' CNAME '+ 'spgo.io' + '\n')

else:
    printHelp()

# Tidy up
if dnsFname:
    dnsFile.close()
exit(0)
