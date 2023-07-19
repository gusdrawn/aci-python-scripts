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

LEAF_UNPAIR = input("Leaf Unpair: ")

#Gracias a la persona que dijo que el par del 133 era el 136 :), solo valido para DCC
if APIC == "10.249.0.4" and LEAF_UNPAIR == "133":
    LEAF_PAIR = 136
else:
    LEAF_PAIR = int(LEAF_UNPAIR)+1
    
INTERFACE_ID = input("Phys Interface: ")

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

leaf1 = []
leaf2 = []
leaf1_interface_name = ""
leaf2_interface_name = ""
interface_description_health = ""
interface_epg_health = ""


print("--------------------------------------------------------------------------------------")
print("Getting current config of Leafs: "+str(LEAF_UNPAIR)+" & "+str(LEAF_PAIR))
print("--------------------------------------------------------------------------------------")
url = APIC_URL+"/api/node/mo/topology/pod-1/node-"+str(LEAF_UNPAIR)+"/sys/phys-[eth"+INTERFACE_ID+"].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg"
response = json.loads(s.get(url, verify=False).text)
leaf1_interface_name = response['imdata'][0]['l1PhysIf']['attributes']['pathSDescr']
for epg in response['imdata'][0]['l1PhysIf']['children'][0]['pconsCtrlrDeployCtx']['children']:
    epg_name = epg['pconsResourceCtx']['attributes']['ctxDn']
    leaf1.append(epg_name)
print("\t+ Leaf "+str(LEAF_UNPAIR)+" config loaded")

url = APIC_URL+"/api/node/mo/topology/pod-1/node-"+str(LEAF_PAIR)+"/sys/phys-[eth"+INTERFACE_ID+"].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg"
response = json.loads(s.get(url, verify=False).text)
leaf2_interface_name = response['imdata'][0]['l1PhysIf']['attributes']['pathSDescr']
for epg in response['imdata'][0]['l1PhysIf']['children'][0]['pconsCtrlrDeployCtx']['children']:
    epg_name = epg['pconsResourceCtx']['attributes']['ctxDn']
    leaf2.append(epg_name)
print("\t+ Leaf "+str(LEAF_PAIR)+" config loaded")


print("--------------------------------------------------------------------------------------")
print("Checking if both interface descriptions are equals")
print("--------------------------------------------------------------------------------------")
print("\t+ Leaf "+str(LEAF_UNPAIR)+" description: " + leaf1_interface_name)
print("\t+ Leaf "+str(LEAF_PAIR)+" description: " + leaf2_interface_name)
if(leaf1_interface_name == leaf2_interface_name):
    interface_description_health = "OK - Both are equals"
else:
    interface_description_health = "There is an mismatch on description names, solve this and try again. :)"
print("\n*** Health Check: " + interface_description_health + " ***")

print("--------------------------------------------------------------------------------------")
print("Checking if both interface have same EPG's deployed")
print("--------------------------------------------------------------------------------------")
print("\t+ Leaf "+str(LEAF_UNPAIR)+" EPG Count: " + str(len(leaf1)))
print("\t+ Leaf "+str(LEAF_PAIR)+" EPG Count: " + str(len(leaf2)))
print("\n")
print("\t* Leaf "+str(LEAF_UNPAIR)+" EPGs Resume: ")
for epg_name in leaf1:
    print("\t\t - "+epg_name)

print("\t* Leaf "+str(LEAF_PAIR)+" EPGs Resume: ")
for epg_name in leaf2:
    print("\t\t - "+epg_name)

if leaf1 == leaf2:
    interface_description_health = "Todo bien, todo correcto, y yo que me alegro. :) --- BOTH INTERFACES ON BOTH LEAFS HAVE SAME CONFIG"
else:
    interface_description_health = "Oops, there is an mismatch in the config, solve this and try again."

print("\n*** Health Check: " + interface_description_health + " ***")

print("\n\n\n\n")