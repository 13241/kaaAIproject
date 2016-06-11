#top
import argparse
import json
import random
import socket
import sys
import traceback
import copy
import time

from lib import game

from kingandassassins import KingAndAssassinsState, KingAndAssassinsServer, KingAndAssassinsClient


ACTUALTESTNUMBER = 6
#see the classes below to know what each test stands for (search "#testxclass" where x is a number)

CARDS = None 
POPULATION = None 
BOARD = None 
KNIGHTS = None 
VILLAGERS = None 
PEOPLE = None 
KA_INITIAL_STATE = None
metaX = None
metaY = None
metaAP = None
metaDET = None
metaI = None
metaJ = None

TESTS = {}
for i in range(1,ACTUALTESTNUMBER+1):
	TESTS["test"+str(i)] = {
		"Server":"KingAndAssassinsServer(verbose=args.verbose, CARDS = CARDS, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE).run()",
		"Client":"KingAndAssassinstest"+str(i)+"Client(args.name, (args.host, args.port), verbose=args.verbose, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE)"
		}

class GlobalVariableAffectation():
	def __init__(self, test):
		self.test = test
		global CARDS 
		global POPULATION 
		global BOARD 
		global KNIGHTS 
		global VILLAGERS 
		global PEOPLE 
		global KA_INITIAL_STATE
		global metaX
		global metaY
		global metaAP
		global metaDET
		global metaI
		global metaJ
		
		if self.test == "test1":#test1var
			POPULATION = {str(i)+str(j) for i in range(9) for j in range(9)}
			
			BOARD = (
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G')
			)
			
			KNIGHTS = {}
			
			metaI, metaJ = 4,4
			metaX, metaY = 8,8
			VILLAGERS = {(metaI,metaJ), (0,3), (1,3), (2,2), (3,4), (4,5), (4,7),
				(5,0), (5,1), (5,2), (5,3), (5,4), (5,7), (6,6), (7,1), (7,2),
				(7,3), (7,4), (7,5), (7,7), (7,8), (8,1),
				(8,9), (9,8), (9,9)}
			metaDET = 10
			metaAP = 100
			
			CARDS = (
				(100, 100, True, metaAP),
				(100, 100, True, metaAP)
			)
			
			PEOPLE = [[None for column in range(10)] for row in range(10)]
			
			for coord in KNIGHTS:
				PEOPLE[coord[0]][coord[1]] = 'knight'
				
			for villager, coord in zip(random.sample(POPULATION, len(POPULATION)), VILLAGERS):
				PEOPLE[coord[0]][coord[1]] = villager
				
			KA_INITIAL_STATE = {
				'board': BOARD,
				'people': PEOPLE,
				'castle': [(2, 2, 'N'), (4, 1, 'W')],
				'card': None,
				'king': 'healthy',
				'lastopponentmove': [],
				'arrested': [],
				'killed': {
					'knights': 0,
					'assassins': 0
				}
			}
		elif self.test == "test2":#test2var
			POPULATION = {str(i)+str(j) for i in range(9) for j in range(9)}
			
			BOARD = (
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'R', 'G', 'G', 'R', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'R', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'R'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'R'),
				('G', 'G', 'G', 'G', 'G', 'R', 'R', 'G', 'R', 'G')
			)
			
			metaI, metaJ = 4,4
			metaX, metaY = 8,8
			KNIGHTS = {(metaI, metaJ)}
			VILLAGERS = {(5,4), (6,8), (6,9), (7,6), (7,7), (7,8), 
				(8,5), (8,7), (9,4)}
			metaDET = 10
			metaAP = 100
			
			CARDS = (
				(100, 100, True, metaAP),
				(100, 100, True, metaAP)
			)
			
			PEOPLE = [[None for column in range(10)] for row in range(10)]
			
			for coord in KNIGHTS:
				PEOPLE[coord[0]][coord[1]] = 'knight'
			
			PEOPLE[4][5]="assassin"
			
			for villager, coord in zip(random.sample(POPULATION, len(POPULATION)), VILLAGERS):
				PEOPLE[coord[0]][coord[1]] = villager
				
			KA_INITIAL_STATE = {
				'board': BOARD,
				'people': PEOPLE,
				'castle': [(2, 2, 'N'), (4, 1, 'W')],
				'card': None,
				'king': 'healthy',
				'lastopponentmove': [],
				'arrested': [],
				'killed': {
					'knights': 0,
					'assassins': 0
				}
			}
		elif self.test == "test3":#test3var
			POPULATION = {str(i)+str(j) for i in range(9) for j in range(9)}
			
			BOARD = (
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G')
			)
			
			metaI, metaJ = 4,4
			metaX, metaY = 9,9
			KNIGHTS = {(4,5), (4,6), (5,5), (5,7), (6,4), (6,5), 
				(7,4), (7,8), (7,9), (8,4), (8,5), (8,8), (8,9), 
				(9,4), (9,5)}
			VILLAGERS = {(4,3), (5,3), (6,6), (7,5), (8,7)}
				
			metaDET = 10
			metaAP = 100
			
			CARDS = (
				(100, 100, True, metaAP),
				(100, 100, True, metaAP)
			)
			
			PEOPLE = [[None for column in range(10)] for row in range(10)]
			
			for coord in KNIGHTS:
				PEOPLE[coord[0]][coord[1]] = 'knight'
			
			PEOPLE[metaI][metaJ] = 'assassin'
			PEOPLE[metaX][metaY] = 'king'
			
			for villager, coord in zip(random.sample(POPULATION, len(POPULATION)), VILLAGERS):
				PEOPLE[coord[0]][coord[1]] = villager
				
			KA_INITIAL_STATE = {
				'board': BOARD,
				'people': PEOPLE,
				'castle': [(2, 2, 'N'), (4, 1, 'W')],
				'card': None,
				'king': 'healthy',
				'lastopponentmove': [],
				'arrested': [],
				'killed': {
					'knights': 0,
					'assassins': 0
				}
			}
		elif self.test == "test4":#test4var
			POPULATION = {str(i)+str(j) for i in range(9) for j in range(9)}
			
			BOARD = (
				('G', 'G', 'G', 'R', 'G', 'R', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('R', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'R', 'G', 'G', 'G', 'G', 'G', 'G'),
				('R', 'G', 'R', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'R', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('R', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('R', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G')
			)
			
			metaI, metaJ = 4,3
			metaX, metaY = 0,0
			KNIGHTS = {}
			VILLAGERS = {(0,6), (1,2), (3,0), (4,1)}
				
			metaDET = 10
			metaAP = 100
			
			CARDS = (
				(100, 100, True, metaAP),
				(100, 100, True, metaAP)
			)
			
			PEOPLE = [[None for column in range(10)] for row in range(10)]
			
			for coord in KNIGHTS:
				PEOPLE[coord[0]][coord[1]] = 'knight'
			
			PEOPLE[metaI][metaJ] = 'assassin'
			PEOPLE[metaX][metaY] = 'king'
			
			for villager, coord in zip(random.sample(POPULATION, len(POPULATION)), VILLAGERS):
				PEOPLE[coord[0]][coord[1]] = villager
				
			KA_INITIAL_STATE = {
				'board': BOARD,
				'people': PEOPLE,
				'castle': [(2, 2, 'N'), (4, 1, 'W')],
				'card': None,
				'king': 'healthy',
				'lastopponentmove': [],
				'arrested': [],
				'killed': {
					'knights': 0,
					'assassins': 0
				}
			}
		elif self.test == "test5":#test5var
			POPULATION = {str(i)+str(j) for i in range(9) for j in range(9)}
			
			BOARD = (
				('R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'),
				('G', 'G', 'G', 'R', 'G', 'R', 'G', 'R', 'G', 'R'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G')
			)
			
			metaI, metaJ = -1,-1
			metaX, metaY = 0,1
			KNIGHTS = {}
			VILLAGERS = {(3,0), (4,0), (3,1), (4,1), (3,2), (4,2)}
				
			metaDET = 10
			metaAP = 100
			
			CARDS = (
				(100, 100, True, metaAP),
				(100, 100, True, metaAP)
			)
			
			PEOPLE = [[None for column in range(10)] for row in range(10)]
			
			for coord in KNIGHTS:
				PEOPLE[coord[0]][coord[1]] = 'knight'
			
			PEOPLE[metaX][metaY] = 'knight'
			
			for villager, coord in zip(random.sample(POPULATION, len(POPULATION)), VILLAGERS):
				PEOPLE[coord[0]][coord[1]] = villager
				
			KA_INITIAL_STATE = {
				'board': BOARD,
				'people': PEOPLE,
				'castle': [(2, 2, 'N'), (4, 1, 'W')],
				'card': None,
				'king': 'healthy',
				'lastopponentmove': [],
				'arrested': [],
				'killed': {
					'knights': 0,
					'assassins': 0
				}
			}
		elif self.test == "test6":#test6var
			POPULATION = {str(i)+str(j) for i in range(9) for j in range(9)}
			
			BOARD = (
				('G', 'R', 'G', 'R', 'G', 'R', 'G', 'R', 'G', 'R'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G')
			)
			
			metaI, metaJ = -1,-1
			metaX, metaY = 0,0
			KNIGHTS = {}
			VILLAGERS = {(9,9), (9,8), (8,9)}
				
			metaDET = 10
			metaAP = 100
			
			CARDS = (
				(100, 100, True, metaAP),
				(100, 100, True, metaAP)
			)
			
			PEOPLE = [[None for column in range(10)] for row in range(10)]
			
			for coord in KNIGHTS:
				PEOPLE[coord[0]][coord[1]] = 'knight'
			
			PEOPLE[metaX][metaY] = 'vi'
			
			for villager, coord in zip(random.sample(POPULATION, len(POPULATION)), VILLAGERS):
				PEOPLE[coord[0]][coord[1]] = villager
				
			KA_INITIAL_STATE = {
				'board': BOARD,
				'people': PEOPLE,
				'castle': [(2, 2, 'N'), (4, 1, 'W')],
				'card': None,
				'king': 'healthy',
				'lastopponentmove': [],
				'arrested': [],
				'killed': {
					'knights': 0,
					'assassins': 0
				}
			}

class KingAndAssassinstest6Client(KingAndAssassinsClient):#test6class
	'''
	test6 : this test prints the results of radarKingDefensive for a certain situation
	so we can check if the result is really what we expected.
	a villager is alone on the field
	One path's cost is really low, so little that at some point, another path become
	more profitable by deflecting to that one. (second line costs less than first line)
	the function must return the threats to the villager (none) and all the squares analized
	
	this test is successful (see reflexion IA.xlsx to compare with expected result)
	'''
	
	def __init__(self, name, server, verbose=False, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):
		super().__init__(name, server, verbose=verbose, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE)
			
	def _nextmove(self, state):#nextmovefun
		global metaX
		global metaY
		global metaAP
		global metaDET
		global metaI
		global metaJ
		self.TESTSECONDKILL = 0
		self.KILLCOUNTER = 0
		try:
			state = state._state['visible']
			peopleState = state['people']
			peopleStateCopy = copy.deepcopy(peopleState)
			kingState = state['king']
			self.turns+=1
			if state['card'] is None:
				self.turns-=1
				return json.dumps({'assassins': [peopleState[9][9], peopleState[9][8], peopleState[8][9]]}, separators=(',', ':'))
			else:
				APking = state['card'][0]
				APcom = state['card'][1]
				self.CUFFS = state['card'][2]
				APknight = state['card'][3]
				if self._playernb == 0:
					return json.dumps({'actions': []}, separators=(',', ':'))
				else:
					radarKingDefensive = self._radarDefensive(peopleState, (metaX,metaY), 11)
					print("pertinent scanned squares, final priority")
					print(str(radarKingDefensive['prioritiesDictionary']))
					print('')
					print("all scanned squares, base priority")
					toPrint = {}
					for scannedPosition in radarKingDefensive['scannedPositions'].keys():
						try:
							toPrint[radarKingDefensive['scannedPositions'][scannedPosition]['priority']].append(scannedPosition)
						except:
							toPrint[radarKingDefensive['scannedPositions'][scannedPosition]['priority']]=[]
							toPrint[radarKingDefensive['scannedPositions'][scannedPosition]['priority']].append(scannedPosition)
					for priority in toPrint.keys():
						print(str(priority)+" : ")
						for position in toPrint[priority]:
							print(str(position), end = "")
						print("")
					return json.dumps({'actions': []}, separators=(',', ':'))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")			
			
class KingAndAssassinstest5Client(KingAndAssassinsClient):#test5class
	'''
	test5 : this test prints the results of radarKingDefensive for a certain situation
	so we can check if the result is really what we expected.
	a knight is surrounded by some villagers.
	One path's cost is really low, so little that at some point, another path become
	more profitable by deflecting to that one. (second line costs less than first line)
	the function must return the threats to the knight and all the squares analized
	
	this test is successful (see reflexion IA.xlsx to compare with expected result)
	'''
	
	def __init__(self, name, server, verbose=False, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):
		super().__init__(name, server, verbose=verbose, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE)
			
	def _nextmove(self, state):#nextmovefun
		global metaX
		global metaY
		global metaAP
		global metaDET
		global metaI
		global metaJ
		self.TESTSECONDKILL = 0
		self.KILLCOUNTER = 0
		try:
			state = state._state['visible']
			peopleState = state['people']
			peopleStateCopy = copy.deepcopy(peopleState)
			kingState = state['king']
			self.turns+=1
			if state['card'] is None:
				self.turns-=1
				return json.dumps({'assassins': [peopleState[3][0], peopleState[3][1], peopleState[3][2]]}, separators=(',', ':'))
			else:
				APking = state['card'][0]
				APcom = state['card'][1]
				self.CUFFS = state['card'][2]
				APknight = state['card'][3]
				if self._playernb == 0:
					return json.dumps({'actions': []}, separators=(',', ':'))
				else:
					radarKingDefensive = self._radarDefensive(peopleState, (metaX,metaY), 7)
					print("pertinent scanned squares, final priority")
					print(str(radarKingDefensive['prioritiesDictionary']))
					print('')
					print("all scanned squares, base priority")
					toPrint = {}
					for scannedPosition in radarKingDefensive['scannedPositions'].keys():
						try:
							toPrint[radarKingDefensive['scannedPositions'][scannedPosition]['priority']].append(scannedPosition)
						except:
							toPrint[radarKingDefensive['scannedPositions'][scannedPosition]['priority']]=[]
							toPrint[radarKingDefensive['scannedPositions'][scannedPosition]['priority']].append(scannedPosition)
					for priority in toPrint.keys():
						print(str(priority)+" : ")
						for position in toPrint[priority]:
							print(str(position), end = "")
						print("")
					return json.dumps({'actions': []}, separators=(',', ':'))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")			
			
class KingAndAssassinstest4Client(KingAndAssassinsClient):#test4class
	'''
	test4 : this test prints the results of radarKingDefensive for a certain situation
	so we can check if the result is really what we expected.
	the king is surrounded by some villagers and an assassin
	the function must return the threats to the king and all the squares analized
	
	this test is successful (see reflexion IA.xlsx to compare with expected result)
	'''
	
	def __init__(self, name, server, verbose=False, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):
		super().__init__(name, server, verbose=verbose, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE)
			
	def _nextmove(self, state):#nextmovefun
		global metaX
		global metaY
		global metaAP
		global metaDET
		global metaI
		global metaJ
		self.TESTSECONDKILL = 0
		self.KILLCOUNTER = 0
		try:
			state = state._state['visible']
			peopleState = state['people']
			peopleStateCopy = copy.deepcopy(peopleState)
			kingState = state['king']
			self.turns+=1
			if state['card'] is None:
				self.turns-=1
				return json.dumps({'assassins': [peopleState[0][6], peopleState[1][2], peopleState[3][0]]}, separators=(',', ':'))
			else:
				APking = state['card'][0]
				APcom = state['card'][1]
				self.CUFFS = state['card'][2]
				APknight = state['card'][3]
				if self._playernb == 0:
					return json.dumps({'actions': []}, separators=(',', ':'))
				else:
					radarKingDefensive = self._radarDefensive(peopleState, (metaX,metaY), 5)
					print("pertinent scanned squares, final priority")
					print(str(radarKingDefensive['prioritiesDictionary']))
					print('')
					print("all scanned squares, base priority")
					toPrint = {}
					for scannedPosition in radarKingDefensive['scannedPositions'].keys():
						try:
							toPrint[radarKingDefensive['scannedPositions'][scannedPosition]['priority']].append(scannedPosition)
						except:
							toPrint[radarKingDefensive['scannedPositions'][scannedPosition]['priority']]=[]
							toPrint[radarKingDefensive['scannedPositions'][scannedPosition]['priority']].append(scannedPosition)
					for priority in toPrint.keys():
						print(str(priority)+" : ")
						for position in toPrint[priority]:
							print(str(position), end = "")
						print("")
					return json.dumps({'actions': []}, separators=(',', ':'))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")		
			
class KingAndAssassinstest3Client(KingAndAssassinsClient):#test3class
	'''
	test3 : this test evaluates the ability of PATHFINDING to make an assassin kill some knights on his way to reach the king
	and attack him.
	this test does not have any roof
	
	this test is successful
	'''
	
	def __init__(self, name, server, verbose=False, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):
		super().__init__(name, server, verbose=verbose, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE)
			
	def _nextmove(self, state):#nextmovefun
		global metaX
		global metaY
		global metaAP
		global metaDET
		global metaI
		global metaJ
		self.TESTSECONDKILL = 0
		self.KILLCOUNTER = 0
		try:
			state = state._state['visible']
			peopleState = state['people']
			peopleStateCopy = copy.deepcopy(peopleState)
			kingState = state['king']
			self.turns+=1
			if state['card'] is None:
				self.turns-=1
				return json.dumps({'assassins': [peopleState[4][3], peopleState[5][3], peopleState[6][6]]}, separators=(',', ':'))
			else:
				APking = state['card'][0]
				APcom = state['card'][1]
				self.CUFFS = state['card'][2]
				APknight = state['card'][3]
				if self._playernb == 0:
					finalCommandsList = []
					stateObjective = self._minimizeObjective(peopleStateCopy, kingState, (metaI,metaJ), (metaX,metaY), 't', metaAP)
					if stateObjective['completed']:
						finalCommandsList += stateObjective['movesList']
						stateObjective = self._minimizeObjective(stateObjective['peopleState'], stateObjective['kingState'], 
							stateObjective['lastPosition'], (metaX,metaY), 't', stateObjective['APLeft'])
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							if stateObjective['kingState'] == 'dead':
								return json.dumps({'actions': finalCommandsList}, separators=(',', ':'))
					return json.dumps({'actions': []}, separators=(',', ':'))
				else:
					return json.dumps({'actions': []}, separators=(',', ':'))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")			
			
class KingAndAssassinstest2Client(KingAndAssassinsClient):#test2class
	'''
	test2 : this test evaluates the ability of PATHFINDING to make a knight push some villagers
	to successfully reach its destination. But some pushes in this test will make it impossible for him to do so
	this tests has roofs
	
	this test is successful
	'''
	
	def __init__(self, name, server, verbose=False, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):
		super().__init__(name, server, verbose=verbose, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE)
			
	def _nextmove(self, state):#nextmovefun
		global metaX
		global metaY
		global metaAP
		global metaDET
		global metaI
		global metaJ
		self.TESTSECONDKILL = 0
		self.KILLCOUNTER = 0
		try:
			state = state._state['visible']
			peopleState = state['people']
			peopleStateCopy = copy.deepcopy(peopleState)
			kingState = state['king']
			self.turns+=1
			if state['card'] is None:
				self.turns-=1
				return json.dumps({'assassins': [peopleState[6][8], peopleState[6][9], peopleState[7][8]]}, separators=(',', ':'))
			else:
				APking = state['card'][0]
				APcom = state['card'][1]
				self.CUFFS = state['card'][2]
				APknight = state['card'][3]
				if self._playernb == 1:
					finalCommandsList = []
					stateObjective = self._minimizeObjective(peopleStateCopy, kingState, (metaI,metaJ), (metaX,metaY), 'm', metaAP)
					if stateObjective['completed']:
						finalCommandsList += stateObjective['movesList']
					return json.dumps({'actions': finalCommandsList}, separators=(',', ':'))
				else:
					return json.dumps({'actions': []}, separators=(',', ':'))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")
			
class KingAndAssassinstest1Client(KingAndAssassinsClient):#test1class
	'''
	test1 : this test evaluates the performance of PATHFINDING functions for villagers pawns
	on a board without roof where other villagers stand
	the board is a maze of villagers and one of them must reach its destination
	
	this test is successful
	'''
	
	def __init__(self, name, server, verbose=False, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):
		super().__init__(name, server, verbose=verbose, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE)
			
	def _nextmove(self, state):#nextmovefun
		global metaX
		global metaY
		global metaAP
		global metaDET
		global metaI
		global metaJ
		self.TESTSECONDKILL = 0
		self.KILLCOUNTER = 0
		try:
			state = state._state['visible']
			peopleState = state['people']
			peopleStateCopy = copy.deepcopy(peopleState)
			kingState = state['king']
			self.turns+=1
			if state['card'] is None:
				self.turns-=1
				return json.dumps({'assassins': [peopleState[8][9], peopleState[9][8], peopleState[9][9]]}, separators=(',', ':'))
			else:
				APking = state['card'][0]
				APcom = state['card'][1]
				self.CUFFS = state['card'][2]
				APknight = state['card'][3]
				if self._playernb == 0:
					finalCommandsList = []
					stateObjective = self._minimizeObjective(peopleStateCopy, kingState, (metaI,metaJ), (metaX,metaY), 'm', metaAP)
					if stateObjective['completed']:
						finalCommandsList += stateObjective['movesList']
					return json.dumps({'actions': finalCommandsList}, separators=(',', ':'))
				else:
					return json.dumps({'actions': []}, separators=(',', ':'))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")
	
if __name__ == '__main__':#main
	# Create the top-level parser
	parser = argparse.ArgumentParser(description='King & Assassins game')
	subparsers = parser.add_subparsers(
		description='server client',
		help='King & Assassins game components',
		dest='component'
	)
	for test in TESTS.keys():
		# Create the parser for the 'testxServer' subcommand
		server_parser = subparsers.add_parser(test+"Server", help='launch a server')
		server_parser.add_argument('--host', help='hostname (default: localhost)', default='localhost')
		server_parser.add_argument('--port', help='port to listen on (default: 5000)', default=5000)
		server_parser.add_argument('-v', '--verbose', action='store_true')
		# Create the parser for the 'testxClient' subcommand
		client_parser = subparsers.add_parser(test+"Client", help='launch test1Client')
		client_parser.add_argument('name', help='name of the player')
		client_parser.add_argument('--host', help='hostname of the server (default: localhost)',
								   default=socket.gethostbyname(socket.gethostname()))
		client_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
		client_parser.add_argument('-v', '--verbose', action='store_true')
	
	# C
	# Parse the arguments of sys.args
	args = parser.parse_args()
	cmp = str(args.component)
	if cmp.count("Server") == 1:
		try:
			lastIndex = cmp.find("Server")
			testx = cmp[:lastIndex]
			GlobalVariableAffectation(testx)
			exec(TESTS[testx]["Server"])
		except:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")
	elif cmp.count("Client") == 1:
		try:
			lastIndex = cmp.find("Client")
			testx = cmp[:lastIndex]
			GlobalVariableAffectation(testx)
			exec(TESTS[testx]["Client"])
		except:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")
	a = input("Enter")
#bottom