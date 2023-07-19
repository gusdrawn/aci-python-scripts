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

            payload = '{"vzBrCP":{"attributes":{"dn":"uni/tn-'+tenant+'/brc-'+contractName+'","scope":"global","name":"'+contractName+'","rn":"brc-'+contractName+',"status":"created"},"children":[{"vzSubj":{"attributes":{"dn":"uni/tn-'+tenant+'/brc-'+contractName+'/subj-Permit-Any","name":"Permit-Any","rn":"subj-Permit-Any","status":"created"},"children":[{"vzRsSubjFiltAtt":{"attributes":{"status":"created,modified","tnVzFilterName":"default","directives":"none"},"children":[]}}]}}]}}'

            createContract = s.post(APIC_URL+"/api/node/mo/uni/tn-"+tenant+"/brc-"+contractName+".json", verify=False, data=payload)
            if createContract.status_code == 200:
                print("Created contract on tenant '"+tenant+"' with name '"+contractName+"'")
            else:
                print("Error creating contract > '"+contractName)
                print(createContract.content)
            line_count += 1
        else:
            ## bypass csv headers
            line_count += 1
