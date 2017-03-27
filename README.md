# sparkySPSetup
Command-line tool to set up Subaccounts and Sending Domains, e.g. for service providers or customers with separate internal departments.

Command-line parameters specify
- action to take
- list of Subaccounts and sending domains

## Pre-requisites
Install the [python-sparkpost](https://github.com/sparkpost/python-sparkpost) library using
```
pip install sparkpost
```

Set up a sparkpost.ini file as follows.
  
```
[SparkPost]
# SparkPost Enterprise EU values
Authorization = "##myAPIkey##"
Host = "demo.sparkpostelite.com"
```
The surrounding quotes are needed.

Replace `##myAPIkey##` with your specific, private API key. 

The `host`, attribute is only needed for SparkPost Enterprise service usage; you can omit them for [sparkpost.com](https://www.sparkpost.com/).


## Usage
```
$ ./sparkySPSetup.py
   SparkPost Service Provider tool for creating subaccounts, and creating and deleting subaccount domains.

SYNOPSIS
  ./sparkySPSetup.py action [files]

MANDATORY PARAMETERS
    action
         -createsub subfile_in
             subfile_in           text file, each line containing a subaccount name

         -deletesub               ** currently unsupported in Sparkpost

         -viewsub                 View the subaccounts

         -createdomains domfile_in
             domfile_in           .csv format file, each line containing subaccount_id, domain[, tracking_domain]

         -deletedomains domfile_in

         -viewdomains domfile_in [bindfile_out]
                                  Check domains are set up to match the domfile_in and display them.
             bindfile_out         Optional output text file, containing DNS BIND entries for the domains created.

USAGE
    The first step is to create the subaccounts, if you do not already have them set up.
    The -createsub option is used for this.  The output is a list of numeric subaccount IDs.  Put these
    numeric IDs in a second file used to create the domains, then use the -createdomain option.

    This two-step approach is used, because you may already have existing subaccounts; and it's not
    currently possible to delete subaccounts in SparkPost.

    An arbitrary number of domains may be given for each subaccount, one per line.
    Tracking domain may be specified in the third row, per subaccount.
    Whitespace from the input files is ignored.
```

## Example output

Start with a simple input file listing the required subaccounts, for example `subacc.csv`:
```
service_provider1
service_provider2
service_provider3
service_provider4
service_provider5
```

Create these subaccounts:
```
$ ./sparkySPSetup.py -createsub subac-list.csv 
-createsub :
{"results": {"key": "##redacted##", "short_key": "938f", "label": "key_service_provider1", "subaccount_id": 1}}
{"results": {"key": "##redacted##", "short_key": "a1b3", "label": "key_service_provider2", "subaccount_id": 2}}
{"results": {"key": "##redacted##", "short_key": "4c98", "label": "key_service_provider3", "subaccount_id": 3}}
{"results": {"key": "##redacted##", "short_key": "42e5", "label": "key_service_provider4", "subaccount_id": 4}}
{"results": {"key": "##redacted##", "short_key": "8282", "label": "key_service_provider5", "subaccount_id": 5}}
```

View all subaccounts in this account:
```
$ ./sparkySPSetup.py -viewsub
-viewsub :
id=1    name="service_provider1" status=active compliance_status=active
id=2    name="service_provider2" status=active compliance_status=active
id=3    name="service_provider3" status=active compliance_status=active
id=4    name="service_provider4" status=active compliance_status=active
id=5    name="service_provider5" status=active compliance_status=active
```

Create the `domfile_in` file, for example `domains-list.csv`.  In this example, no tracking-domains are specified.
```
1,sp01.1.junkdomain.com
1,sp01.2.junkdomain.com
2,sp02.1.junkdomain.com
2,sp02.2.junkdomain.com
3,sp03.1.junkdomain.com
3,sp03.2.junkdomain.com
4,sp04.1.junkdomain.com
4,sp04.2.junkdomain.com
5,sp05.1.junkdomain.com
5,sp05.2.junkdomain.com
5,sp05.3.junkdomain.com
5,sp05.4.junkdomain.com
```

Create those domains:
```
$ ./sparkySPSetup.py -createdomains domains-list.csv
-createdomains :
Create subaccount= 1 domain= sp01.1.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 1 domain= sp01.2.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 2 domain= sp02.1.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 2 domain= sp02.2.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 3 domain= sp03.1.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 3 domain= sp03.2.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 4 domain= sp04.1.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 4 domain= sp04.2.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 5 domain= sp05.1.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 5 domain= sp05.2.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 5 domain= sp05.3.junkdomain.com tracking domain=  : "Successfully Created domain."
Create subaccount= 5 domain= sp05.4.junkdomain.com tracking domain=  : "Successfully Created domain."
```

View and check the domains, writing a new BIND file from info pulled back from SparkPost:
```
$ ./sparkySPSetup.py -viewdomains domains-list.csv my_bind_file.txt 
-viewdomains :
Writing DNS entries in my_bind_file.txt
Subaccount= 1 domain= sp01.1.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3td7dIAlDuRtpJuCVMdPDZhdrBtWTNXu0v424WvwjYkmV/VpQ7m6vrubiibU1iO/SPDW4uzn8d2D5jU8GtCdEw2bCvlq+n2Vh67Q2AIZcOiWoGpj9pO+a45WdCj6LEZkxD/3YzeuRbgA9RaHtCaLbUv/qi9etP65VlTSbu9UVKwIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 1}}
Subaccount= 1 domain= sp01.2.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDXfTVWixGMxAjqTwazyvPqVzTPlY6UzJeu1bQ4YqRu2CZS8SNBhyaV4XJh+S9oHcD+xqps/M5wEeix0skMn2uRLjZDRui5OOzSq5GHr2SmO/2uwxqQgTUEUyg6vq62TO1fQQOfr8TP8EQ4T2+g2s7a0K6aIFO+BCjm/mPGi3bopQIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 1}}
Subaccount= 2 domain= sp02.1.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQBG7mRviZWqQDMTfVXkjtcAQMEafS2CtnSBW4U7lmTFh59gF34INUwYESlqQ8cacUfiWECVtc0LFEeuIw+JCGptXIRj37Uodon91awaMHA5W5vptpk42EAR4zC/j4GnFy5SgFF0MfQbnOI2TJK+nNE64CBi4IqlSoph648T+sNwIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 2}}
Subaccount= 2 domain= sp02.2.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQuJ7xD4jbpD5J6ZFt17hRgbIHIP9UlnZrsK6uh2IVC+ia5tjpNL4St8dUgzorSXXI5AJ2WAjzUL80FOA4+OTjCPHUEmOz2dqLtyig0Qm+wtmorWQ1fB1NYi/ULGKy3pqYBDYAvKpGaY4L+b1s2Tgwt61FmeH3Ft7l3qdZ8qj4OQIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 2}}
Subaccount= 3 domain= sp03.1.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBLI5fqWtF59Of08cDm93Bu+DIosB0xL69oU+ZwtgcPgoUKVhIae2lJSWM7bk8uA8f61B0FjPsOLMtjZTH5hqHlci1f9kDMPcsxtDh06AiLIUD7K8QsIHDbgfZ0kGclLFk7FuBg3C2jO27QQFG2zxT7veFEzTU1+2YiSlg3x3d1wIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 3}}
Subaccount= 3 domain= sp03.2.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDYUPD1hh7NzoxYTg43HrhnxxONdNYX9Fa4zhGIvrOHIFZvaQ8kn8Ta3ued04JzprVjWa2Yuhqc0ex7EdNbANB+JeCrbzNrmMnbiP7LvEiOUNUtjzbLBk0JMNYW3DNvmqYQ/96CGfabs7ImH72AOFQWksk+2irgqXtOdV4Imjxl6QIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 3}}
Subaccount= 4 domain= sp04.1.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCsL3CZqSNTTw5ZDUSROm5kEiW3yNzMx8srg87imb1GJRYm9oZmYVktB3aLcwvDX5FAcLI5Et7ilfPp4xEACeDI7kLkmqgvGqYYVhKkQjawWrYGHGLmGTmN5KzFxsksBSEC7j0W1ZWQSVpPZ6UdHZeK2jRIROUOxVLcV3MKnnvgywIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 4}}
Subaccount= 4 domain= sp04.2.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkuWx9Pj7eaGPhhuteNu+EyfKGR2tvGoHnuwNp+SrJyKb5l1CWnajm34koolfgPdNeanYk6lxmvStA4NyC9/UREfIagRmryBEK7CGl50izrGuzjjZZRjoWKdveXHK8MFa8GoIxbop3NdiK85P/H6SEiK7xuPNJNIQ4R0BhJBLegQIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 4}}
Subaccount= 5 domain= sp05.1.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDrxOwP0UX4MYolEQFBDdKUIguETPYC9Ebdx2rtAK47rsiIjRDlROabr0y0hkWBWW3pmxOOIn9nbYNxJaHT3JNE+a58BPYG/kTLPQDcBgzHjNLZBKW0OpF4x3iUa4s9MWLn0KOWXP/WnDD664213SNKRaNIM4MiJBbc01N5aPINNQIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 5}}
Subaccount= 5 domain= sp05.2.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDZfHEY6Cesks2QecsZtHRahQyb2h41DiFPVLtVTH1V8raqm2uUoGWWXoyHf5tKhes5icsJIHDT04462dfOWVp1LosHAfs78+AB16ieBRbml6KA2SAZrxtD72Ks86s9l2D55+jMzB/dpGan19ewR0qzNE31bZ/qH+ckRMxMlKLpaQIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 5}}
Subaccount= 5 domain= sp05.3.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD7HhUFD5ljziKHVczJhfX7VGDRaFBX9tWgiNgv68Q/Ya6c2aGZOxM7oN3xWyZiPFai4MUshB/KUEf0ZhRO8DY1f926gpZDz5b4E264nBDVnG+Z2uPD2pKijY5I22+mcif0SEnRXuPTt5JD8ozmsVv0JnmKc40owO50SzRsnoikTwIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 5}}
Subaccount= 5 domain= sp05.4.junkdomain.com : Domain subaccount set correctly: {'results': {'status': {'ownership_verified': False, 'spf_status': 'unverified', 'abuse_at_status': 'unverified', 'compliance_status': 'pending', 'dkim_status': 'unverified', 'verification_mailbox_status': 'unverified', 'postmaster_at_status': 'unverified'}, 'dkim': {'headers': 'from:to:subject:date', 'public': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCtKiaCMZGyROvXQXuTBtKDAk8N3CQKz4v4ATOzx/+r2ekQC9fXXXnVBes9ZAPDP+0opTn6v1McI95mcdmtkeuqG0937rQT+rgSyf1tFzZGTQNAsZydqON5XaLu/CrekoOhW4HtyOL6yz+UbE004G3UwHzYnFC8YvBAdoWn/jc5OQIDAQAB', 'selector': 'scph0317'}, 'subaccount_id': 5}}
```

The BIND file format is:
```
$ cat my_bind_file.txt 
scph0317._domainkey.sp01.1.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3td7dIAlDuRtpJuCVMdPDZhdrBtWTNXu0v424WvwjYkmV/VpQ7m6vrubiibU1iO/SPDW4uzn8d2D5jU8GtCdEw2bCvlq+n2Vh67Q2AIZcOiWoGpj9pO+a45WdCj6LEZkxD/3YzeuRbgA9RaHtCaLbUv/qi9etP65VlTSbu9UVKwIDAQAB"
scph0317._domainkey.sp01.2.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDXfTVWixGMxAjqTwazyvPqVzTPlY6UzJeu1bQ4YqRu2CZS8SNBhyaV4XJh+S9oHcD+xqps/M5wEeix0skMn2uRLjZDRui5OOzSq5GHr2SmO/2uwxqQgTUEUyg6vq62TO1fQQOfr8TP8EQ4T2+g2s7a0K6aIFO+BCjm/mPGi3bopQIDAQAB"
scph0317._domainkey.sp02.1.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQBG7mRviZWqQDMTfVXkjtcAQMEafS2CtnSBW4U7lmTFh59gF34INUwYESlqQ8cacUfiWECVtc0LFEeuIw+JCGptXIRj37Uodon91awaMHA5W5vptpk42EAR4zC/j4GnFy5SgFF0MfQbnOI2TJK+nNE64CBi4IqlSoph648T+sNwIDAQAB"
scph0317._domainkey.sp02.2.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQuJ7xD4jbpD5J6ZFt17hRgbIHIP9UlnZrsK6uh2IVC+ia5tjpNL4St8dUgzorSXXI5AJ2WAjzUL80FOA4+OTjCPHUEmOz2dqLtyig0Qm+wtmorWQ1fB1NYi/ULGKy3pqYBDYAvKpGaY4L+b1s2Tgwt61FmeH3Ft7l3qdZ8qj4OQIDAQAB"
scph0317._domainkey.sp03.1.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBLI5fqWtF59Of08cDm93Bu+DIosB0xL69oU+ZwtgcPgoUKVhIae2lJSWM7bk8uA8f61B0FjPsOLMtjZTH5hqHlci1f9kDMPcsxtDh06AiLIUD7K8QsIHDbgfZ0kGclLFk7FuBg3C2jO27QQFG2zxT7veFEzTU1+2YiSlg3x3d1wIDAQAB"
scph0317._domainkey.sp03.2.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDYUPD1hh7NzoxYTg43HrhnxxONdNYX9Fa4zhGIvrOHIFZvaQ8kn8Ta3ued04JzprVjWa2Yuhqc0ex7EdNbANB+JeCrbzNrmMnbiP7LvEiOUNUtjzbLBk0JMNYW3DNvmqYQ/96CGfabs7ImH72AOFQWksk+2irgqXtOdV4Imjxl6QIDAQAB"
scph0317._domainkey.sp04.1.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCsL3CZqSNTTw5ZDUSROm5kEiW3yNzMx8srg87imb1GJRYm9oZmYVktB3aLcwvDX5FAcLI5Et7ilfPp4xEACeDI7kLkmqgvGqYYVhKkQjawWrYGHGLmGTmN5KzFxsksBSEC7j0W1ZWQSVpPZ6UdHZeK2jRIROUOxVLcV3MKnnvgywIDAQAB"
scph0317._domainkey.sp04.2.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkuWx9Pj7eaGPhhuteNu+EyfKGR2tvGoHnuwNp+SrJyKb5l1CWnajm34koolfgPdNeanYk6lxmvStA4NyC9/UREfIagRmryBEK7CGl50izrGuzjjZZRjoWKdveXHK8MFa8GoIxbop3NdiK85P/H6SEiK7xuPNJNIQ4R0BhJBLegQIDAQAB"
scph0317._domainkey.sp05.1.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDrxOwP0UX4MYolEQFBDdKUIguETPYC9Ebdx2rtAK47rsiIjRDlROabr0y0hkWBWW3pmxOOIn9nbYNxJaHT3JNE+a58BPYG/kTLPQDcBgzHjNLZBKW0OpF4x3iUa4s9MWLn0KOWXP/WnDD664213SNKRaNIM4MiJBbc01N5aPINNQIDAQAB"
scph0317._domainkey.sp05.2.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDZfHEY6Cesks2QecsZtHRahQyb2h41DiFPVLtVTH1V8raqm2uUoGWWXoyHf5tKhes5icsJIHDT04462dfOWVp1LosHAfs78+AB16ieBRbml6KA2SAZrxtD72Ks86s9l2D55+jMzB/dpGan19ewR0qzNE31bZ/qH+ckRMxMlKLpaQIDAQAB"
scph0317._domainkey.sp05.3.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD7HhUFD5ljziKHVczJhfX7VGDRaFBX9tWgiNgv68Q/Ya6c2aGZOxM7oN3xWyZiPFai4MUshB/KUEf0ZhRO8DY1f926gpZDz5b4E264nBDVnG+Z2uPD2pKijY5I22+mcif0SEnRXuPTt5JD8ozmsVv0JnmKc40owO50SzRsnoikTwIDAQAB"
scph0317._domainkey.sp05.4.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCtKiaCMZGyROvXQXuTBtKDAk8N3CQKz4v4ATOzx/+r2ekQC9fXXXnVBes9ZAPDP+0opTn6v1McI95mcdmtkeuqG0937rQT+rgSyf1tFzZGTQNAsZydqON5XaLu/CrekoOhW4HtyOL6yz+UbE004G3UwHzYnFC8YvBAdoWn/jc5OQIDAQAB"
```

Delete those domains:
```
$ ./sparkySPSetup.py -deletedomains domains-list.csv
-deletedomains :
Delete subaccount= 1 domain= sp01.1.junkdomain.com : done
Delete subaccount= 1 domain= sp01.2.junkdomain.com : done
Delete subaccount= 2 domain= sp02.1.junkdomain.com : done
Delete subaccount= 2 domain= sp02.2.junkdomain.com : done
Delete subaccount= 3 domain= sp03.1.junkdomain.com : done
Delete subaccount= 3 domain= sp03.2.junkdomain.com : done
Delete subaccount= 4 domain= sp04.1.junkdomain.com : done
Delete subaccount= 4 domain= sp04.2.junkdomain.com : done
Delete subaccount= 5 domain= sp05.1.junkdomain.com : done
Delete subaccount= 5 domain= sp05.2.junkdomain.com : done
Delete subaccount= 5 domain= sp05.3.junkdomain.com : done
Delete subaccount= 5 domain= sp05.4.junkdomain.com : done
```

## See Also

[SparkPost Developer Hub](https://developers.sparkpost.com/)

[python-sparkpost library](https://github.com/sparkpost/python-sparkpost)

[Getting Started on SparkPost Enterprise](https://support.sparkpost.com/customer/portal/articles/2162798-getting-started-on-sparkpost-enterprise)

