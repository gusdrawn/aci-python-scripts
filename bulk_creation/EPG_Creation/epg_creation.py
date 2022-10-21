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

def createEPG():
    payload = '{"fvAEPg":{"attributes":{"dn":"uni/tn-'+tenant+'/ap-'+appProfile+'/epg-'+name+'","name":"'+name+'","nameAlias":"'+alias+'","rn":"epg-'+name+'","status":"created"},"children":[{"fvRsBd":{"attributes":{"tnFvBDName":"'+name+'","status":"created,modified"},"children":[]}}]}}'
    return payload

with open('epg_creation.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            tenant = str(row[0])
            appProfile = str(row[1])
            createBD = str(row[2])
            name = str(row[3])
            alias = str(row[4])
            if createBD == 'yes':
                ## create BD first                         
                payload = '{"fvBD":{"attributes":{"dn":"uni/tn-'+tenant+'/BD-'+name+'","mac":"00:22:BD:F8:19:FF","arpFlood":"true","name":"'+name+'","nameAlias":"'+alias+'","unicastRoute":"false","rn":"BD-'+name+'","status":"created"},"children":[]}}'
                postBD = s.post(APIC_URL+'/api/node/mo/uni/tn-'+tenant+'/BD-'+name+".json", verify=False, data=payload)
                if postBD.status_code == 200:
                    print("Created Bridge Domain on tenant '"+tenant+"' with name '"+name+"'")
                else:
                    print("Error creating Bridge Domain > '"+postBD)
                    print(postBD.content)
            ## create EPG after
            payload = '{"fvAEPg":{"attributes":{"dn":"uni/tn-'+tenant+'/ap-'+appProfile+'/epg-'+name+'","name":"'+name+'","nameAlias":"'+alias+'","rn":"epg-'+name+'","status":"created"},"children":[{"fvRsBd":{"attributes":{"tnFvBDName":"'+name+'","status":"created,modified"},"children":[]}}]}}'
            postEPG = s.post(APIC_URL+'/api/node/mo/uni/tn-'+tenant+'/ap-'+appProfile+'/epg-'+name+'.json', verify=False, data=payload)
            if postEPG.status_code == 200:
                print("Created EPG on tenant '"+tenant+"' with name "+appProfile+"/"+name)
            else:
                print("Error creating EPG > '"+postEPG)
                print(postEPG.content)
            ## Add Domain in the EPG
            payload = '{"fvRsDomAtt":{"attributes":{"resImedcy":"immediate","tDn":"uni/phys-'+physicalDomain+'","status":"created"},"children":[]}}'
            postDomain = s.post(APIC_URL+'/api/node/mo/uni/tn-'+tenant+'/ap-'+appProfile+'/epg-'+name+'.json', verify=False, data=payload)
            if postDomain.status_code == 200:
                print("Add Domain in EPG '"+name)
            else:
                print("Error add Domain > '"+postDomain)
                print(postDomain.content)
            ## Add VRF just to avoid alarms in ACI
            payload = '{"fvRsCtx":{"attributes":{"tnFvCtxName":"vrfMigracion"},"children":[]}}'
            postVRF = s.post(APIC_URL+'/api/node/mo/uni/tn-'+tenant+'/BD-'+name+'/rsctx.json', verify=False, data=payload)
            if postVRF.status_code == 200:
                print("Add VRF in '"+name)
            else:
                print("Error add VRF > '"+postVRF)
                print(postVRF.content)
            line_count += 1
        else:
            ## bypass csv headers
            line_count += 1
