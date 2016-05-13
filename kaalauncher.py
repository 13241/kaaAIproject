#!/usr/bin/env python3

from subprocess import Popen
import random
import socket
from sys import platform as myPlatform
import time
import traceback


try:
	cpuAs = False
	response = input("Type IA to play IA's, Press ENTER to play yourself\r\n")
	client = "humanClient"
	if response == "IA":
		client = "client"
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
		[Popen((command+" kingandassassins.py server --verbose").split())]
		optA = command+" kingandassassins.py "+client+" a --host "+host+" --verbose"
		optB = command+" kingandassassins.py "+client+" b --host "+host+" --verbose"
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