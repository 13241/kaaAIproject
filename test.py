import argparse
import json
import random
import socket
import sys
import traceback
import copy
import time
#-###################################################################################################

from lib import game

from kingandassassins import KingAndAssassinsState, KingAndAssassinsServer, KingAndAssassinsClient


ACTUALTESTNUMBER = 2


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
		
		if self.test == "test1":
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
				# (AP King, AP Knight, Fetter, AP Population/Assassins)
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
		elif self.test == "test2":
			POPULATION = {str(i)+str(j) for i in range(9) for j in range(9)}
			
			BOARD = (
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
				('G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
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
				# (AP King, AP Knight, Fetter, AP Population/Assassins)
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

class KingAndAssassinstest2Client(KingAndAssassinsClient):
	'''
	test2 : Ce test évalue la capacité du pathfinding à se sortir d'une situation ou le chevalier
	doit pousser certains villageois mais pas tous pour atteindre sa destination
	
	Ce test échoue pour l'instant (modifier _stateObjective ou faire une autre fonction pour les chevaliers)
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
					stateObjective = self._stateObjective(peopleStateCopy, kingState, (metaI,metaJ), (metaX,metaY), 'm', 13, 2)
					finalCommandsList += stateObjective['movesList']
					return json.dumps({'actions': finalCommandsList}, separators=(',', ':'))
				else:
					return json.dumps({'actions': []}, separators=(',', ':'))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")
			
class KingAndAssassinstest1Client(KingAndAssassinsClient):
	'''
	test1 : Ce teste évalue la performance des fonctions de pathfinding pour des pions de type 
	villageois sur un terrain sans toit encombré par d'autres villageois.
	Le terrain est un labyrinthe qui se résout en 28 déplacements dont 10 détours (autrement dit :
	20 déplacements servent à contourner des obstacles, et la distance avec l'objectif est de 8)
	
	Ce test réussit en 120-130 secondes. (=> améliorer _minimizeObjective pour réduire ce temps)
	On ne devra jamais calculer de déplacement aussi complexe dans une partie réelle, 
	réduire la durée de ce test n'est donc pas une priorité.
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
					stateObjective = self._minimizeObjective(peopleStateCopy, kingState, (metaI,metaJ), (metaX,metaY), 'm', metaAP, False)
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