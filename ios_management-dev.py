#!/usr/bin/python2.6

import csv
import re #Import Regex library
import os #Import OS for calling 'cpeconnect'
import paramiko
import time


md5keys = {
	"c1900-universalk9-mz.SPA.154-3.M6a.bin" : "010a7d365055d1c466c9f2cde87adc05",
	"c1900-universalk9-mz.SPA.155-3.M7.bin" : "a1a0927da4509fa8cc62f02c10b279f2 ",
	"c2900-universalk9-mz.SPA.154-3.M6a.bin" : "6159eeb84c48dd396f1dfa9a1a03e8dc",
	"c2900-universalk9-mz.SPA.155-3.M7.bin" : "dd58b1f51703d52170e01f90f0986a79",
	"c3900-universalk9-mz.SPA.155-3.M7.bin" : "441134f69088b9d317f1b43e4a8858e9",
	"c3900-universalk9-mz.SPA.154-3.M6a.bin" : "237f33cb535c68df60e8f60528551d4",
	"c3900e-universalk9-mz.SPA.154-3.M6a.bin" : "d696d4a711daf6b2c8fd2f5fc7c94828",
	"c3900e-universalk9-mz.SPA.155-3.M7.bin" : "ca62116304611ba3aeb267c81c0f2056",
	"isr4400-universalk9.03.16.07b.S.155-3.S7b-ext.SPA.bin" : "da518d363defa2dbed8307535a61f0fc"
}

x = 1
print "-" * 60
print('Enter list of CPEs below, type x after last CPE')
print "-" * 60
cpe_list = []
while  x == 1:
	raw_cpe_input = raw_input()
	raw_cpe_input = raw_cpe_input.strip()
	if raw_cpe_input == "x":
		break
	else:
		cpe_list.append(raw_cpe_input)
	
print cpe_list	

#for cpe in cpe_list:
#	print cpe
#	os.system("snmpwalk -c CPE73f1G -v2c " + cpe + " sysDescr.0 | grep Software")




for cpe in cpe_list:
	
#This section directly below is used to derive the password in my specific environment
#If the script is ported to another environment, changes will need to be made as appropriate


###Establish SSH session###
	USER = "admin"
	os.system("cpepwdget " + cpe + "> redirect.txt")
	file = open('redirect.txt')
	output = file.read()
	file.close()
	x,y = output.split()
	PASS = y
	
	remote_conn_pre=paramiko.SSHClient()
	remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	remote_conn_pre.connect(cpe, port=22, username=USER,
	password=PASS,
	look_for_keys=False, allow_agent=False)

	remote_conn = remote_conn_pre.invoke_shell()
	output = remote_conn.recv(65535)

	remote_conn.send("en\n")
	time.sleep(.5)
	output = remote_conn.recv(65535)

	remote_conn.send(PASS + "\n")
	time.sleep(.5)
	output = remote_conn.recv(65535)

###Check Flash images###
	
	remote_conn.send("dir | i bin\n")
	time.sleep(1)
	output = remote_conn.recv(65535)
	output = output.split()
	ios_image_files = filter(lambda x: '.bin' in x, output)
	print "-" * 25
	print("Images found on disk")
	print "-" * 25
	print(cpe, ios_image_files)
	print "-" * 25
	
	
#Identify the hardware based on the image file pattern, whatever the first image in the list is
	
	if "c800" in ios_image_files[0]:
		print("This is a Cisco 892FSP")
		model = "892"
		#new_image = 
	elif "1900" in ios_image_files[0]:
		print("This is a Cisco 1900")
		model = "1900"
		new_image = "c1900-universalk9-mz.SPA.155-3.M7.bin"
	elif "2900" in ios_image_files[0]:
		print("This is a Cisco 2900")
		model = "2900"
		new_image = "c2900-universalk9-mz.SPA.155-3.M7.bin"
	elif "3900-" in ios_image_files[0]:
		print("This is a Cisco 3900")
		model = "3900"
		
	elif "3900e" in ios_image_files[0]:
		print("This is a Cisco 3900e")
		model = "3900e"	
		
	elif "3900e" in ios_image_files[0]:
		print("This is a Cisco 4451-X")
		model = "4400"	
		
	print "-" * 25
	
#If our desired image already exists(in our case .M7), we don't need to carry on with the file transfer, in this case, move to the next router in the cpe_list for loop
	upgrade_image = filter(lambda x: '155-3.M7' in x, ios_image_files)
	if not upgrade_image:
		print("Latest image not found")
	elif '155-3.M7' in upgrade_image[0]:
		print("Device already has 155-3.M7 Image\n")
		print("Go to next devices\n")
		print "-" * 25
		continue #go to next item in cpe_list for loop
	else:
		print("processing error")
		exit()
		
	#Filter out protected images, leaving unwanted images in the final list
	print("images to delete:")
	nominated_for_deletion = [x for x in  ios_image_files if x != 'c1900-universalk9-mz.SPA.155-3.M7.bin']
	nominated_for_deletion = [x for x in  nominated_for_deletion if x != 'c1900-universalk9-mz.SPA.154-3.M6a.bin']
	nominated_for_deletion = [x for x in  nominated_for_deletion if x != 'c1900-universalk9-mz.SPA.155-3.M7.bin']
	nominated_for_deletion = [x for x in  nominated_for_deletion if x != 'c2900-universalk9-mz.SPA.154-3.M6a.bin']
	nominated_for_deletion = [x for x in  nominated_for_deletion if x != 'c2900-universalk9-mz.SPA.155-3.M7.bin']
	nominated_for_deletion = [x for x in  nominated_for_deletion if x != 'c3900-universalk9-mz.SPA.154-3.M6a.bin']
	nominated_for_deletion = [x for x in  nominated_for_deletion if x != 'c3900-universalk9-mz.SPA.155-3.M7.bin']	
		
	if not nominated_for_deletion:
		print("No old images to delete")
	else:
		print nominated_for_deletion
		#proceed = raw_input('Delete images? y or n :\n')
		proceed = y
		#Ask user if they really want to delete the images in the nominated_for_deletion list
		if proceed =='y':
			print "Removing old images"
			#continue
	
			for bin_file in nominated_for_deletion:
				remote_conn.send("delete " + bin_file)
				time.sleep(2)
				output = remote_conn.recv(65535)
				print "-" * 25
				print output
				remote_conn.send("\n")
				time.sleep(2)
				output = remote_conn.recv(65535)
				print "-" * 25
				print output
				remote_conn.send("\n")
				time.sleep(2)
				output = remote_conn.recv(65535)
				print "-" * 25
				print output
				remote_conn.send("\n")
				time.sleep(2)
				output = remote_conn.recv(65535)
				print "-" * 25
				print output
			else:
				print("Preserving old images")
		
	#Code Upload new image file
	#proceed = raw_input('Upload new image? y or n :\n')
	#if proceed =='n':
	#	print "Moving to next device"
	#	continue
	
	#router_model = <something><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	if not new_image:
		new_image = proceed = raw_input('Enter new image name\n')
		new_image = new_image.strip()
	
	print("Uploading image file: " + new_image)
	remote_conn.send("copy ftp flash\n")
	time.sleep(2)
	output = remote_conn.recv(65535)
	#print output
	
	remote_conn.send("212.23.36.150\n")
	time.sleep(2)
	output = remote_conn.recv(65535)
	#print output
	
	remote_conn.send("/ios/2900/" + new_image + "\n")
	time.sleep(2)
	output = remote_conn.recv(65535)
	print output
	
	remote_conn.send("\n")
	time.sleep(2)
	output = remote_conn.recv(65535)
	
	remote_conn.send("\n")
	time.sleep(2)
	output = remote_conn.recv(65535)
	#At this point, the IOS transfer starts
	
	#print output
	print "Uploading image!!!"
	time.sleep(5)
	output = remote_conn.recv(65535)
	print output

	x = 1
	
	while x == 1:
		
		print "!"
		time.sleep(1)
		output = remote_conn.recv(65535)
		output = output.split()
		output = filter(lambda x: 'OK' in x, output)
		if '[OK' in output:
			break
	
	print "image uploaded"

	#Verify md5 hash matches
	time.sleep(1)
	
	print "Expecting hash value of: " + md5keys.get(new_image)
	print "starting verification check"
	
	remote_conn.send("verify /md5 " + new_image + "\n")
	time.sleep(2)
	output = remote_conn.recv(65535)
	#print output
	
	remote_conn.send("\n")
	time.sleep(2)
	output = remote_conn.recv(65535)
	#print output
	
	x = 1
	while x == 1:
		
		print "!"
		time.sleep(1)
		output = remote_conn.recv(65535)
		#print output
		output = output.split()
		#print output
		status = filter(lambda x: 'Done!' in x, output)
		#print output
		if 'Done!' in status:
			break
	#print "loop broken"
	print("Expecting hash value of: " + md5keys.get(new_image))
	print("Calculated MD5 hash: " + output[-3])
	
	
	if md5keys.get(new_image) in output:
		print "Verification succeeded"
	else: 
		print "Verification failed - Hash Mismatch"
		remote_conn_pre.close()
	
	remote_conn_pre.close()		
	print "Moving to next device"

exit()

