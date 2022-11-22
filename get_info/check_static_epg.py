import requests
import urllib3
import csv
import getpass
import json, re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

print("This script to check if Port is already added in EPG")

APIC = input("APIC IP Address: ")
USERNAME = input("Username: ")
PASSWORD = getpass.getpass("Password: ")
APIC_URL = "https://"+APIC

## Edit the next array to check interface in the EPG
listInterface = [
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-01",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-02",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-03",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-04",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-05",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-06",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-07",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-08",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-09",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-10",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-11",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-12",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-13",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-14",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-15",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-16",
    "Vpc-Ntnx-LNX-ING-DCC-03-Node-17"
]

s = requests.Session()

#Login to APIC
payload = '{"aaaUser" : {"attributes": {"name":"'+USERNAME+'","pwd":"'+PASSWORD+'"} } }'
login = s.post(APIC_URL+"/api/aaaLogin.json", verify=False, data=payload)
if login.status_code == 200:
    print("--------------------------------------------------------------------------------------")    
    print("Logged on APIC -> "+ APIC_URL+" with username '"+USERNAME+"'")
    print("--------------------------------------------------------------------------------------\n\n")
else:
    print("Error on login")
    exit()

with open('check_epg.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            # Tenant;AplicationProfile;epg;
            tenant = str(row[0])
            appProfile = str(row[1])
            epg = str(row[2])
            ## add static port to EPG
            getStaticFromEPG = json.loads(s.get(APIC_URL+'/api/node/mo/uni/tn-'+tenant+'/ap-'+appProfile+'/epg-'+epg+'.json?query-target=children&target-subtree-class=fvRsPathAtt&query-target-filter=not(wcard(fvRsPathAtt.dn,"__ui_"))', verify=False).text)
            print ("Checking: "+epg+"")
            for interface in listInterface:
                checkInterface = False;
                for dnInterface in getStaticFromEPG['imdata']:
                    justInterface = re.search("pathep-\[([a-zA-Z0-9_-]+)\]?", dnInterface['fvRsPathAtt']['attributes']['dn']).group(1)
                    if justInterface == interface:
                        print ("\t "+interface+" -> OK")
                        checkInterface = True
                        break                  
                if checkInterface == False:
                    print ("\t "+interface+" -> NO OK")
            line_count += 1
        else:
            ## bypass csv headers
            line_count += 1
