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

NAME
   ./sparkySPSetup.py
   SparkPost Service Provider tool for creating subaccounts, and creating and deleting subaccount domains.

SYNOPSIS
  ./sparkySPSetup.py action [files]

MANDATORY PARAMETERS
    action
         -createsub subfile_in
             subfile_in           text file, each line containing a subaccount name

         -deletesub               ** currently unsupported in Sparkpost

         -viewsub subfile_in      View the subaccounts given in the input file

         -createdomains domfile_in [bindfile_out]
             domfile_in           .csv format file, each line containing subaccount_id, [domain1, domain2, ..]
             bindfile_out         Optional output text file, containing DNS BIND entries for the domains created.

         -deletedomains domfile_in

         -viewdomains domfile_in [bindfile_out]
                                  Check domains are set up to match the domfile_in and display them.
                                  Optionally make an output text file, containing DNS BIND entries.

USAGE
    The first step is to create the subaccounts, if you do not already have them set up.
    The -createsub option is used for this.  The output is a list of numeric subaccount IDs.  Put these
    numeric IDs in a second file used to create the domains, then use the -createdomain option.

    This two-step approach is used, because you may already have existing subaccounts; and it's not
    currently possible to delete subaccounts in SparkPost.

    An arbitrary number of domains may be given for each subaccount.
    Whitespace from the input files is ignored.
    The -createdomains option takes a second filename. BIND format DNS entries are written to it.
```

## Example output

Start with a simple input file listing the required subaccounts.  Get the numeric subaccount_id values:

```
$ ./sparkySPSetup.py -createsub subac-list.csv 
-createsub :
{"results": {"key": "##redacted##", "short_key": "938f", "label": "key_service_provider1", "subaccount_id": 1}}
{"results": {"key": "##redacted##", "short_key": "a1b3", "label": "key_service_provider2", "subaccount_id": 2}}
{"results": {"key": "##redacted##", "short_key": "4c98", "label": "key_service_provider3", "subaccount_id": 3}}
{"results": {"key": "##redacted##", "short_key": "42e5", "label": "key_service_provider4", "subaccount_id": 4}}
{"results": {"key": "##redacted##", "short_key": "8282", "label": "key_service_provider5", "subaccount_id": 5}}
```

Create the `domfile_in` file, for example `domains-list.csv`:

```
1,sp01.1.junkdomain.com,sp01.2.junkdomain.com
2,sp02.1.junkdomain.com,sp02.2.junkdomain.com
3,sp03.1.junkdomain.com,sp03.2.junkdomain.com
4,sp04.1.junkdomain.com,sp04.2.junkdomain.com
5,sp05.1.junkdomain.com,sp05.2.junkdomain.com,sp05.3.junkdomain.com,sp05.4.junkdomain.com
```

Create those domains, optionally writing DNS entries to a BIND file

```
$ ./sparkySPSetup.py -createdomains domains-list.csv my_bind_file.txt
-createdomains :
Writing DNS entries in my_bind_file.txt
Create subaccount= 1 domain= sp01.1.junkdomain.com : Successfully Created domain.
Create subaccount= 1 domain= sp01.2.junkdomain.com : Successfully Created domain.
Create subaccount= 2 domain= sp02.1.junkdomain.com : Successfully Created domain.
Create subaccount= 2 domain= sp02.2.junkdomain.com : Successfully Created domain.
Create subaccount= 3 domain= sp03.1.junkdomain.com : Successfully Created domain.
Create subaccount= 3 domain= sp03.2.junkdomain.com : Successfully Created domain.
Create subaccount= 4 domain= sp04.1.junkdomain.com : Successfully Created domain.
Create subaccount= 4 domain= sp04.2.junkdomain.com : Successfully Created domain.
Create subaccount= 5 domain= sp05.1.junkdomain.com : Successfully Created domain.
Create subaccount= 5 domain= sp05.2.junkdomain.com : Successfully Created domain.
Create subaccount= 5 domain= sp05.3.junkdomain.com : Successfully Created domain.
Create subaccount= 5 domain= sp05.4.junkdomain.com : Successfully Created domain.
```

The BIND file format is:

```
$ cat my_bind_file.txt 
scph0317.sp01.1.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCti+yhxwuS3OxHlqyth7Ftv3mTO3nB1jIGvyohhFGiZeeQQhYRVLH0rc4hTL8gjmToxmW4+V32gJ4BbX628lLFuEWUfTvN4hJkcBEFN9vKSekKhigqAlbR4UvijbMRvY/V82qEe5jz2tvsln4+72Ada4WqNFreiRYkQvZSCchKmQIDAQAB"
scph0317.sp01.2.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCwoz78He9vVDJ+CreES+p2w8fZx6smDAvPnqir9i18rZVBgns/8zxOslXmUd9NY3jcdOdGZqSnSPDTazD1pe7HmbeZOXov/2kYRK58d7vr1ssYEWa/6iOsOj+dR6ohR5O2xchn52qILX0oyCm6H153Wpdh9lcZ/IBwHE+Sb2krSwIDAQAB"
scph0317.sp02.1.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCs/wjQp1wpFw8o9ekaZ6naaIcIeWP2Z8SQKZImslQMn4I9/3m4RF3RWAd9kHPe/E4jZi3j3uXHb2gMgNSith3E9HCKt0lZSsSmmWfP29moqYGCOclzWLzCzVFAQIRZiRx4oIPpDS7quANC4PyAnbThwWgxJV4NohLx5VGnfbcuDwIDAQAB"
scph0317.sp02.2.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC2kfWRXzV9DyYeGGDJRSPVrSDx3uZa04O/GSYhs9VImg1FlIp+tQ0GxIGks+YAzIuWQ+JoWl2zeRXT9NUE8lZ3cVs0yk0wvKlUMI1JnCEmuKVqdZlhrTG1a7hZou6yu/J+RKApz69qbdLCHVaOuXIbIVYXdiMgAnyWlSsXn7ycpwIDAQAB"
scph0317.sp03.1.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCwit1vQbHEaJzJaPvOygSHRsoq9RGCvpaxbPqfqKDpq0QmO5DyLnD1g87mjYGvFQ7g+0QvlFwyknyuVaWs0bxSIC+vmCLiXWjpbzXi7N5pX0Hpvj1SrexSpPmHvwtSqPl9tlnZYYSWP3Fx0y9QjwDo1LqqquWJs1x84XYcx5x9OQIDAQAB"
scph0317.sp03.2.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3Eu5NxTEPlgkB9IYiLN8haWsWrikmbqzrzz1wkS/h+ohsryqURW1H4+t/aqRBkUE8Dgb7jHcDsdcmFNOyA38pRP6tV8wTdboG1TGRVqt/4ZolUr8xL2/ZBf8ctY+d8T+oROWVNuGTacSLoTY8Pld6iJAJ36IWdoC88yRN5EQLOQIDAQAB"
scph0317.sp04.1.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCUxdsucAWYhGDFYSv/JHShDQk65qWr826raakP4ZWYHyBaZub7QCHYeNV8JzXyK0mNLgE1OujwTpp4JP29rDv+mnUM70jpfNQaT4xAsUC/xn6dfUbqx6S9hsaC7m0csl6yF605Yd4/yWtpiQPQJnHhcvU3vfh8HPnAXRPbjgqvDQIDAQAB"
scph0317.sp04.2.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDPXwpIhJfrM+juO8hbqO2wtdqepudnD9HzShyuPOhYTm+tMQE0dVQty+IQZwNRXisDBmP9m4DweU77oyuZg3+PnhXn9+aKvP1rDvKTr+DSIowppcTivQYnwQWP/Lz/k3RDlWi+o3Ye2koJjTSrVa7pqpz/z4cP5afXEIyk1yReBQIDAQAB"
scph0317.sp05.1.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQ81mzRQKuoEhG1frduJ5sXB1scvZyQJ8aDqZPOX/87zMPqUOuBqXowCpaYEUF/+SI7ZLLqkiqqn+Lp/F4A9gZus2J3KWkBvrnaBbBfzsYtgPTudbYey0uautV3tua7+jMLjnLItr8aU7IwgD8ehIsejZ99LihaGcqQB9oC+j2bQIDAQAB"
scph0317.sp05.2.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDVARz9acM0k9aFcJFtFKiXqQ8yJdVntyPw6jBBnqkpYNA804f0UPHXH6c1pHuRE7BjvUVTzH156rn5iA/k2uTHVVJ1uxo0KcwxeiwfutXGs2QgGJtHL78Rkn1FEv++zhHTxIGr7sdj8cs+vW5K/oA3xC8REKBE6Esd8ewMdD4QzQIDAQAB"
scph0317.sp05.3.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDGoiBzU+flZtOZut6VDmNSoQ6RD3gBgeBuN8PuacxsURM+J8x0oZsk6mapALrd8IB16fkdJTzqQvMLN4MdfM7EYe1FmORikq4/gIjaNSOJEqW50srLeEuDoy6aJDEPki+nZrpdWiWXNhif93QFblGwGrCXcvvI9GcR+cTMb92xLwIDAQAB"
scph0317.sp05.4.junkdomain.com. IN TXT "v=DKIM1\; h=sha256\; k=rsa\; s=email\; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDMhb/0H+YmcjKHnpvq67qZPO7Ji5pr/boMyGFxyqT4+oNfxwsh07k67O8r5M0A7RKTAcJ27NoRzSy4KAkzjbfHQAjS7Ll/X5QRBoDNTdxfYd6aJrnSHTwMlELeaPFiV6AJ/jDnJmQvNoWrELw8Cxj3gjrTUDjAoEtVVoPDOMBTwwIDAQAB"
```

View and check the subaccounts:

```
$ ./sparkySPSetup.py -viewsub domains-list.csv
-viewsub :
{"results": {"id": 1, "name": "service_provider1", "status": "active", "compliance_status": "active"}}
{"results": {"id": 2, "name": "service_provider2", "status": "active", "compliance_status": "active"}}
{"results": {"id": 3, "name": "service_provider3", "status": "active", "compliance_status": "active"}}
{"results": {"id": 4, "name": "service_provider4", "status": "active", "compliance_status": "active"}}
{"results": {"id": 5, "name": "service_provider5", "status": "active", "compliance_status": "active"}}
```

View and check the domains, optionally writing a new BIND file from info pulled back from SparkPost:
```
$ ./sparkySPSetup.py -viewdomains domains-list.csv another_bind_file.txt
-viewdomains :
Writing DNS entries in another_bind_file.txt
Subaccount= 1 domain= sp01.1.junkdomain.com : Domain subaccount set correctly
Subaccount= 1 domain= sp01.2.junkdomain.com : Domain subaccount set correctly
Subaccount= 2 domain= sp02.1.junkdomain.com : Domain subaccount set correctly
Subaccount= 2 domain= sp02.2.junkdomain.com : Domain subaccount set correctly
Subaccount= 3 domain= sp03.1.junkdomain.com : Domain subaccount set correctly
Subaccount= 3 domain= sp03.2.junkdomain.com : Domain subaccount set correctly
Subaccount= 4 domain= sp04.1.junkdomain.com : Domain subaccount set correctly
Subaccount= 4 domain= sp04.2.junkdomain.com : Domain subaccount set correctly
Subaccount= 5 domain= sp05.1.junkdomain.com : Domain subaccount set correctly
Subaccount= 5 domain= sp05.2.junkdomain.com : Domain subaccount set correctly
Subaccount= 5 domain= sp05.3.junkdomain.com : Domain subaccount set correctly
Subaccount= 5 domain= sp05.4.junkdomain.com : Domain subaccount set correctly
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

