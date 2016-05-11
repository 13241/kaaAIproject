#!/usr/bin/env python3

from subprocess import Popen
import random
import socket
from sys import platform as myPlatform
import time


try:
	cpuAs = False
	if myPlatform =="win32":
		'''Windows'''
		command = "cmd.exe /c start"
		cpuAs = True
	elif myPlatform =="darwin":
		'''Mac OS'''#not tested...
		command = "open -a python"
		cpuAs = True
	if cpuAs:
		host = str(socket.gethostname())
		[Popen((command+" kingandassassins.py server --verbose").split())]
		optA = command+" kingandassassins.py humanClient a --host "+host+" --verbose"
		optB = command+" kingandassassins.py humanClient b --host "+host+" --verbose"
		cpuAs = False#random.randint(0,1)
		if cpuAs:
			[Popen(optA.split())]
			time.sleep(1)
			[Popen(optB.split())]
		else:
			[Popen(optB.split())]
			time.sleep(1)
			[Popen(optA.split())]
except Exception as e:
	print(e)
	a = input("Enter")