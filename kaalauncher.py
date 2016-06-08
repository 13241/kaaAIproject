#!/usr/bin/env python3

from subprocess import Popen
import random
import socket
from sys import platform as myPlatform
import time
import traceback


#WARNING : this launcher does NOT work for native console on MAC OS, please install another one or run this file on windows

try:
	cpuAs = False
	response = input(''.join([
		"Type : \r\n", 
		"2players = humanPlayer vs humanPlayer \r\n",
		"2ias or nothing = IA vs IA \r\n",
		"testx = run testx where x is a number \r\n"]))
	#response = "IA"
	server = "server"
	client = "client"
	file = " kingandassassins.py "
	if response == "2players":
		client = "humanClient"
	elif response.count("test")==1:
		server = response+"Server"
		client = response+"Client"
		file = " test.py "
	if myPlatform =="win32":
		'''Windows'''
		command = "cmd.exe /c start"
		cpuAs = True
	elif myPlatform =="darwin":
		'''Mac OS
		native console for mac does not have the equivalent statement of that for windows console, 
		you must install another one or this launcher will not work on your OS
		'''
		command = ""#please insert here the equivalent of windows console command for your own
		cpuAs = True
	if cpuAs:
		host = str(socket.gethostname())
		[Popen((command+file+server+" --verbose").split())]
		optA = command+file+client+" a --host "+host+" --verbose"
		optB = command+file+client+" b --host "+host+" --verbose"
		cpuAs = random.randint(0,1)
		if cpuAs:
			[Popen(optA.split())]
			time.sleep(1)
			[Popen(optB.split())]
		else:
			[Popen(optB.split())]
			time.sleep(1)
			[Popen(optA.split())]
except Exception as e:
	traceback.print_exc(file=sys.stdout)
	a = input("Enter")