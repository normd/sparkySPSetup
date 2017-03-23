# sparkySPSetup
Simple command-line tool to set up Subaccounts and Sending Domains, e.g. for service providers or customers with separate internal departments.

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
    action               -createsub subfile_in
    action               -deletesub      ** currently unsupported in Sparkpost
    action               -createdomains domfile_in bindfile_out 
    action               -deletedomains domfile_in

    subfile_in           .csv format file, each line containing subaccount name
    domfile_in           .csv format file, each line containing subaccount_id, [domain1, domain2, ..]

USAGE
    The first step is to create the subaccounts, if you do not already have them set up.
    The -createsub option is used for this.  The output is a list of numeric subaccount IDs.  Put these
    numeric IDs in a second file used to create the domains, then use the -createdomain option.

    This two-step approach is used, because you may already have existing subaccounts; and it's not
    currently possible to delete subaccounts in SparkPost

    An arbitrary number of domains may be given for each subaccount.
    Whitespace from the input files is ignored.
    The -createdomains option takes a second filename. BIND format DNS entries are written to it.
```

## Example output

```
```

## TODO / possible extensions

## See Also

[SparkPost Developer Hub](https://developers.sparkpost.com/)

[python-sparkpost library](https://github.com/sparkpost/python-sparkpost)

[Getting Started on SparkPost Enterprise](https://support.sparkpost.com/customer/portal/articles/2162798-getting-started-on-sparkpost-enterprise)

