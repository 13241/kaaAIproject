#!/usr/bin/env python3
# kingandassassins.py
# Author: Sébastien Combéfis, Damien Abeloos
# Version: June 6, 2016

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

BUFFER_SIZE = 2048

#see glossary : #CARDS
CARDS = (
	(1, 6, True, 5),
	(1, 5, False, 4),
	(1, 6, True, 5),
	(1, 6, True, 5),
	(1, 5, True, 4),
	(1, 5, False, 4),
	(2, 7, False, 5),
	(2, 7, False, 4),
	(1, 6, True, 5),
	(1, 6, True, 5),
	(2, 7, False, 5),
	(2, 5, False, 4),
	(1, 5, True, 5),
	(1, 5, False, 4),
	(1, 5, False, 4)
)

#see glossary : #POPULATION
POPULATION = {
	'monk', 'plumwoman', 'appleman', 'hooker', 'fishwoman', 'butcher',
	'blacksmith', 'shepherd', 'squire', 'carpenter', 'witchhunter', 'farmer'
}

#see glossary : #BOARD
BOARD = (
	('R', 'R', 'R', 'R', 'R', 'G', 'G', 'R', 'R', 'R'),
	('R', 'R', 'R', 'R', 'R', 'G', 'G', 'R', 'R', 'R'),
	('R', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'R'),
	('R', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
	('R', 'G', 'G', 'G', 'G', 'R', 'R', 'G', 'G', 'G'),
	('G', 'G', 'G', 'G', 'G', 'R', 'R', 'G', 'G', 'G'),
	('R', 'R', 'G', 'G', 'G', 'R', 'R', 'G', 'G', 'G'),
	('R', 'R', 'G', 'G', 'G', 'R', 'R', 'G', 'G', 'G'),
	('R', 'R', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'),
	('R', 'R', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G')
)

#see glossary : #KNIGHTS
KNIGHTS = {(1, 3), (3, 0), (7, 8), (8, 7), (8, 8), (8, 9), (9, 8)}

#see glossary : #VILLAGERS
VILLAGERS = {
	(1, 7), (2, 1), (3, 4), (3, 6), (5, 2), (5, 5),
	(5, 7), (5, 9), (7, 1), (7, 5), (8, 3), (9, 5)
}

#see glossary : #PEOPLE
PEOPLE = [[None for column in range(10)] for row in range(10)]

# Places the king in the right-bottom corner
PEOPLE[9][9] = 'king'

# Places the knights on the board
for coord in KNIGHTS:
	PEOPLE[coord[0]][coord[1]] = 'knight'

# Place the villagers on the board
# random.sample(A, len(A)) returns a list where the elements are shuffled
# this randomizes the position of the villagers
for villager, coord in zip(random.sample(POPULATION, len(POPULATION)), VILLAGERS):
	PEOPLE[coord[0]][coord[1]] = villager

#see glossary : #KA_INITIAL_STATE
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

class KingAndAssassinsState(game.GameState):#stateclass
	'''represents a state for the King & Assassins game.'''
	DIRECTIONS = {
		'E': (0, 1),
		'W': (0, -1),
		'S': (1, 0),
		'N': (-1, 0)
	}
	
	BUFFER_SIZE = 2048

	def __init__(self, initialstate=KA_INITIAL_STATE, POPULATION=POPULATION, BOARD=BOARD):#initfun
		'''
		arguments : 
		-	initialstate : #see glossary : #KA_INITIAL_STATE
		-	POPULATION : #see glossary : #POPULATION
		-	BOARD : #see glossary : #BOARD
		'''
		self.POPULATION = POPULATION
		self.BOARD = BOARD
		self.APKING = 0
		self.APKNIGHT = 0
		self.CUFFS = False
		self.APCOM = 0
		self.SECONDKILL = 0
		self.KILLCOUNT = 0
		super().__init__(initialstate)

	def _nextfree(self, x, y, dir):#nextfreefun
		'''
		this method was not recovered from the official repository : knight push is treated differently in the update method
		
		arguments : 
			see glossary : #action >elements
		'''
		pass #nx, ny = self._getcoord((x, y, dir))

	def update(self, moves, player):#updatefun
		'''
		updates the state of the game each turn and for each action
		each action will be checked and has to follow the rules of the games
		
		arguments : 
			moves : list of actions : see glossary : #action
			player : index of the player (int : 0-1)
		'''
		visible = self._state['visible']
		hidden = self._state['hidden']
		people = visible['people']
		for move in moves:
			# ('move', x, y, dir): moves person at position (x,y) of one cell in direction dir
			if move[0] == 'move':#updatemove
				x, y, d = int(move[1]), int(move[2]), move[3]
				if x<0 or y <0 or x>9 or y>9:
					raise game.InvalidMoveException('{}: cannot select out of the map'.format(move))
				p = people[x][y]
				if p is None:
					raise game.InvalidMoveException('{}: there is no one to move'.format(move))
				nx, ny = self._getcoord((x, y, d))
				if nx<0 or ny <0 or nx>9 or ny>9:
					raise game.InvalidMoveException('{}: cannot move/act out of the map'.format(move))
				new = people[nx][ny]
				if p == 'king' and ((x, y, d) == visible['castle'][0] or (x, y, d) == visible['castle'][1]):
					if self.APKING >= 1:
						self.APKING-=1
						people[x][y], people[nx][ny] = people[nx][ny], people[x][y]
						continue
				# King, assassins, villagers can only move on a free cell
				if p != 'knight' and new is not None:
					raise game.InvalidMoveException('{}: cannot move on a cell that is not free'.format(move))
				if p == 'king' and self.BOARD[nx][ny] == 'R':
					raise game.InvalidMoveException('{}: the king cannot move on a roof'.format(move))
				if p in {'assassin'} | self.POPULATION and player != 0:
					raise game.InvalidMoveException('{}: villagers and assassins can only be moved by player 0'.format(move))
				if p in {'king', 'knight'} and player != 1:
					raise game.InvalidMoveException('{}: the king and knights can only be moved by player 1'.format(move))
				# Move granted if cell is free
				if new is None:
					cost = 0
					if self.BOARD[x][y] == self.BOARD[nx][ny]:
						cost = 1
					elif self.BOARD[x][y] == 'G':
						cost = 1 if p == 'assassin' else 2
					else:
						cost = 0 if p == 'assassin' else 1
					if p == 'king' and self.APKING >= cost:
						self.APKING-=cost
					elif p == 'knight' and self.APKNIGHT >= cost:
						self.APKNIGHT-=cost
					elif p in {'assassin'} | self.POPULATION and self.APCOM >= cost:
						self.APCOM-=cost
					else:
						raise game.InvalidMoveException('{}: not enough AP left'.format(move))
					people[x][y], people[nx][ny] = people[nx][ny], people[x][y]
				# If cell is not free, check if the knight can push villagers
				else:
					news = [(x,y)]
					pushable = False
					knightIsUp = False
					if self.BOARD[x][y] == 'R' or self.BOARD[nx][ny] == 'R':
						knightIsUp = True
					while (self.BOARD[nx][ny] == 'G' or knightIsUp) and new is not None and new != 'knight' and new != 'king':
						news.append((nx,ny))
						if self.BOARD[nx][ny] == 'G':
							knightIsUp = False
						nx, ny = self._getcoord((nx, ny, d))
						if nx<0 or ny<0 or nx>9 or ny>9:
							break
						new = people[nx][ny]
						if new is None and (self.BOARD[nx][ny] == 'G' or knightIsUp):
							pushable = True
					if pushable:
						if self.APKNIGHT >= 1:
							self.APKNIGHT-=1
						else:
							raise game.InvalidMoveException('{}: not enough AP left'.format(move))
						while len(news)>0:
							loc = news.pop()
							people[loc[0]][loc[1]], people[nx][ny] = people[nx][ny], people[loc[0]][loc[1]]
							nx, ny = loc[0], loc[1]
					else:
						raise game.InvalidMoveException("{}: The knight can not push this way".format(move))
			# ('arrest', x, y, dir): arrests the villager in direction dir with knight at position (x, y)
			elif move[0] == 'arrest':#updatearrest
				if player != 1:
					raise game.InvalidMoveException('arrest action only possible for player 1')
				if not self.CUFFS:
					raise game.InvalidMoveException('arrest action only possible if the drawn card says so')
				x, y, d = int(move[1]), int(move[2]), move[3]
				arrester = people[x][y]
				if arrester != 'knight':
					raise game.InvalidMoveException('{}: the attacker is not a knight'.format(move))
				tx, ty = self._getcoord((x, y, d))
				target = people[tx][ty]
				if target not in self.POPULATION:
					raise game.InvalidMoveException('{}: only villagers can be arrested'.format(move))
				if self.BOARD[tx][ty] == 'R' and self.BOARD[x][y] == 'G':
					raise game.InvalidMoveException('{}: arrest action impossible from below'.format(move))
				if self.APKNIGHT >= 1:
					self.APKNIGHT-=1
				else:
					raise game.InvalidMoveException('{}: not enough AP left'.format(move))			
				visible['arrested'].append(people[tx][ty])
				people[tx][ty] = None
			# ('kill', x, y, dir): kills the assassin/knight in direction dir with knight/assassin at position (x, y)
			elif move[0] == 'kill':#updatekill
				x, y, d = int(move[1]), int(move[2]), move[3]
				killer = people[x][y]
				cost = 0
				if killer == 'assassin' and player != 0:
					raise game.InvalidMoveException('{}: kill action for assassin only possible for player 0'.format(move))
				if killer == 'knight' and player != 1:
					raise game.InvalidMoveException('{}: kill action for knight only possible for player 1'.format(move))
				tx, ty = self._getcoord((x, y, d))
				target = people[tx][ty]
				if target is None:
					raise game.InvalidMoveException('{}: there is no one to kill'.format(move))
				if self.BOARD[tx][ty] == 'R' and self.BOARD[x][y] == 'G':
					raise game.InvalidMoveException('{}: kill action impossible from below'.format(move))
				if killer == 'assassin' and target == 'knight':
					if self.KILLCOUNT >= 2:
						raise game.InvalidMoveException('{}: you can only kill 2 knights per turn'.format(move))
					cost = 1 + self.SECONDKILL
					self.SECONDKILL = 1
					self.KILLCOUNT+=1
					if self.APCOM >= cost:
						self.APCOM-=cost
					else:
						raise game.InvalidMoveException('{}: not enough AP left'.format(move))
					visible['killed']['knights'] += 1
					people[tx][ty] = None
				elif killer == 'knight' and target == 'assassin':
					if self.APKNIGHT >= 1:
						self.APKNIGHT-=1
					else:
						raise game.InvalidMoveException('{}: not enough AP left'.format(move))
					visible['killed']['assassins'] += 1
					people[tx][ty] = None
				else:
					raise game.InvalidMoveException('{}: forbidden kill'.format(move))
			# ('attack', x, y, dir): attacks the king in direction dir with assassin at position (x, y)
			elif move[0] == 'attack':#updateattack
				if player != 0:
					raise game.InvalidMoveException('attack action only possible for player 0')
				x, y, d = int(move[1]), int(move[2]), move[3]
				attacker = people[x][y]
				if attacker != 'assassin':
					raise game.InvalidMoveException('{}: the attacker is not an assassin'.format(move))
				tx, ty = self._getcoord((x, y, d))
				target = people[tx][ty]
				if target != 'king':
					raise game.InvalidMoveException('{}: only the king can be attacked'.format(move))
				if self.APCOM >=2:
					self.APCOM-=2
				else:
					raise game.InvalidMoveException('{}: not enough AP left'.format(move))
				visible['king'] = 'injured' if visible['king'] == 'healthy' else 'dead'
			# ('reveal', x, y): reveals villager at position (x,y) as an assassin
			elif move[0] == 'reveal':#updatereveal
				if player != 0:
					raise game.InvalidMoveException('raise action only possible for player 0')
				x, y = int(move[1]), int(move[2])
				p = people[x][y]
				if p not in hidden['assassins']:
					raise game.InvalidMoveException('{}: the specified villager is not an assassin'.format(move))
				people[x][y] = 'assassin'
		# If assassins' team just played, draw a new card
		if player == 0:
			visible['card'] = hidden['cards'].pop()
			self.APKING = visible['card'][0]
			self.APKNIGHT = visible['card'][1]
			self.CUFFS = visible['card'][2]
			self.APCOM = visible['card'][3]
			self.SECONDKILL = 0
			self.KILLCOUNT = 0
			
	def _getcoord(self, coord):#getcoordfun
		'''
		returns a tuple of coordinates updated after a move in a certain direction
		
		arguments : 
			coord : (x, y, dir)
				see glossary : #action >elements
		
		returns :
			(x, y) see glossary : #action >elements
		'''
		return tuple(coord[i] + KingAndAssassinsState.DIRECTIONS[coord[2]][i] for i in range(2))

	def winner(self):#winnerfun
		'''
		returns differents values for an ended game
		does nothing for an ongoing game
		
		returns : x such as x is included in [-1,1]
		or
		returns : nothing
		'''
		visible = self._state['visible']
		hidden = self._state['hidden']
		# The king reached the castle
		for doors in visible['castle']:
			coord = self._getcoord(doors)
			if visible['people'][coord[0]][coord[1]] == 'king':
				return 1
		# The are no more cards
		if len(hidden['cards']) == 0:
			return 0
		# The king has been killed
		if visible['king'] == 'dead':
			return 0
		# All the assassins have been arrested or killed
		if visible['killed']['assassins'] + len(set(visible['arrested']) & hidden['assassins']) == 3:
			return 1
		return -1

	def isinitial(self):#isinitialfun
		'''
		States if the board is untouched (True) or not (False)
		
		returns : (bool)
		'''
		return self._state['hidden']['assassins'] is None

	def setassassins(self, assassins):#setassassinsfun
		'''
		Registers assassins in the hidden part of the ongoing game data as a set
		
		arguments :
			assassins : collection of str
		'''
		self._state['hidden']['assassins'] = set(assassins)

	def prettyprint(self):#prettyprintfun
		'''
		Prints the state of the game (console)
		'''
		visible = self._state['visible']
		hidden = self._state['hidden']
		result = ''
		if hidden is not None:
			result += '   - Assassins: {}\n'.format(hidden['assassins'])
			result += '   - Remaining cards: {}\n'.format(len(hidden['cards']))
		result += '   - Current card: {}\n'.format(visible['card'])	
		result += '   - King: {}\n'.format(visible['king'])
		result += '   - People:\n'
		result += '    {}\n'.format(''.join(['  '+str(i)+'  ' for i in range(10)]))
		result += '   +{}\n'.format('----+' * 10)
		for i in range(10):
			result += ' '+str(i)+' | {} |\n'.format(' | '.join(['  ' if e is None else e[0:2] for e in visible['people'][i]]))
			result += '   +{}\n'.format(''.join(['----+' if e == 'G' else '^^^^+' for e in visible['board'][i]]))
		print(result)

	@classmethod
	def buffersize(cls):#buffersizefun
		'''
		returns the buffer size (bits)
		'''
		return BUFFER_SIZE


class KingAndAssassinsServer(game.GameServer):#serverclass
	'''represents a server for the King & Assassins game'''

	def __init__(self, verbose=False, CARDS = CARDS, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):#initfun
		'''
		arguments :
			verbose : prints console related informations (True) or nothing (False)
			CARDS : see glossary : #CARDS
			POPULATION : see glossary : #POPULATION
			BOARD : see glossary : #BOARD
			KA_INITIAL_STATE : see glossary : #KA_INITIALSTATE
		'''
		self.POPULATION = POPULATION
		self.CARDS = CARDS
		super().__init__('King & Assassins', 2, KingAndAssassinsState(initialstate = KA_INITIAL_STATE, POPULATION = POPULATION, BOARD = BOARD), verbose=verbose)
		self._state._state['hidden'] = {
			'assassins': None,
			'cards': random.sample(self.CARDS, len(self.CARDS))
		}

	def _setassassins(self, move):#setassassinsfun
		'''
		Checks whether the move that declares assassins is legal or not
		if it is, modifies the ongoing game data
		
		arguments : 
			move : see glossary : #action
		'''
		state = self._state
		if 'assassins' not in move:
			raise game.InvalidMoveException('The dictionary must contain an "assassins" key')
		if not isinstance(move['assassins'], list):
			raise game.InvalidMoveException('The value of the "assassins" key must be a list')
		if len(move['assassins'])!=3:
			raise game.InvalidMoveException('There must be exactly 3 assassins')
		for assassin in move['assassins']:
			if not isinstance(assassin, str):
				raise game.InvalidMoveException('The "assassins" must be identified by their name')
			if not assassin in self.POPULATION:
				raise game.InvalidMoveException('Unknown villager: {}'.format(assassin))
		state.setassassins(move['assassins'])
		state.update([], 0)

	def applymove(self, move):#applymovefun
		'''
		Applies the move and modifies the ongoing game data
		
		arguments :
			move : see glossary : #action
		'''
		try:
			state = self._state
			move = json.loads(move)
			if state.isinitial():
				self._setassassins(move)
			else:
				self._state.update(move['actions'], self.currentplayer)
		except game.InvalidMoveException as e:
			raise e
		except Exception as e:
			traceback.print_exc(file=sys.stdout)	
			raise game.InvalidMoveException('A valid move must be a dictionary')


class KingAndAssassinsClient(game.GameClient):#clientclass
	'''represents a client for the King & Assassins game'''

	def __init__(self, name, server, verbose=False, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):
		'''
		arguments : 
			name : name of the client 
			server : server (tuple : (hostIP, port))
			verbose : prints console related informations (True) or nothing (False)
			POPULATION : see glossary : #POPULATION
			BOARD : see glossary : #BOARD
			KA_INITIAL_STATE : see glossary : #KA_INITIAL_STATE
		'''
		self.BOARD = BOARD
		self.POPULATION = POPULATION
		self.__name = name
		self.assassins = []
		self.CODESACTIONS = {'m':'move', 'r':'reveal', 't':'attack', 'a':'arrest', 'k':'kill'}
		self.DIRECTIONS = {
			'E': (0, 1),
			'W': (0, -1),
			'S': (1, 0),
			'N': (-1, 0)
		}
		self.CUFFS = False
		self.TESTSECONDKILL = 0
		self.KILLCOUNTER = 0
		self.turns = 0
		super().__init__(server, KingAndAssassinsState(initialstate = KA_INITIAL_STATE, POPULATION = POPULATION, BOARD = BOARD), verbose=verbose)

	def _handle(self, message):#handlefun
		'''
		no use of this for now
		'''
		pass
	
	def _radar(self, state, coord, alAP, enAP):#radarfun
		'''
		6 incoming types of radar
		'''	
		pass
		
	def _radarKingDefensive(self, peopleState, iPos, AP):#radarkingdefensivefun
		'''
		Roams over the board around the king in search of villagers assuming they are
		assassins with a certain amount of AP.
		Makes a priority ranking for those villagers and a list of all the analyzed squares
		
		arguments : 
			peopleState : an updated version of PEOPLE see glossary : #PEOPLE
			iPos : (x, y) coordinates of the radar-calling-pawn see glossary : #action >elements
			AP : actions points of the enemy see glossary : #CARDS >elements
			
		returns : dictionary 
			{
				'scannedPositions' : {
					(x, y): see glossary : #action >elements
						{
							'directionsSet': (dir, ...) see glossary : #action >elements
							'priority': value (int) : 0-n, 0 is the highest priority
							'occupation': name (str) : name of a pawn
							},
					...}
				'prioritiesDictionary' : {
					priority: (int) : 0-n, 0 is the highest priority
						[ 
							(x, y), see glossary : #action >elements
							...]}
				}
		'''
		posDict = {}
		extDict = {}
		prioDict = {}
		utmosts = self._getcoords(iPos, set())
		extDict[1] = []
		prioDict[0] = []
		prioDict[1] = []
		for utmost in utmosts:
			occupation = peopleState[utmost[0][0]][utmost[0][1]]
			posDict[utmost[0]] = {'directionsSet':utmost[1], 'priority':1, 'occupation':occupation}
			extDict[1].append(utmost[0])
			if occupation == "assassin":
				posDict[utmost[0]]['priority'] = 0
				prioDict[0].append(utmost[0])
			elif occupation is not None and occupation != "king" and occupation != "knight":
				prioDict[1].append(utmost[0])
		for APLeft in range(2,AP+1):
			if APLeft<AP:
				extDict[APLeft] = []
				prioDict[APLeft] = []
			utmosts = []
			for previous in extDict[APLeft-1]:
				utmosts += self._getcoords(previous, posDict[previous]['directionsSet'])
			for utmost in utmosts:
				if utmost[2] == 'GR':
					if utmost[0] not in posDict.keys():
						update = True
					elif posDict[utmost[0]]['priority'] > APLeft-1:
						update = True
					else:
						update = False
					if update:
						occupation = peopleState[utmost[0][0]][utmost[0][1]]
						posDict[utmost[0]] = {'directionsSet':utmost[1], 'priority':APLeft-1, 'occupation':occupation}
						extDict[APLeft-1].append(utmost[0])
						newUtmosts = self._getcoords(utmost[0], posDict[utmost[0]]['directionsSet'])
						utmosts += newUtmosts
						if occupation == "assassin":
							posDict[utmost[0]]['priority'] = 0
							prioDict[0].append(utmost[0])
						elif occupation is not None and occupation != "king" and occupation != "knight":
							prioDict[APLeft-1].append(utmost[0])
				elif APLeft<AP:
					if utmost[0] not in posDict.keys():
						update = True
					elif posDict[utmost[0]]['priority']>APLeft:
						update = True
					else:
						update = False
					if update:
						occupation = peopleState[utmost[0][0]][utmost[0][1]]
						posDict[utmost[0]] = {'directionsSet':utmost[1], 'priority':APLeft, 'occupation':occupation}
						extDict[APLeft].append(utmost[0])
						if occupation == "assassin":
							posDict[utmost[0]]['priority'] = 0
							prioDict[0].append(utmost[0])
						elif occupation is not None and occupation != "king" and occupation != "knight":
							prioDict[APLeft].append(utmost[0])
		return {'prioritiesDictionary': prioDict, 'scannedPositions':posDict}

	def _getcoords(self, pos, dirSet):#getcoordsfun
		'''
		returns the adjacent squares to coordinate pos while following the
		flow indicated by the directions in dirSet :
		if dirSet has no element, returns all adjacent squares,
		if dirSet has at least one element, returns all adjacent
		squares except in the opposites directions of those in
		dirSet. 
		It also indicates the ground-level transition from pos
		to the adjacent squares and the new flow of directions
		
		arguments :
			pos : (x, y) see glossary : #actions >elements
			dirSet : (dir, ...) see glossary : #actions >element
			
		returns : list of tuple
			[
				(coord, newDirSet, transition),
				...]
			coord : (x, y) see glossary : #actions >elements
			newDirSet : (dir, ...) see glossary : #actions >element
			transition : ground-level+ground-level (str) see glossary : #BOARD >element
		'''
		if pos[0] >= 0 and pos[1] >= 0 and pos[0]<len(self.BOARD) and pos[1]<len(self.BOARD[0]):
			directions = ['N','S','E','W']
			coords = []
			for direction in dirSet:
				directions.pop(directions.index(self._getopposite(direction)))
			for direction in directions:
				coord = self._getcoord((pos[0], pos[1], direction))
				if coord[0] >= 0 and coord[1] >= 0 and coord[0]<len(self.BOARD) and coord[1]<len(self.BOARD[0]):
					newDirSet = dirSet
					newDirSet.add(direction)
					transition = self.BOARD[pos[0]][pos[1]]+self.BOARD[coord[0]][coord[1]]
					coords.append((coord, newDirSet, transition))
			return coords
		else:
			return []
	
	def _getcoord(self, coord):#getcoordfun
		'''
		returns a tuple of coordinates deplaced in a certain DIRECTION (N, S, E, W)
		
		arguments : 
			coord : (x, y, dir) see glossary : #action >elements
			
		returns :
			(x, y) see glossary : #action >elements
		'''
		return tuple(coord[i] + self.DIRECTIONS[coord[2]][i] for i in range(2))
	
	def _getdir(self, movement):#getdirfun
		'''
		returns the DIRECTIONS elements that describe movement for x and y in a tuple
		WARNING : null values return S-E
		
		arguments :
			movement : (xs, ys)
				xs : (int) distance in vertical direction, positive_0 - downward, negative - upward
				ys : (int) distance in horizontal direction, positive_0 - rightward, negative - leftward
				
		returns :
			(xdir, ydir) :
				xdir : global vertical direction of the movement as a dir see glossary : #action >element
				ydir : global horizontal direction of the movement as a dir see glossary : #action >element
		'''
		xs, ys = movement[0], movement[1]
		xdir = 'S' if xs >= 0 else 'N'
		ydir = 'E' if ys >= 0 else 'W'
		return (xdir, ydir)
	
	def _getopposite(self, dir):#getoppositefun
		'''
		returns the opposite direction of dir
		
		arguments : dir see glossary : #action >element
		
		returns : dir see glossary : #action >element
		'''
		oppositeDir = 'NS'.strip(dir)
		oppositeDir = 'WE'.strip(dir) if len(oppositeDir)==2 else oppositeDir
		oppositeDir = '' if len(oppositeDir)==2 else oppositeDir
		return oppositeDir
	
	def _validMove(self, peopleState, moveList):#validmovefun
		'''
		the purpose of this function is to determine whether a move is legal or not on the
		actual state of the board, the cost of this move, and whether the moves pushed
		any other pawns or not
		WARNING : this method does not take account of the remaining available AP for this turn
		
		arguments :
			peopleState : an updated version of PEOPLE see glossary : #PEOPLE
			moveList : an action see glossary : #action >element
		
		returns : dictionary
			{
				'cost' : (int) action points
				'legal' : (bool) whether the action is legal or not
				'push' : (bool) whether the move pushed some pawns or not
				}
		'''
		returnValue = {'cost':0,'legal':False,'push':False}
		player = self._playernb
		if moveList[0] == 'move':#validmovemove
			x, y, d = int(moveList[1]), int(moveList[2]), moveList[3]
			if x<0 or y <0 or x>9 or y>9:
				return returnValue #cannot select out of the map
			p = peopleState[x][y]
			if p is None:
				return returnValue #there is no one to move
			nx, ny = self._getcoord((x, y, d))
			if nx<0 or ny <0 or nx>9 or ny>9:
				return returnValue #cannot move/act out of the map
			new = peopleState[nx][ny]
			if p == 'king' and ((x, y, d) == (2, 2, 'N') or (x, y, d) == (4, 1, 'W')):
				returnValue['cost']=1
				returnValue['legal']=True
				return returnValue
			# King, assassins, villagers can only move on a free cell
			if p != 'knight' and new is not None:
				return returnValue #cannot move on a cell that is not free
			if p == 'king' and self.BOARD[nx][ny] == 'R':
				return returnValue #the king cannot move on a roof
			if p in {'assassin'} | self.POPULATION and player != 0:
				return returnValue #villagers and assassins can only be moved by player 0
			if p in {'king', 'knight'} and player != 1:
				return returnValue #the king and knights can only be moved by player 1
			# Move granted if cell is free
			if new is None:
				cost = 0
				if self.BOARD[x][y] == self.BOARD[nx][ny]:
					cost = 1
				elif self.BOARD[x][y] == 'G':
					cost = 1 if p == 'assassin' else 2
				else:
					cost = 0 if p == 'assassin' else 1
				returnValue['cost']=cost
				returnValue['legal']=True
				return returnValue
			# If cell is not free, check if the knight can push villagers
			else:
				news = [(x,y)]
				pushable = False
				knightIsUp = False
				if self.BOARD[x][y] == 'R' or self.BOARD[nx][ny] == 'R':
					knightIsUp = True
				while (self.BOARD[nx][ny] == 'G' or knightIsUp) and new is not None and new != 'knight' and new != 'king':
					news.append((nx,ny))
					if self.BOARD[nx][ny] == 'G':
						knightIsUp = False
					nx, ny = self._getcoord((nx, ny, d))
					if nx<0 or ny<0 or nx>9 or ny>9:
						break
					new = peopleState[nx][ny]
					if new is None and (self.BOARD[nx][ny] == 'G' or knightIsUp):
						pushable = True
				if pushable:
					returnValue['cost']=1
					returnValue['legal']=True
					returnValue['push']=True
					return returnValue
				else:
					return returnValue #The knight can not push this way
		# ('arrest', x, y, dir): arrests the villager in direction dir with knight at position (x, y)
		elif moveList[0] == 'arrest':#validmovearrest
			if player != 1:
				return returnValue #arrest action only possible for player 1
			if not self.CUFFS:
				return returnValue #arrest action only possible if the drawn card says so
			x, y, d = int(moveList[1]), int(moveList[2]), moveList[3]
			arrester = peopleState[x][y]
			if arrester != 'knight':
				return returnValue #the attacker is not a knight
			tx, ty = self._getcoord((x, y, d))
			target = peopleState[tx][ty]
			if target not in self.POPULATION:
				return returnValue #only villagers can be arrested
			if self.BOARD[tx][ty] == 'R' and self.BOARD[x][y] == 'G':
				return returnValue #arrest action impossible from below
			returnValue['cost']=1
			returnValue['legal']=True
			return returnValue		
		# ('kill', x, y, dir): kills the assassin/knight in direction dir with knight/assassin at position (x, y)
		elif moveList[0] == 'kill':#validmovekill
			x, y, d = int(moveList[1]), int(moveList[2]), moveList[3]
			killer = peopleState[x][y]
			cost = 0
			if killer == 'assassin' and player != 0:
				return returnValue #kill action for assassin only possible for player 0
			if killer == 'knight' and player != 1:
				return returnValue #kill action for knight only possible for player 1
			tx, ty = self._getcoord((x, y, d))
			target = peopleState[tx][ty]
			if target is None:
				return returnValue #there is no one to kill
			if self.BOARD[tx][ty] == 'R' and self.BOARD[x][y] == 'G':
				return returnValue #kill action impossible from below
			if killer == 'assassin' and target == 'knight':
				if self.KILLCOUNTER >= 2:
					return returnValue #2 knight kills max per turn for assassin player
				cost = 1 + self.TESTSECONDKILL
				returnValue['cost']=cost
				returnValue['legal']=True
				return returnValue
			elif killer == 'knight' and target == 'assassin':
				returnValue['cost']=1
				returnValue['legal']=True
				return returnValue
			else:
				return returnValue #forbidden kill
		# ('attack', x, y, dir): attacks the king in direction dir with assassin at position (x, y)
		elif moveList[0] == 'attack':#validmoveattack
			if player != 0:
				return returnValue #attack action only possible for player 0
			x, y, d = int(moveList[1]), int(moveList[2]), moveList[3]
			attacker = peopleState[x][y]
			if attacker != 'assassin':
				return returnValue #the attacker is not an assassin
			tx, ty = self._getcoord((x, y, d))
			target = peopleState[tx][ty]
			if target != 'king':
				return returnValue #only the king can be attacked
			returnValue['cost']=2
			returnValue['legal']=True
			return returnValue
		# ('reveal', x, y): reveals villager at position (x,y) as an assassin
		elif moveList[0] == 'reveal':#validmovereveal
			if player != 0:
				return returnValue #action only possible for player 0
			x, y = int(moveList[1]), int(moveList[2])
			p = peopleState[x][y]
			if p not in hidden['assassins']:
				return returnValue #the specified villager is not an assassin
			returnValue['legal']=True
			return returnValue
	
	def _updateCopy(self, peopleState, kingState, moveList):#updatecopyfun
		'''
		applies a moveList on peopleState and return the new state of the game as well 
		as the new state of the king
		WARNINGS : 
			The moveList MUST return True when called with _validMove
			peopleState will be modified
			
		arguments : 
			peopleState : an updated version of PEOPLE see glossary : #PEOPLE
			kingState : (str) status of the king ('healty', 'injured', 'dead')
			moveList : an action see glossary : #action >element
			
		returns : dictionary 
			{
				'peopleState' : peopleState an updated version of PEOPLE see glossary : #PEOPLE
				'kingState' : kingState (str) status of the king ('healty', 'injured', 'dead')
				}
		'''
		if moveList[0] == 'move':#updatecopymove
			x, y, d = int(moveList[1]), int(moveList[2]), moveList[3]
			p = peopleState[x][y]
			nx, ny = self._getcoord((x, y, d))
			new = peopleState[nx][ny]
			# Move granted if cell is free
			if new is None or p == 'king':
				peopleState[x][y], peopleState[nx][ny] = peopleState[nx][ny], peopleState[x][y]
			# If cell is not free the knight can push villagers
			else:
				news = [(x,y)]
				while new is not None:
					news.append((nx,ny))
					nx, ny = self._getcoord((nx, ny, d))
					new = peopleState[nx][ny]
				while len(news)>0:
					loc = news.pop()
					peopleState[loc[0]][loc[1]], peopleState[nx][ny] = peopleState[nx][ny], peopleState[loc[0]][loc[1]]
					nx, ny = loc[0], loc[1]
		# ('arrest', x, y, dir): arrests the villager in direction dir with knight at position (x, y)
		elif moveList[0] == 'arrest':#updatecopyarrest
			x, y, d = int(moveList[1]), int(moveList[2]), moveList[3]
			tx, ty = self._getcoord((x, y, d))
			peopleState[tx][ty] = None		
		# ('kill', x, y, dir): kills the assassin/knight in direction dir with knight/assassin at position (x, y)
		elif moveList[0] == 'kill':#updatecopykill
			x, y, d = int(moveList[1]), int(moveList[2]), moveList[3]
			killer = peopleState[x][y]
			tx, ty = self._getcoord((x, y, d))
			if killer == 'assassin':
				self.TESTSECONDKILL = 1
				self.KILLCOUNTER+=1
			peopleState[tx][ty] = None
		# ('attack', x, y, dir): attacks the king in direction dir with assassin at position (x, y)
		elif moveList[0] == 'attack':#updatecopyattack
			kingState = 'injured' if kingState == 'healthy' else 'dead'
		# ('reveal', x, y): reveals villager at position (x,y) as an assassin
		elif moveList[0] == 'reveal':#updatecopyreveal
			x, y = int(moveList[1]), int(moveList[2])
			peopleState[x][y] = 'assassin'
		return {'peopleState':peopleState,'kingState':kingState}
	
	def _prettyCommands(self, movesString):#prettycommandsfun
		'''
		converts a string command into a list of actions
		
		arguments : 
			movesString : see glossary : #command
			
		returns : 
			movesList : see glossary : #action
		'''
		movesList = []
		movesString = movesString.strip(' +')
		movesStringList = movesString.split(' + ')
		for i in range(len(movesStringList)):
			movesStringList[i] = movesStringList[i].split(' ')#regex ' + ' or '+'
			x = int(movesStringList[i][0])
			y = int(movesStringList[i][1])
			commandsList = movesStringList[i][2:len(movesStringList[i])]
			for j in range(len(commandsList)):
				copyH = copy.copy(commandsList[j])
				commandsList[j]=[]
				if copyH[0] in self.CODESACTIONS:
					commandsList[j].append(self.CODESACTIONS[copyH[0]])
					commandsList[j].append(x)
					commandsList[j].append(y)
					if copyH[0] != 'r' and len(copyH)==2:
						commandsList[j].append(copyH[1])
						if copyH[0] == 'm':
							x, y = x+self.DIRECTIONS[copyH[1]][0], y+self.DIRECTIONS[copyH[1]][1]
			movesList+=copy.copy(commandsList)
		return movesList
	
	def _validObjective(self, peopleState, kingState, iPos, commands, APLeft):#validobjectivefun
		'''
		this function tests a string command that stands for multiple actions on the pawn at iPos for the price of APLeft and
		evaluates if each action in command is legal and if there are enough AP. It returns useful informations whether
		the move is legal or not. (move stands for every actions in commands)
		WARNING : peopleState is NOT modified
		
		arguments :
			peopleState : an updated version of PEOPLE see glossary : #PEOPLE
			kingState : (str) status of the king ('healty', 'injured', 'dead')
			iPos : (x, y) coordinates of the pawn see glossary : #action >elements
			commands : same as movesString (prettyCommands) without the coordinates : see glossary : #command
			APLeft : (int) action points left see glossary : #CARDS >elements
			
		returns : dictionary
			{
				'legal': False : the move can not entirely be done
				'validCommands': identical as commands up to the point where the first failed action occurs
				'history': dictionary
					{
						'APLeft': [APLeft, ...] : list of action points left after each action in validCommands see glossary : #CARDS >elements
						'pushes': [push, ...] : list of booleans (True if the action pushed else False) for each action in validCommands
						'from': [(x, y), ...] : list of coordinates for each previous position (for each action in validCommands) see glossary : #action >elements
						}
				'APLeft': (int) action points left after every actions in validCommands see glossary : #CARDS >elements
				'fatalMoveString': (str) character for the action that failed see glossary : #command >element
				'lastValidPosition': (x, y) last valid coordinates for the pawn that was at iPos before see glossary : #action >elements
				}
				
			OR
			
			{
				'legal': True : the move can be done entirely
				'movesList': see glossary : #action
				'APLeft': (int) action points left after every actions in movesList see glossary : #CARDS >elements
				'peopleStateCopy': a modified copy of peopleState see glossary : #PEOPLE
				'kingState': (str) status of the king ('healty', 'injured', 'dead')
		
		'''
		movesString = str(iPos[0])+' '+str(iPos[1])+' '+commands
		validCommands = ''
		movesList = self._prettyCommands(movesString)
		peopleStateCopy = copy.deepcopy(peopleState)
		history = {'from':[],'pushes':[],'APLeft':[]}
		for i in range(len(movesList)):
			validMove = self._validMove(peopleStateCopy, movesList[i])
			if validMove['legal'] and APLeft-validMove['cost']>=0:
				APLeft-=validMove['cost']
				history['APLeft'].append(APLeft)
				history['pushes'].append(validMove['push'])
				history['from'].append((movesList[i][1], movesList[i][2]))
				updateCopy= self._updateCopy(peopleStateCopy, kingState, movesList[i])
				peopleStateCopy, kingState = updateCopy['peopleState'], updateCopy['kingState']
				validCommands=commands[0:3*i+3]
			else:
				fPos = (int(movesList[i][1]), int(movesList[i][2]))
				return {'legal':False, 'validCommands':validCommands, 'history':history, 'APLeft':APLeft, 'fatalMoveString':commands[3*i:3*i+3],
					'lastValidPosition':fPos}
		return {'legal':True, 'movesList':movesList, 'APLeft':APLeft, 'peopleStateCopy':peopleStateCopy, 'kingState':kingState}
	
	def _stateObjective(self, peopleState, kingState, iPos, fPos, objective, APAvailable, nDetour = 0, dirPrevious = '', nKill = 0):#stateobjectivefun
		'''
		PATHFINDING. Returns a list of moves to accomplish objective, as well as many useful informations whether objective
		was actually completed or not
		WARNING : this function is recursive
		
		the algorithm consists of the following serie of actions :
		
			selects the pawn at coordinates iPos,
			
			tries to accomplish objective at coordinates fPos with APAvailable, to do that :
				moves the pawn by performing all horizontal movements (the pawn is now in a vertical line with fPos),
				does the same thing vertically (the pawn is now next to fPos),
				accomplishes objective on fPos.
				
			if that fails and the parameter nKill allows the function to kill an obstacle :
				attempts to kill the obstacle
			
			if that fails and the parameter nDetour allows the function to make a detour :
				attempts to avoid the obstacle by making a detour
				
			if that fails :
				attempts to avoid the obstacle without making a detour
				
			if that fails and some of the previous actions consisted in pushing some pawns :
				aborts the last push, considering it as an obstacle. Resume the algorithm at
				this point
				
		arguments : 
			peopleState : an updated version of PEOPLE see glossary : #PEOPLE
			kingState : (str) status of the king ('healty', 'injured', 'dead')
			iPos : (x, y) coordinates of the pawn see glossary : #action >elements
			fPos : (x, y) coordinates of the target square see glossary : #action >elements
			objective : (str) character for the desired action see glossary : #command >element
			APAvailable : (int) action points available see glossary : #CARDS >elements
			nDetour : (int) maximal amount of detours allowed
			dirPrevious : dir see glossary : #action >element
			nKill : (int) maximal amount of kills allowed
			
		returns : dictionary
			{
				'completed': True : if objective was completed
				'movesList': movesList list of actions to accomplish objective see glossary : #action
				'APLeft': (int) action points left after completion of objective see glossary : #CARDS >elements
				'peopleState' : an updated version of PEOPLE see glossary : #PEOPLE
				'kingState' : (str) status of the king ('healty', 'injured', 'dead')
				'lastPosition': (x, y) new coordinates of the pawn after completion of objective se glossary : #action >elements
				}
				
			OR
			
			{
				'completed': False : if objective was not completed
				'movesList': [] : an empty list, no move since the objective was not completed
				'APLeft': APAvailable : no change here
				'error': (str) message that helps to understand why the objective was not completed
				}
		'''
		if iPos == fPos and objective == 'm':
			return {'completed':True, 'movesList':[], 'APLeft':APAvailable, 'peopleState':peopleState, 'kingState':kingState,
				'lastPosition':iPos}
		elif iPos == fPos and objective != 'm' and objective != 'r':
			return None #error, cannot execute an action on the pawn square (other than move)
		x, y = fPos[0]-iPos[0], fPos[1]-iPos[1]
		xdir, ydir = self._getdir((x,y))
		ixdir, iydir = self._getopposite(xdir), self._getopposite(ydir)
		metadir = ydir if x==0 else xdir
		kx = 0 if x==0 else 1
		ky = 1 if x==0 else 0
		stated = ''.join([
			(abs(y)-ky)*''.join(['m',ydir,' ']),
			(abs(x)-kx)*''.join(['m',xdir,' ']),
			''.join([objective,metadir,' '])])
		regress = False
		if stated[1] == dirPrevious:
			ended = False
			validCommands = ''
			pushes = []
			ydone = 0
			xdone = 0
			APLeft = APAvailable
			fatalCommand = stated[:3]
			fatalCoord = (iPos[0],iPos[1])
			regress = True
		else:
			validObjective = self._validObjective(peopleState, kingState, iPos, stated, APAvailable)
			ended = validObjective['legal']
		forceEnded = False
		detourEnded = False
		killEnded = False
		longestValidCommands = ''
		while not ended:
			if not regress :
				validCommands = validObjective['validCommands']
				history = validObjective['history']
				pushes = history['pushes']
				longestValidCommands =validCommands if len(validCommands)>len(longestValidCommands) else longestValidCommands
				ydone = validCommands.count(''.join(['m',ydir]))
				xdone = validCommands.count(''.join(['m',xdir]))
				APLeft = validObjective['APLeft']
				fatalCommand = validObjective['fatalMoveString']
				fatalCoord = validObjective['lastValidPosition']
				dirPrevious = self._getopposite(validCommands[-2:].strip(' ')) if validCommands != '' else dirPrevious
			else:
				regress = False
			'''debug purposes
			print("fcoord = "+str(fatalCoord))
			print("fcmd   = "+str(fatalCommand))
			print("nkill  = "+str(nKill))
			print("ndtour = "+str(nDetour))
			print("dprev  = "+str(dirPrevious))
			'''
			if nKill>0:
				if fatalCommand != dirPrevious:
					kill = ''.join([
						''.join(['k',fatalCommand[1],' ']),
						''.join(['m',fatalCommand[1],' '])])
					killObjective = self._validObjective(peopleState, kingState, iPos, ''.join([validCommands, kill]), APAvailable)
					if killObjective['legal']:
						newIPos = self._getcoord((killObjective['movesList'][-1][1],
							killObjective['movesList'][-1][2], killObjective['movesList'][-1][3]))
						sentDirPrevious = self._getopposite(fatalCommand[1])
						statedKillObjective = self._stateObjective(killObjective['peopleStateCopy'], killObjective['kingState'], newIPos,
							fPos, objective, killObjective['APLeft'], nDetour, sentDirPrevious, nKill-1)
						if statedKillObjective['completed']:
							killEnded = True
							break
						elif peopleState[iPos[0]][iPos[1]]=="assassin":
							self.KILLCOUNTER-=1
							if self.KILLCOUNTER == 0:
								self.TESTSECONDKILL=0
					elif killObjective['fatalMoveString'][0]=='m' and peopleState[iPos[0]][iPos[1]]=="assassin":
						self.KILLCOUNTER-=1
						if self.KILLCOUNTER == 0:
							self.TESTSECONDKILL=0
			if nDetour>0:
				if fatalCommand[1]==xdir or fatalCommand[1]==ydir:
					wrongDir = fatalCommand[1]
					newDir = ydir if wrongDir == xdir else xdir
					dirRemaining = (abs(y)-ydone) if wrongDir == xdir else (abs(x)-xdone)
					opNewDir = self._getopposite(newDir)
					tryOppositeDirection = False
					if dirRemaining == 0:
						if newDir != dirPrevious:
							detour = ''.join(['m',newDir,' '])
							detourObjective = self._validObjective(peopleState, kingState, iPos, ''.join([validCommands,detour]), APAvailable)
							tryOppositeDirection = not detourObjective['legal']
							if detourObjective['legal']:
								newIPos = self._getcoord((detourObjective['movesList'][-1][1], 
									detourObjective['movesList'][-1][2], detourObjective['movesList'][-1][3]))
								sentDirPrevious = self._getopposite(newDir)
								statedDetourObjective = self._stateObjective(detourObjective['peopleStateCopy'], 
									detourObjective['kingState'], newIPos, fPos, objective, detourObjective['APLeft'], nDetour-1, sentDirPrevious, nKill)
								tryOppositeDirection = not statedDetourObjective['completed']
								if statedDetourObjective['completed']:
									detourEnded = True
									break
						else:
							tryOppositeDirection = True
					if (dirRemaining > 0 or tryOppositeDirection) and opNewDir != dirPrevious:
						detour = ''.join(['m',opNewDir,' '])
						detourObjective = self._validObjective(peopleState, kingState, iPos, ''.join([validCommands,detour]), APAvailable)
						if detourObjective['legal']:
							newIPos = self._getcoord((detourObjective['movesList'][-1][1], detourObjective['movesList'][-1][2],
								detourObjective['movesList'][-1][3]))
							sentDirPrevious = self._getopposite(opNewDir)
							statedDetourObjective = self._stateObjective(detourObjective['peopleStateCopy'], detourObjective['kingState'],
								newIPos, fPos, objective, detourObjective['APLeft'], nDetour-1, sentDirPrevious, nKill)
							if statedDetourObjective['completed']:
								detourEnded = True
								break
			if fatalCommand[1]==ydir and abs(x)-xdone >=1:
				if abs(y)-ydone == 1 and abs(x)-xdone == 1:
					stated = ''.join([
						validCommands,
						''.join(['m',xdir,' ']),
						''.join([objective,ydir,' '])])
				elif abs(x)-xdone == 1:
					xdone+=1
					stated = ''.join([
						validCommands,
						''.join(['m',xdir,' ']),
						(abs(y)-ydone-1)*''.join(['m',ydir,' ']),
						''.join([objective,ydir,' '])])
				else:
					xdone+=1
					stated = ''.join([
						validCommands,
						''.join(['m',xdir,' ']),
						(abs(y)-ydone)*''.join(['m',ydir,' ']),
						(abs(x)-xdone-1)*''.join(['m',xdir,' ']),
						''.join([objective,xdir,' '])])
			elif fatalCommand[1]==xdir and abs(x)-xdone >=2 and validCommands.count(''.join(['m',ydir,' '])) > 0:
				xdone+=2
				ydone-=1
				lastyid = validCommands.rfind(''.join(['m',ydir,' ']))
				beforelastyid = validCommands[0:lastyid]
				afterlastyid = validCommands[lastyid+3:len(validCommands)]
				if abs(x)-xdone == 0:
					if abs(y)-ydone == 1:
						stated =''.join([
							beforelastyid,
							afterlastyid,
							2*''.join(['m',xdir,' ']),
							''.join([objective,ydir,' '])])
					else:
						stated = ''.join([
							beforelastyid,
							afterlastyid,
							2*''.join(['m',xdir,' ']),
							(abs(y)-ydone-1)*''.join(['m',ydir,' ']),
							''.join([objective,ydir,' '])])
				else:
					stated = ''.join([
						beforelastyid,
						afterlastyid,
						2*''.join(['m',xdir,' ']),
						(abs(y)-ydone)*''.join(['m',ydir,' ']),
						(abs(x)-xdone-1)*''.join(['m',xdir,' ']),
						''.join([objective,xdir,' '])])
			elif True in pushes:
				regress = True
				lastTruePushIndex = len(pushes)-1-pushes[::-1].index(True) #index of last element of pushes (so stupid... => rindex())
				fatalCommand = validCommands[3*lastTruePushIndex:3*lastTruePushIndex+3]
				validCommands = validCommands[0:3*lastTruePushIndex]
				pushes = pushes[0:lastTruePushIndex]
				ydone = validCommands.count(''.join(['m',ydir]))
				xdone = validCommands.count(''.join(['m',xdir]))
				APLeft = history['APLeft'][lastTruePushIndex]
				fatalCoord = history['from'][lastTruePushIndex]
				dirPrevious = self._getopposite(validCommands[-2:].strip(' ')) if validCommands != '' else dirPrevious
				continue
			else:
				forceEnded = True
				break
			validObjective = self._validObjective(peopleState, kingState, iPos, stated, APAvailable)
			ended = validObjective['legal']
		if forceEnded:
			reason = 'notFullyCompleted'
			if longestValidCommands != '':
				return {'completed':False, 'movesList':self._prettyCommands(str(iPos[0])+' '+str(iPos[1])+' '+longestValidCommands),
					'APLeft':APLeft, 'error':reason}#will disapear with a new final version for nextmove
			else:
				return {'completed':False, 'movesList':[], 'APLeft':APAvailable, 'error':reason}
		elif detourEnded:
			movesList = detourObjective['movesList']+statedDetourObjective['movesList']
			APLeft = statedDetourObjective['APLeft']
			peopleState = statedDetourObjective['peopleState']
			kingState = statedDetourObjective['kingState']
			newcoord = fPos if objective == 'm' else (movesList[-1][1], movesList[-1][2])
			return {'completed':True, 'movesList':movesList, 'APLeft':APLeft, 'peopleState':peopleState, 'kingState':kingState,
				'lastPosition':newcoord}
		elif killEnded:
			movesList = killObjective['movesList']+statedKillObjective['movesList']
			APLeft = statedKillObjective['APLeft']
			peopleState = statedKillObjective['peopleState']
			kingState = statedKillObjective['kingState']
			newcoord = fPos if objective == 'm' else (movesList[-1][1], movesList[-1][2])
			return {'completed':True, 'movesList':movesList, 'APLeft':APLeft, 'peopleState':peopleState, 'kingState':kingState,
				'lastPosition':newcoord}
		else:
			movesList = validObjective['movesList']
			APLeft = validObjective['APLeft']
			peopleState = validObjective['peopleStateCopy']
			kingState = validObjective['kingState']
			newcoord = fPos if objective == 'm' else (movesList[-1][1], movesList[-1][2])
			return {'completed':True, 'movesList':movesList, 'APLeft':APLeft, 'peopleState':peopleState, 'kingState':kingState,
				'lastPosition':newcoord}
	
	def _minimizeObjective(self, peopleState, kingState, iPos, fPos, objective, APAvailable):#minimizeobjectivefun
		'''
		tries to accomplish objective with a minimal amount of AP within APAvailable
		it calls successively for _stateObjective with different parameters for APAvailable, nDetour, nKill
		starting with the minimal amount of AP required to accomplish objective, the minimal amount of kills
		and the minimal amount of detours, then gradually increases these three parameters following specific rules
		these rules are different for knights, assassins, villagers/king
		WARNING : temporary : prints informations while searching for a path (console)
		
		arguments :
			peopleState : an updated version of PEOPLE see glossary : #PEOPLE
			kingState : (str) status of the king ('healty', 'injured', 'dead')
			iPos : (x, y) coordinates of the pawn see glossary : #action >elements
			fPos : (x, y) coordinates of the target square see glossary : #action >elements
			objective : (str) character for the desired action see glossary : #command >element
			APAvailable : (int) action points available see glossary : #CARDS >elements
			
		returns : same returns as _statedObjective
		'''
		distance = abs(fPos[0]-iPos[0]) + abs(fPos[1]-iPos[1])
		assassinPattern = (peopleState[iPos[0]][iPos[1]] == "assassin")
		knightPattern = (peopleState[iPos[0]][iPos[1]] == "knight")
		if assassinPattern:
			minCostDist = distance//2
			maxCostDist = distance
		else:
			minCostDist = distance
			maxCostDist = (distance//2)*3+(distance%2)*2
		print("Searching for a valid path (please be patient)...")
		tic = time.time()
		for AP in range(minCostDist, APAvailable+1):
			if assassinPattern:
				maxKill = (AP-minCostDist)//2+(AP-minCostDist)%2
				if maxKill >2:
					maxKill = 2#this is a rule of the game/ #knightsleft
			elif knightPattern:
				maxKill = AP-minCostDist
				if maxKill >3:
					maxKill = 3#there can only be 3 assassins/ #assassinsleft
			else:
				maxKill = 0
			for kill in range(0, maxKill+1):
				if assassinPattern:
					APMove = AP-2*kill+1 if kill > 1 else AP-kill
					minDet = (APMove-maxCostDist)//2
					maxDet = APMove-minCostDist
				else:
					APMove = AP-kill
					minDet = (APMove-maxCostDist)//3 if (APMove-maxCostDist)%3 ==0 else (APMove-maxCostDist)//3+1
					maxDet = (APMove-minCostDist)//2
				if minDet <0:
					minDet = 0
				if maxDet <0:
					maxDet = 0
				for detour in range(minDet, maxDet+1):
					stateObjective = self._stateObjective(peopleState, kingState, iPos, fPos, objective, AP, detour, '', kill)
					sys.stdout.write(' '*40)
					sys.stdout.write(chr(13))
					sys.stdout.write("AP : "+str(AP)+" kills : "+str(kill)+" detours : "+str(detour))
					sys.stdout.write(chr(13))
					sys.stdout.flush()
					if stateObjective['completed']:
						print("\r\n... Succeeded ("+str(time.time()-tic)+" seconds)")
						stateObjective['APLeft'] = APAvailable - AP
						return stateObjective
		print("\r\n... Failed ("+str(time.time()-tic)+" seconds)")
		stateObjective['APLeft'] = APAvailable
		return stateObjective
	
	def _nextmove(self, state):#nextmovefun
		'''
		Two possible situations:
		- If the player is the first to play, it has to select his/her assassins
		- Otherwise, it has to choose a sequence of actions
		see glossary : #action
		 
		arguments :
			state : an updated version of KA_INITIAL_STATE see glossary : #KA_INITIAL_STATE
			
		returns : 
			dumped informations for the server see glossary : #action
		'''
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
				self.assassins.append(peopleState[7][1])
				self.assassins.append(peopleState[1][7])
				self.assassins.append(peopleState[2][1])
				return json.dumps({'assassins': [peopleState[7][1], peopleState[1][7], peopleState[2][1]]}, separators=(',', ':'))
			else:
				APking = state['card'][0]
				APcom = state['card'][1]
				self.CUFFS = state['card'][2]
				APknight = state['card'][3]
				if self._playernb == 0:
					finalCommandsList=[]
					if self.turns == 1:
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (8,3), (5,4), 'm', 4)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APcom = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
					elif self.turns == 2:
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (5,2), (4,3), 'm', 4)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APcom = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (3,6), (1,6), 'm', 2)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APcom = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
					elif self.turns == 3:
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (2,1), (2,2), 'm', 4)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APcom = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (3,4), (1,4), 'm', 3)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APcom = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
					elif self.turns == 4:
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (7,5), (6,5), 'm', 4)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APcom = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (5,5), (2,5), 'm', 3)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APcom = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
					elif self.turns == 5:
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (5,7), (4,7), 'm', 4)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APcom = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
					return json.dumps({'actions': finalCommandsList}, separators=(',', ':'))
				else:
					finalCommandsList=[]
					if self.turns == 1:
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (9,8), (7,6), 'm', 5)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APknight = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
					elif self.turns == 2:
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (7,6), (5,6), 'm', 5)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APknight = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (3,0), (3,2), 'm', 3)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APknight = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (7,8), (6,8), 'm', 1)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APknight = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
					elif self.turns == 3:
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (6,8), (2,8), 'm', 5)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APknight = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (8,8), (7,8), 'm', 1)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APknight = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
					elif self.turns == 4:
						stateObjective = self._stateObjective(peopleStateCopy, kingState, (7,8), (3,8), 'm', 5)
						if stateObjective['completed']:
							finalCommandsList += stateObjective['movesList']
							APknight = stateObjective['APLeft']
							peopleStateCopy = stateObjective['peopleState']
							kingState = stateObjective['kingState']
						else:
							print(stateObjective['movesList'])
					#moves the king
					x, y = -1, -1
					for i in range(len(peopleState)):
						for j in range(len(peopleState[x])):
							if peopleState[i][j] == 'king':
								x, y = i, j
								break
						if x>-1:
							break
					stateObjective = self._stateObjective(peopleStateCopy, kingState, (x,y), (4,1), 'm', APking)
					if stateObjective['completed']:
						finalCommandsList += stateObjective['movesList']
						APking = stateObjective['APLeft']
						peopleStateCopy = stateObjective['peopleState']
						kingState = stateObjective['kingState']
						if APking>=1:
							stateObjective = self._stateObjective(peopleStateCopy, kingState, (4,1), (4,0), 'm', APking)
							if stateObjective['completed']:
								finalCommandsList += stateObjective['movesList']
								APking = stateObjective['APLeft']
								peopleStateCopy = stateObjective['peopleState']
								kingState = stateObjective['kingState']
							else:
								print(stateObjective['movesList'])
					else:
						finalCommandsList += stateObjective['movesList']
						APking = stateObjective['APLeft']
					return json.dumps({'actions': finalCommandsList}, separators=(',', ':'))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")

class KingAndAssassinsHumanClient(game.GameClient):#humanclientclass
	'''represents a client for the King & Assassins game'''

	def __init__(self, name, server, verbose=False, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):#initfun
		'''
		arguments : 
			name : name of the client 
			server : server (tuple : (hostIP, port))
			verbose : prints console related informations (True) or nothing (False)
			POPULATION : see glossary : #POPULATION
			BOARD : see glossary : #BOARD
			KA_INITIAL_STATE : see glossary : #KA_INITIAL_STATE
		'''
		self.CODESACTIONS = {'m':'move', 'r':'reveal', 't':'attack', 'a':'arrest', 'k':'kill'}
		self.DIRECTIONS = {
			'E': (0, 1),
			'W': (0, -1),
			'S': (1, 0),
			'N': (-1, 0)
		}
		self.POPULATION = POPULATION
		self.__name = name
		super().__init__(server, KingAndAssassinsState(initialstate = KA_INITIAL_STATE, POPULATION = POPULATION, BOARD = BOARD), verbose=verbose)

	def _handle(self, message):#handlefun
		pass

	def _nextmove(self, state):#nextmovefun
		'''
		see glossary : #command
		
		arguments :
			state : an updated version of KA_INITIAL_STATE see glossary : #KA_INITIAL_STATE
			
		returns : 
			dumped informations for the server see glossary : #action
		'''
		state = state._state['visible']
		humanMove = sys.stdin.readline()
		humanMove = humanMove.strip("\n ")
		if state['card'] is None:
			while True:
				humanMove = set(acronym[0:2] for acronym in humanMove.split(' '))
				humanMove = [POPULATION_el for acronym in humanMove for POPULATION_el in self.POPULATION if acronym==POPULATION_el[0:2]]
				if len(humanMove) != 3:
					print("Entrez 3 acronymes d'assassin valides (2 premieres lettres minimum)")
					humanMove = sys.stdin.readline()
					humanMove = humanMove.strip("\n ")
				else:
					return json.dumps({'assassins': humanMove}, separators=(',', ':'))
		else:
			try:
				finalCommandsList = []
				while humanMove != "end":
					humanMoveList = humanMove.split(' + ')
					for i in range(len(humanMoveList)):
						humanMoveList[i] = humanMoveList[i].split(' ')#regex ' + ' or '+'
						if len(humanMoveList[i]) <3:
							print("Entrez une commande d'action correcte (mini 3 arguments)")
							break
						x = humanMoveList[i][0]
						y = humanMoveList[i][1]
						actionsList = humanMoveList[i][2:len(humanMoveList[i])]
						for j in range(len(actionsList)):
							copyH = copy.copy(actionsList[j])
							actionsList[j]=[]
							if copyH[0] in self.CODESACTIONS:
								actionsList[j].append(self.CODESACTIONS[copyH[0]])
								actionsList[j].append(x)
								actionsList[j].append(y)
								if copyH[0] != 'r' and len(copyH)==2:
									actionsList[j].append(copyH[1])
									if copyH[0] == 'm':
										x, y = str(int(x)+self.DIRECTIONS[copyH[1]][0]), str(int(y)+self.DIRECTIONS[copyH[1]][1])
						finalCommandsList+=copy.copy(actionsList)
					humanMove = sys.stdin.readline()
					humanMove = humanMove.strip("\n ")
				return json.dumps({'actions': finalCommandsList}, separators=(',', ':'))
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

	# Create the parser for the 'server' subcommand
	server_parser = subparsers.add_parser('server', help='launch a server')
	server_parser.add_argument('--host', help='hostname (default: localhost)', default='localhost')
	server_parser.add_argument('--port', help='port to listen on (default: 5000)', default=5000)
	server_parser.add_argument('-v', '--verbose', action='store_true')
	# Create the parser for the 'client' subcommand
	client_parser = subparsers.add_parser('client', help='launch a client')
	client_parser.add_argument('name', help='name of the player')
	client_parser.add_argument('--host', help='hostname of the server (default: localhost)',
							   default=socket.gethostbyname(socket.gethostname()))
	client_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
	client_parser.add_argument('-v', '--verbose', action='store_true')
	# Create the parser for the 'humanClient' subcommand
	client_parser = subparsers.add_parser('humanClient', help='launch a humanClient')
	client_parser.add_argument('name', help='name of the player')
	client_parser.add_argument('--host', help='hostname of the server (default: localhost)',
							   default=socket.gethostbyname(socket.gethostname()))
	client_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
	client_parser.add_argument('-v', '--verbose', action='store_true')
	# C
	# Parse the arguments of sys.args
	args = parser.parse_args()

	if args.component == 'server':
		try:
			KingAndAssassinsServer(verbose=args.verbose).run()
		except:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")
	elif args.component == 'client':
		try:
			KingAndAssassinsClient(args.name, (args.host, args.port), verbose=args.verbose)
		except:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")
	elif args.component == 'humanClient':
		try:
			KingAndAssassinsHumanClient(args.name, (args.host, args.port), verbose=args.verbose)
		except:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")
	a = input("Enter")
#bottom