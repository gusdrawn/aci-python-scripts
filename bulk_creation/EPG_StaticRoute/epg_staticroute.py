import requests
import urllib3
import csv
import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# method: POST
# url: https://10.249.0.5/api/node/mo/uni/tn-Adessa/ap-Web/epg-epWeb-Nutanix/subnet-[10.245.37.176/32].json
# payload{"fvSubnet":{"attributes":{"dn":"uni/tn-Adessa/ap-Web/epg-epWeb-Nutanix/subnet-[10.245.37.176/32]","ctrl":"no-default-gateway","ip":"10.245.37.176/32","scope":"","rn":"subnet-[10.245.37.176/32]","status":"created"},"children":[{"fvEpReachability":{"attributes":{"dn":"uni/tn-Adessa/ap-Web/epg-epWeb-Nutanix/subnet-[10.245.37.176/32]/epReach","rn":"epReach","status":"created"},"children":[{"ipNexthopEpP":{"attributes":{"dn":"uni/tn-Adessa/ap-Web/epg-epWeb-Nutanix/subnet-[10.245.37.176/32]/epReach/nh-[10.245.36.174]","nhAddr":"10.245.36.174","rn":"nh-[10.245.36.174]","status":"created"},"children":[]}}]}}]}}
# response: {"totalCount":"0","imdata":[]}
# timestamp: 11:42:36 DEBUG 

print("This script add bullk EPG Subnet (static route to EndPoint)")

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

with open('epg_staticroute.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            # IP;NextHop;
            tenant = str(row[0])
            ap = str(row[1])
            epg = str(row[2])
            endpoint = str(row[3])
            nexthop = str(row[4])
            ## add static port to EPG
            payload = '{"fvSubnet":{"attributes":{"dn":"uni/tn-'+tenant+'/ap-'+ap+'/epg-'+epg+'/subnet-['+endpoint+'/32]","ctrl":"no-default-gateway","ip":"'+endpoint+'/32","scope":"","rn":"subnet-['+endpoint+'/32]","status":"created"},"children":[{"fvEpReachability":{"attributes":{"dn":"uni/tn-'+tenant+'/ap-'+ap+'/epg-'+epg+'/subnet-['+endpoint+'/32]/epReach","rn":"epReach","status":"created"},"children":[{"ipNexthopEpP":{"attributes":{"dn":"uni/tn-'+tenant+'/ap-'+ap+'/epg-'+epg+'/subnet-['+endpoint+'/32]/epReach/nh-['+nexthop+']","nhAddr":"'+nexthop+'","rn":"nh-['+nexthop+']","status":"created"},"children":[]}}]}}]}}'
            postStatic = s.post(APIC_URL+'/api/node/mo/uni/tn-'+tenant+'/ap-'+ap+'/epg-'+epg+'/subnet-['+endpoint+'/32].json', verify=False, data=payload)
            if postStatic.status_code == 200:
                print("Added EPG Static Route'"+epg+"' (Endpoint: '"+endpoint+"') nexthop: '"+nexthop)
            else:
                print("Error creating Static EPG > '"+postStatic.text)
                print(postStatic.content)
            line_count += 1
        else:
            ## bypass csv headers
            line_count += 1
