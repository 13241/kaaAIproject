#!/usr/bin/env python3

from subprocess import Popen
import random
import socket
from sys import platform as myPlatform
import time
import traceback


try:
	cpuAs = False
	response = input(''.join([
		"Type : \r\n", 
		"2players = humanPlayer vs humanPlayer \r\n",
		"2ias or nothing = IA vs IA \r\n",
		"test1 = run Test1 \r\n"]))
	#response = "IA"
	client = "client"
	file = " kingandassassins.py "
	if response == "2players":
		client = "humanClient"
	elif response == "test1":
		client = "test1Client"
		file = " test.py "
	if myPlatform =="win32":
		'''Windows'''
		command = "cmd.exe /c start"
		cpuAs = True
	elif myPlatform =="darwin":
		'''Mac OS'''#does not work
		command = "open -a python"#wrong command
		cpuAs = True
	if cpuAs:
		host = str(socket.gethostname())
		[Popen((command+file+"server --verbose").split())]
		optA = command+file+client+" a --host "+host+" --verbose"
		optB = command+file+client+" b --host "+host+" --verbose"
		cpuAs = True#random.randint(0,1)
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