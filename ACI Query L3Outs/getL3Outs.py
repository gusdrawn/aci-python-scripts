import requests
import urllib3
import json
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


url = APIC_URL+"/api/node/class/l3extOut.json"
response = json.loads(s.get(url, verify=False).text)


for L3Outs in response['imdata']:
    dn = L3Outs['l3extOut']['attributes']['dn']
    url2 = APIC_URL+"/api/node/mo/"+L3Outs['l3extOut']['attributes']['dn']+".json?query-target=subtree&target-subtree-class=l3extIp"
    response2 = json.loads(s.get(url2, verify=False).text)
    url3 = APIC_URL+"/api/node/mo/"+L3Outs['l3extOut']['attributes']['dn']+".json?query-target=subtree&target-subtree-class=l3extMember"
    response3 = json.loads(s.get(url3, verify=False).text)
    url4 = APIC_URL+"/api/node/mo/"+L3Outs['l3extOut']['attributes']['dn']+".json?query-target=subtree&target-subtree-class=l3extRsPathL3OutAtt"
    response4 = json.loads(s.get(url4, verify=False).text)
    try:
        vip = response2['imdata'][0]['l3extIp']['attributes']['addr']
        memberB = response3['imdata'][0]['l3extMember']['attributes']['addr']
        memberA = response3['imdata'][1]['l3extMember']['attributes']['addr']
        vlan = response4['imdata'][0]['l3extRsPathL3OutAtt']['attributes']['encap']
        
    except:
        vip = "0.0.0.0"
        memberB = "0.0.0.0"
        memberA = "0.0.0.0"
        vlan = "0"
    print(memberA+","+memberB+","+vip+","+vlan+","+dn)