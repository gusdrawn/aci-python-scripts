import requests
import urllib3
import csv
import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# example add static port
# Viprion01
# method: POST
# url: https://example.com/api/node/mo/uni/tn-Laboratorio/ap-RedesDePaso/epg-epRedesDePaso.json
# payload{"fvRsPathAtt":{"attributes":{"encap":"vlan-999","tDn":"topology/pod-1/protpaths-195-196/pathep-[vpc-Viprion01]","status":"created"},"children":[]}}
# response: {"totalCount":"0","imdata":[]}

# Viprion02
# method: POST
# url: https://example.com/api/node/mo/uni/tn-Laboratorio/ap-RedesDePaso/epg-epRedesDePaso.json
# payload{"fvRsPathAtt":{"attributes":{"encap":"vlan-999","tDn":"topology/pod-1/protpaths-103-104/pathep-[vpc-Viprion02]","status":"created"},"children":[]}}
# response: {"totalCount":"0","imdata":[]}

# N7k
# method: POST
# url: https://example.com/api/node/mo/uni/tn-Laboratorio/ap-RedesDePaso/epg-epRedesDePaso.json
# payload{"fvRsPathAtt":{"attributes":{"encap":"vlan-999","tDn":"topology/pod-1/protpaths-137-138/pathep-[vpc_L2Out-N7K1-N7k2]","status":"created"},"children":[]}}
# response: {"totalCount":"0","imdata":[]}


print("This script add static port in EPG from .csv")

APIC = input("APIC IP Address: ")
USERNAME = input("Username: ")
PASSWORD = getpass.getpass("Password: ")
APIC_URL = "https://"+APIC
physicalDomain = "Domain_for_Static"

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

with open('epg_addstatic.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            # Tenant;AplicationProfile;epg;vlan;node;vpc;
            tenant = str(row[0])
            appProfile = str(row[1])
            epg = str(row[2])
            vlan = str(row[3])
            node = str(row[4])
            vpc = str(row[5])
            ## add static port to EPG
            payload = '{"fvRsPathAtt":{"attributes":{"encap":"vlan-'+vlan+'","tDn":"topology/pod-1/protpaths-'+node+'/pathep-['+vpc+']","status":"created"},"children":[]}}'
            postStatic = s.post(APIC_URL+'/api/node/mo/uni/tn-'+tenant+'/ap-'+appProfile+'/epg-'+epg+'.json', verify=False, data=payload)
            if postStatic.status_code == 200:
                print("Added EPG '"+epg+"' (Encap: '"+vlan+"') to the VPC '"+vpc+"' on nodes '"+node+"'")
            else:
                print("Error creating Static Port EPG > '"+postStatic)
                print(postStatic.content)
            line_count += 1
        else:
            ## bypass csv headers
            line_count += 1
