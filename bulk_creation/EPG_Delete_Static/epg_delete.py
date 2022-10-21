import requests
import urllib3
import csv
import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# example bridge Domain
# method: POST
# url: https://10.0.0.1/api/node/mo/uni/tn-TenantA/BD-Vlan97.json
# payload{"fvBD":{"attributes":{"dn":"uni/tn-TenantA/BD-Vlan97","mac":"00:22:BD:F8:19:FF","arpFlood":"true","name":"Vlan97","nameAlias":"AliasAlias","unicastRoute":"false","rn":"BD-Vlan97","status":"created"},"children":[]}}
# response: {"totalCount":"0","imdata":[]}

# example EPG
# method: POST
# url: https://10.0.0.1/api/node/mo/uni/tn-TenantA/ap-AppProfileB/epg-Vlan100.json
# payload{"fvAEPg":{"attributes":{"dn":"uni/tn-TenantA/ap-AppProfileB/epg-Vlan100","name":"Vlan97","nameAlias":"AliasAlias","rn":"epg-Vlan100","status":"created"},"children":[{"fvRsBd":{"attributes":{"tnFvBDName":"Vlan96","status":"created,modified"},"children":[]}}]}}
# response: {"totalCount":"0","imdata":[]}

# example Domain
# method: POST
# url: https://10.0.0.1/api/node/mo/uni/tn-TenantA/ap-AppProfileB/epg-Vlan100.json
# payload{"fvRsDomAtt":{"attributes":{"resImedcy":"immediate","tDn":"uni/phys-phys","status":"created"},"children":[]}}
# response: {"totalCount":"0","imdata":[]}

print("This script create EPG and Bridge Domain after creation add Domain and VRF")

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

with open('epg_delete.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            tenant = str(row[0])
            appProfile = str(row[1])
            epg = str(row[2])
            vlan = str(row[3])
            node = str(row[4])
            vpc = str(row[5])
            ## delete static port
            payload = '{"fvRsPathAtt": {"attributes":{"tDn":"topology/pod-1/protpaths-'+node+'/pathep-['+vpc+']", "instrImedcy":"immediate", "status":"deleted"},"children":[]}}'
            postEPG = s.post(APIC_URL+"/api/node/mo/uni/tn-"+tenant+"/ap-"+appProfile+"/epg-"+vlan+".json", verify=False, data=payload)
            if postEPG.status_code == 200:
                print("Delete Static Port "+vpc+"' in EPG "+vlan)
            else:
                print("Error delete Static Port > '"+postEPG)
                print(postEPG.content)
            line_count += 1
        else:
            ## bypass csv headers
            line_count += 1