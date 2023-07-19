import requests
import urllib3
import csv
import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


APIC = input("APIC IP Address: ")
USERNAME = input("Username: ")
PASSWORD = getpass.getpass("Password: ")
APIC_URL = "https://"+APIC

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

with open('contracts.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            tenant = str(row[0])
            contractName = str(row[1])
            #addConsumer
            payload = '{"fvRsCons":{"attributes":{"tnVzBrCPName":"'+contractName+'","status":"created,modified"},"children":[]}}'
            addContract = s.post(APIC_URL+"/api/node/mo/uni/tn-Adessa/ap-Servicios-Corporativos/epg-epNutanix-NFS-QA-Test.json", verify=False, data=payload)
            if addContract.status_code == 200:
                print("Added Consumer '"+contractName+"'")
            else:
                print("Error creating contract > '"+contractName)
                print(addContract.content)

            #addProvider
            payload = '{"fvRsProv":{"attributes":{"tnVzBrCPName":"'+contractName+'","status":"created,modified"},"children":[]}}'
            addContract = s.post(APIC_URL+"/api/node/mo/uni/tn-Adessa/ap-Servicios-Corporativos/epg-epNutanix-NFS-QA-Test.json", verify=False, data=payload)
            if addContract.status_code == 200:
                print("Added Provider '"+contractName+"'")
            else:
                print("Error creating contract > '"+contractName)
                print(addContract.content)

            line_count += 1
        else:
            ## bypass csv headers
            line_count += 1
