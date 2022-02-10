from ncclient import manager
import xml.etree.ElementTree as ET
import csv
from getpass import getpass
from netmiko import ConnectHandler

#Gather credentials for the lifetime of the script
tacacs_user = input("Enter TACACS username: ")
tacacs_user = tacacs_user.strip()
tacacs_pass = getpass("Enter password ")
tacacs_pass = tacacs_pass.strip()

print("###############----Checking devices with NETCONF support-----#############")
text_file = open("pr_router_list.txt", "r")
lines = text_file.readlines()
text_file.close()

#Open CSV File ready to write data into
outputFile = open('peering_info.csv', 'w', newline='')
outputWriter = csv.writer(outputFile)

for router in lines:
        print("Logging into " + router)
        hostname=str(router)
        hostname=hostname.strip()
        m = manager.connect(host=hostname, port='22', username=tacacs_user,
                            password=tacacs_pass, device_params={'name':'junos'}, hostkey_verify=False)

        nc_show_bgp_neighbor_xml = m.command(command='show bgp neighbor')

#close the netconf session, we don't want to keep it open for no reason
        m.close_session()
        print("Parsing XML Data")
        show_bgp_neighbor_xml = str(nc_show_bgp_neighbor_xml)
        show_bgp_neighbor_root = ET.fromstring(show_bgp_neighbor_xml)

        peer_count = len(show_bgp_neighbor_root[0].getchildren())
        print("BGP Peer count: " + str(peer_count))
        print("Extracting peer data")
        for x in show_bgp_neighbor_root[0]:
                peer_address = x.find('peer-address').text
                peer_description = x.find('description').text
                peer_state = x.find('peer-state').text
                peer_as = x.find('peer-as').text
                outputWriter.writerow([hostname,peer_address,peer_description,peer_state,peer_as])
        print("Logging out of " + router)


print("###############----Checking devices without NETCONF support, falling back to SSH-----#############")

text_file = open("pr_cisco_routers.txt", "r")
ssh_lines = text_file.readlines()
print(ssh_lines)
text_file.close()

for router in ssh_lines:
        print("logging into " + router)
        print(router)
        hostname=str(router)
        hostname=hostname.strip()
        print("Establishing SSH Connection")
        ssh = ConnectHandler(device_type='cisco_ios', host=hostname,  username=tacacs_user, password=tacacs_pass)
        output = ssh.send_command("show bgp neighbor")
        print("Extracting peer data")
        ssh.disconnect()
        peer_row = ['a','b','c','d']
        for line in output.splitlines():
                if 'BGP neighbor is' in line:
                        list_of_chunks = line.split('/ ')
                        peer_address = list_of_chunks[0]
                        peer_address = peer_address.strip()
                        peer_address = peer_address.split()
                        peer_address = peer_address[3]
                        peer_row[0] = peer_address
                if 'Description' in line:
                        list_of_chunks = line.split(':')
                        peer_desc = list_of_chunks[1]
                        peer_desc = peer_desc.strip()
                        peer_row[1] = peer_desc
                if 'BGP state' in line:
                        list_of_chunks = line.split('=')
                        peer_state = list_of_chunks[1]
                        peer_state = peer_state.strip()
                        peer_state = peer_state.split()
                        peer_state = peer_state[0]
                        peer_state = peer_state.split(',')
                        peer_state = peer_state[0]
                        peer_row[2] = peer_state
                if 'Remote AS' in line:
                        list_of_chunks = line.split('/ ')
                        peer_as = list_of_chunks[0]
                        peer_as = peer_as.strip()
                        peer_as = peer_as.split()
                        peer_as = peer_as[2]
                        peer_as = peer_as.replace('"', '')
                        peer_as = peer_as.replace(',', '')
                        peer_row[3] = peer_as
                        print(peer_row)
                        a = peer_row[0]
                        b = peer_row[1]
                        c = peer_row[2]
                        d = peer_row[3]
                        outputWriter.writerow([hostname,a,b,c,d])
        print("Logging out of " + router)
#Close the CSV file as by now we've finished writing to it
outputFile.close()
print("Finished writing to CSV file")
print("Exiting...")
