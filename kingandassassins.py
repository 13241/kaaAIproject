#!/usr/bin/env python3
# kingandassassins.py
# Author: Sébastien Combéfis, Damien Abeloos
# Version: May 28, 2016

#top
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

BUFFER_SIZE = 2048

CARDS = (
	# (AP King, AP Knight, Fetter, AP Population/Assassins)
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

POPULATION = {
	'monk', 'plumwoman', 'appleman', 'hooker', 'fishwoman', 'butcher',
	'blacksmith', 'shepherd', 'squire', 'carpenter', 'witchhunter', 'farmer'
}

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

# Coordinates of pawns on the board
KNIGHTS = {(1, 3), (3, 0), (7, 8), (8, 7), (8, 8), (8, 9), (9, 8)}

VILLAGERS = {
	(1, 7), (2, 1), (3, 4), (3, 6), (5, 2), (5, 5),
	(5, 7), (5, 9), (7, 1), (7, 5), (8, 3), (9, 5)
}

# Separate board containing the position of the pawns
PEOPLE = [[None for column in range(10)] for row in range(10)]

# Place the king in the right-bottom corner
PEOPLE[9][9] = 'king'

# Place the knights on the board
for coord in KNIGHTS:
	PEOPLE[coord[0]][coord[1]] = 'knight'

# Place the villagers on the board
# random.sample(A, len(A)) returns a list where the elements are shuffled
# this randomizes the position of the villagers
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

class KingAndAssassinsState(game.GameState):#stateclass
	'''Class representing a state for the King & Assassins game.'''

	DIRECTIONS = {
		'E': (0, 1),
		'W': (0, -1),
		'S': (1, 0),
		'N': (-1, 0)
	}
	
	BUFFER_SIZE = 2048

	def __init__(self, initialstate=KA_INITIAL_STATE, POPULATION=POPULATION, BOARD=BOARD):#initfun
		'''
		needs : self.POPULATION, self.BOARD
		'''
		self.POPULATION = POPULATION
		self.BOARD = BOARD
		self.APKING = 0
		self.APKNIGHT = 0
		self.CUFFS = False
		self.APCOM = 0
		self.SECONDKILL = 0
		super().__init__(initialstate)

	def _nextfree(self, x, y, dir):#nextfreefun
		nx, ny = self._getcoord((x, y, dir))

	def update(self, moves, player):#updatefun
		visible = self._state['visible']
		hidden = self._state['hidden']
		people = visible['people']
#-###################################################################################################
		for move in moves:
			# ('move', x, y, dir): moves person at position (x,y) of one cell in direction dir
			if move[0] == 'move':#updatemove
				x, y, d = int(move[1]), int(move[2]), move[3]
				if x<0 or y <0 or x>9 or y>9:
					raise game.InvalidMoveException('{}: cannot select out of the map'.format(move))
#-###################################################################################################	
				p = people[x][y]
				if p is None:
					raise game.InvalidMoveException('{}: there is no one to move'.format(move))
				nx, ny = self._getcoord((x, y, d))
				if nx<0 or ny <0 or nx>9 or ny>9:
					raise game.InvalidMoveException('{}: cannot move/act out of the map'.format(move))
#-###################################################################################################	
				new = people[nx][ny]
				if p == 'king' and ((x, y, d) == visible['castle'][0] or (x, y, d) == visible['castle'][1]):
					if self.APKING >= 1:
						self.APKING-=1
						people[x][y], people[nx][ny] = people[nx][ny], people[x][y]
						continue
#-###################################################################################################
				# King, assassins, villagers can only move on a free cell
				if p != 'knight' and new is not None:
					raise game.InvalidMoveException('{}: cannot move on a cell that is not free'.format(move))
				if p == 'king' and self.BOARD[nx][ny] == 'R':
					raise game.InvalidMoveException('{}: the king cannot move on a roof'.format(move))
				#if p in {'assassin'} + self.POPULATION and player != 0:
#-###################################################################################################
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
#-###################################################################################################
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
#-###################################################################################################
			# ('arrest', x, y, dir): arrests the villager in direction dir with knight at position (x, y)
			elif move[0] == 'arrest':#updatearrest
#-###################################################################################################
				if player != 1:
					raise game.InvalidMoveException('arrest action only possible for player 1')
				if not self.CUFFS:
					raise game.InvalidMoveException('arrest action only possible if the drawn card says so')
#-###################################################################################################
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
#-###################################################################################################					
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
					cost = 1 + self.SECONDKILL
					self.SECONDKILL = 1
					if self.APCOM >= cost:
						self.APCOM-=cost
					else:
						raise game.InvalidMoveException('{}: not enough AP left'.format(move))
#-###################################################################################################
					visible['killed']['knights'] += 1
					people[tx][ty] = None
#-###################################################################################################
				elif killer == 'knight' and target == 'assassin':
					if self.APKNIGHT >= 1:
						self.APKNIGHT-=1
					else:
						raise game.InvalidMoveException('{}: not enough AP left'.format(move))
#-###################################################################################################
					visible['killed']['assassins'] += 1
					people[tx][ty] = None
#-###################################################################################################
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
#-###################################################################################################
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
	def _getcoord(self, coord):#getcoordfun
		return tuple(coord[i] + KingAndAssassinsState.DIRECTIONS[coord[2]][i] for i in range(2))

	def winner(self):#winnerfun
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
		return self._state['hidden']['assassins'] is None

	def setassassins(self, assassins):#setassassinsfun
		self._state['hidden']['assassins'] = set(assassins)

	def prettyprint(self):#prettyprintfun
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
		return BUFFER_SIZE


class KingAndAssassinsServer(game.GameServer):#serverclass
	'''Class representing a server for the King & Assassins game'''

	def __init__(self, verbose=False, CARDS = CARDS, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):#initfun
		'''
		needs : self.CARDS, self.POPULATION
		'''
		self.POPULATION = POPULATION
		self.CARDS = CARDS
		super().__init__('King & Assassins', 2, KingAndAssassinsState(initialstate = KA_INITIAL_STATE, POPULATION = POPULATION, BOARD = BOARD), verbose=verbose)
		self._state._state['hidden'] = {
			'assassins': None,
			'cards': random.sample(self.CARDS, len(self.CARDS))
		}

	def _setassassins(self, move):#setassassinsfun
		state = self._state
		if 'assassins' not in move:
			raise game.InvalidMoveException('The dictionary must contain an "assassins" key')
		if not isinstance(move['assassins'], list):
			raise game.InvalidMoveException('The value of the "assassins" key must be a list')
		for assassin in move['assassins']:
			if not isinstance(assassin, str):
				raise game.InvalidMoveException('The "assassins" must be identified by their name')
			if not assassin in self.POPULATION:
				raise game.InvalidMoveException('Unknown villager: {}'.format(assassin))
		state.setassassins(move['assassins'])
		state.update([], 0)

	def applymove(self, move):#applymovefun
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
#-###################################################################################################			
			raise game.InvalidMoveException('A valid move must be a dictionary')


class KingAndAssassinsClient(game.GameClient):#clientclass
	'''Class representing a client for the King & Assassins game'''

	def __init__(self, name, server, verbose=False, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):
		'''
		needs : self.BOARD, self.POPULATION
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
		self.ABORTKILL = False
		self.turns = 0
		super().__init__(server, KingAndAssassinsState(initialstate = KA_INITIAL_STATE, POPULATION = POPULATION, BOARD = BOARD), verbose=verbose)

	def _handle(self, message):#handlefun
		pass
	
	def _radar(self, state, coord, alAP, enAP):#radarfun
		'''
		dangers esquivables
		dangers inesquivables
		priorite (assassin/roi en danger)
		=>si les 3 assassins sont reveles, on ne tient plus compte des villageois
		'''	
		pass
		
	def _getcoord(self, coord):#getcoordfun
		'''
		returns a tuple of coordinates deplaced in a certain DIRECTION (N, S, E, W)
		'''
		return tuple(coord[i] + self.DIRECTIONS[coord[2]][i] for i in range(2))
	
	def _getdir(self, movement):#getdirfun
		'''
		returns the DIRECTIONS elements that describe movement for x and y in a tuple
		WARNING : null values return S-E
		'''
		xs, ys = movement[0], movement[1]
		xdir = 'S' if xs >= 0 else 'N'
		ydir = 'E' if ys >= 0 else 'W'
		return (xdir, ydir)
	
	def _getopposite(self, dir):#getoppositefun
		oppositeDir = 'NS'.strip(dir)
		oppositeDir = 'WE'.strip(dir) if len(oppositeDir)==2 else oppositeDir
		oppositeDir = '' if len(oppositeDir)==2 else oppositeDir
		return oppositeDir
	
	def _validMove(self, peopleState, moveList):#validmovefun
		'''
		the purpose of this function is to determine whether a moveList will pass the
		kingAndAssassinsState._update(...) method without raising an error (except for cost error)
		it returns a dictionary containing :
		- the cost of the moveList
		- whether the moveList is legal or not (True/False)
		
		WARNING : a valid moveList can raise an error in the _update method if there is not enough
		AP left for this moveList
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
		this method's purpose is to simulate a moveList on a copy of peopleState
		to check the new state of the game. 
		
		Warnings : 
		The moveList MUST return True when called with _validMove
		peopleState may be modified
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
		this function convert a string command as described in kingAndAssassinsHumanClient class
		into a list of commands as described in _nextmove from kingAndAssassinsClient class
		'''
		movesList = []
		movesString = movesString.strip(' +')
		movesStringList = movesString.split(' + ')
		for i in range(len(movesStringList)):
			movesStringList[i] = movesStringList[i].split(' ')#regex ' + ' ou '+'
			x = movesStringList[i][0]
			y = movesStringList[i][1]
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
							x, y = str(int(x)+self.DIRECTIONS[copyH[1]][0]), str(int(y)+self.DIRECTIONS[copyH[1]][1])
			movesList+=copy.copy(commandsList)
		return movesList
	
	def _validObjective(self, peopleState, kingState, iPos, commands, APLeft):#validobjectivefun
		'''
		this function tests a set of actions (commands) on the piece at iPos for the price of APLeft
		it returns a dictionary with the following keys :
		{legal, movesList, APLeft, peopleStateCopy, kingState} if the set of actions can be done
		{legal, validCommands, APLeft, fatalMoveString, lastValidPosition} if it can not be done
		
		peopleState is not modified
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
				fPos = (movesList[i][1], movesList[i][2])
				return {'legal':False, 'validCommands':validCommands, 'history':history, 'APLeft':APLeft, 'fatalMoveString':commands[3*i:3*i+3],
					'lastValidPosition':fPos}
		return {'legal':True, 'movesList':movesList, 'APLeft':APLeft, 'peopleStateCopy':peopleStateCopy, 'kingState':kingState}
	
	def _stateObjective(self, peopleState, kingState, iPos, fPos, objective, APAvailable, nDetour = 0, dirPrevious = ''):#stateobjectivefun
		'''
		this function searches for a path to accomplish objective at position fPos from position iPos with APAvailable on peopleState
		'''
		#etat actuel : PathFinding pour tous les pions, opérationnel. :) YAY (:
		#nécessite une analyse et une révision complète : la structure du code est dégueulasse, et de plus la fonction
		#teste énormément de mouvements "tentaculaires" inutiles (conditions supplémentaires à rajouter). La complexité du code
		#nécessite une explication détaillée pour la relecture
		#manoeuvre d'évitement possible
		#gère le push des chevaliers
		#=> WARNING : cette fonction est récursive
		if iPos == fPos and objective == 'm':
			return {'completed':True, 'movesList':[], 'APLeft':APAvailable, 'peopleState':peopleState, 'kingState':kingState,
				'lastPosition':iPos}
		elif iPos == fPos and objective != 'm' and objective != 'r':
			return None #erreur, on essaye d'effectuer une action autre que deplacement sur la case ou on se trouve
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
		#execute tous les mouvements en x, tous les mouvements en y sauf un, et l'objectif en y)
		regress = False
		if stated[1] == dirPrevious:
			ended = False
			validCommands = ''
			pushes = []
			ydone = 0
			xdone = 0
			APLeft = APAvailable
			fatalCommand = stated[:3]
			fatalCoord = (str(iPos[0]),str(iPos[1]))
			regress = True
		else:
			validObjective = self._validObjective(peopleState, kingState, iPos, stated, APAvailable)
			ended = validObjective['legal']
		forceEnded = False
		detourEnded = False
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
			print("ndtour = "+str(nDetour))
			print("dprev  = "+str(dirPrevious))
			'''
			if nDetour>0:
				if fatalCommand[1]==xdir:
					tryOppositeDirection = False
					if abs(y)-ydone == 0:
						if ydir != dirPrevious:
							detour = ''.join(['m',ydir,' '])
							detourObjective = self._validObjective(peopleState, kingState, iPos, ''.join([validCommands,detour]), APAvailable)
							tryOppositeDirection = not detourObjective['legal']
							if detourObjective['legal']:
								newIPos = self._getcoord((int(detourObjective['movesList'][-1][1]), 
									int(detourObjective['movesList'][-1][2]), detourObjective['movesList'][-1][3]))
								dirPrevious = self._getopposite(ydir)
								statedDetourObjective = self._stateObjective(detourObjective['peopleStateCopy'], 
									detourObjective['kingState'], newIPos, fPos, objective, detourObjective['APLeft'], nDetour-1, dirPrevious)
								tryOppositeDirection = not statedDetourObjective['completed']
								if statedDetourObjective['completed']:
									detourEnded = True
									break
						else:
							tryOppositeDirection = True
					if (abs(y)-ydone > 0 or tryOppositeDirection) and iydir != dirPrevious:
						detour = ''.join(['m',iydir,' '])
						detourObjective = self._validObjective(peopleState, kingState, iPos, ''.join([validCommands,detour]), APAvailable)
						if detourObjective['legal']:
							newIPos = self._getcoord((int(detourObjective['movesList'][-1][1]), int(detourObjective['movesList'][-1][2]),
								detourObjective['movesList'][-1][3]))
							dirPrevious = self._getopposite(iydir)
							statedDetourObjective = self._stateObjective(detourObjective['peopleStateCopy'], detourObjective['kingState'],
								newIPos, fPos, objective, detourObjective['APLeft'], nDetour-1, dirPrevious)
							if statedDetourObjective['completed']:
								detourEnded = True
								break
				elif fatalCommand[1]==ydir:
					tryOppositeDirection = False
					if abs(x)-xdone == 0:
						if xdir != dirPrevious:
							detour = ''.join(['m',xdir,' '])
							detourObjective = self._validObjective(peopleState, kingState, iPos, ''.join([validCommands,detour]), APAvailable)
							tryOppositeDirection = not detourObjective['legal']
							if detourObjective['legal']:
								newIPos = self._getcoord((int(detourObjective['movesList'][-1][1]), int(detourObjective['movesList'][-1][2]),
									detourObjective['movesList'][-1][3]))
								dirPrevious = self._getopposite(xdir)
								statedDetourObjective = self._stateObjective(detourObjective['peopleStateCopy'], detourObjective['kingState'],
									newIPos, fPos, objective, detourObjective['APLeft'], nDetour-1, dirPrevious)
								tryOppositeDirection = not statedDetourObjective['completed']
								if statedDetourObjective['completed']:
									detourEnded = True
									break
						else:
							tryOppositeDirection = True
					if (abs(x)-xdone > 0 or tryOppositeDirection) and ixdir != dirPrevious:
						detour = ''.join(['m',ixdir,' '])
						detourObjective = self._validObjective(peopleState, kingState, iPos, ''.join([validCommands,detour]), APAvailable)
						if detourObjective['legal']:
							newIPos = self._getcoord((int(detourObjective['movesList'][-1][1]), int(detourObjective['movesList'][-1][2]),
								detourObjective['movesList'][-1][3]))
							dirPrevious = self._getopposite(ixdir)
							statedDetourObjective = self._stateObjective(detourObjective['peopleStateCopy'], detourObjective['kingState'],
								newIPos, fPos, objective, detourObjective['APLeft'], nDetour-1, dirPrevious)
							if statedDetourObjective['completed']:
								detourEnded = True
								break
			if fatalCommand[1]==ydir and abs(x)-xdone >=1:
				if abs(y)-ydone == 1:
					if abs(x)-xdone == 1:
						stated = ''.join([
							validCommands,
							''.join(['m',xdir,' ']),
							''.join([objective,ydir,' '])])
					else:
						stated = ''.join([
							validCommands,
							''.join(['m',xdir,' ']),
							''.join(['m',ydir,' ']),
							(abs(x)-xdone-2)*''.join(['m',xdir,' ']),
							''.join([objective,xdir,' '])])
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
				if abs(x)-xdone ==0:
					if abs(y)-ydone ==0:
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
				lastTruePushIndex = len(pushes)-1-pushes[::-1].index(True) #index du dernier element de pushes (so stupid... => rindex())
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
			#fin de boucle
			validObjective = self._validObjective(peopleState, kingState, iPos, stated, APAvailable)
			ended = validObjective['legal']
		#move impossible
		if forceEnded:
			reason = 'notFullyCompleted'#a modifier
#-###################################################################################################
			if longestValidCommands != '':
				return {'completed':False, 'movesList':self._prettyCommands(str(iPos[0])+' '+str(iPos[1])+' '+longestValidCommands),
					'APLeft':APLeft, 'error':reason}
			else:
				return {'completed':False, 'movesList':[], 'APLeft':APLeft, 'error':reason}
		elif detourEnded:
			movesList = detourObjective['movesList']+statedDetourObjective['movesList']
			APLeft = statedDetourObjective['APLeft']
			peopleState = statedDetourObjective['peopleState']
			kingState = statedDetourObjective['kingState']
			newcoord = fPos if objective == 'm' else (movesList[-1][1], movesList[-1][2])
			return {'completed':True, 'movesList':movesList, 'APLeft':APLeft, 'peopleState':peopleState, 'kingState':kingState,
				'lastPosition':newcoord}
		else:
			#move validé
			movesList = validObjective['movesList']
			APLeft = validObjective['APLeft']
			peopleState = validObjective['peopleStateCopy']
			kingState = validObjective['kingState']
			newcoord = fPos if objective == 'm' else (movesList[-1][1], movesList[-1][2])
			return {'completed':True, 'movesList':movesList, 'APLeft':APLeft, 'peopleState':peopleState, 'kingState':kingState,
				'lastPosition':newcoord}
	
	def _minimizeObjective(self, peopleState, kingState, iPos, fPos, objective, APAvailable, assassinPattern = True):#minimizeobjectivefun
		'''
		this function try to accomplish objective with a minimal amount of AP within APAvailable
		Revamped, it is now 0-8 times faster (15 seconds for test1, (128 seconds before))
		'''
		#WARNING : vérifier que la nouvelle version traite bien tous les cas intéressants (possible perte de certains cas)
		distance = abs(fPos[0]-iPos[0]) + abs(fPos[1]-iPos[1])
		if assassinPattern :
			minCostDist = distance//2
			maxCostDist = distance
		else:
			minCostDist = distance
			maxCostDist = (distance//2)*3+(distance%2)*3
		print("Searching for a valid path (please be patient)...")
		tic = time.time()
		for AP in range(minCostDist, APAvailable+1):
			if assassinPattern:
				minDet = (AP-maxCostDist)//2
				maxDet = AP-minCostDist
			else:
				minDet = (AP-maxCostDist)//3 if (AP-maxCostDist)%3 ==0 else (AP-maxCostDist)//3+1
				maxDet = (AP-minCostDist)//2
			if minDet <0:
				minDet = 0
			if maxDet <0:
				maxDet = 0
			for detour in range(minDet, maxDet+1):
				stateObjective = self._stateObjective(peopleState, kingState, iPos, fPos, objective, AP, detour)
				sys.stdout.write(chr(13))
				sys.stdout.write("AP : "+str(AP)+" detours : "+str(detour))
				sys.stdout.flush()
				if stateObjective['completed']:
					print("\r\n... Succeeded ("+str(time.time()-tic)+" seconds)")
					return stateObjective
		print("\r\n... Failed ("+str(time.time()-tic)+" seconds)")
		return stateObjective
	
	def _nextmove(self, state):#nextmovedrunkheartfun
		'''
		 Two possible situations:
		 - If the player is the first to play, it has to select his/her assassins
		   The move is a dictionary with a key 'assassins' whose value is a list of villagers' names
		 - Otherwise, it has to choose a sequence of actions
		   The possible actions are:
		   ('move', x, y, dir): moves person at position (x,y) of one cell in direction dir
		   ('arrest', x, y, dir): arrests the villager in direction dir with knight at position (x, y)
		   ('kill', x, y, dir): kills the assassin/knight in direction dir with knight/assassin at position (x, y)
		   ('attack', x, y, dir): attacks the king in direction dir with assassin at position (x, y)
		   ('reveal', x, y): reveals villager at position (x,y) as an assassin
		'''
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
					#IA
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
					#IA
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

class KingAndAssassinsHumanClient(game.GameClient):#humanclass
	'''Class representing a client for the King & Assassins game'''

	def __init__(self, name, server, verbose=False, POPULATION = POPULATION, BOARD = BOARD, KA_INITIAL_STATE = KA_INITIAL_STATE):#initfun
		'''
		needs self.POPULATION
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
		Two possible situations:
		  -	If the player is the first to play, it has to select his/her assassins
			i.e.: "mo pl ap" 
			This move will select the monk, the appleman and the plumwoman as the 3 assassins
		  -	Otherwise, it has to choose a sequence of actions
			First it has to select the position of the targetted piece
			Second it has to write a pattern of actions(>directions if necessary)
			actions commands are :
			  -	"m" : move
			  -	"a"	: arrest
			  -	"k"	: kill
			  -	"t"	: attack
			  -	"r"	: reveal
			directions commands are :
			  -	"N" : north
			  -	"E"	: east
			  - "W"	: west
			  - "S"	: south
			i.e.: "9 8 mW mW mW mW aW"
			This move will select a knight located at line 9, column 8
			Make it move 4 times to the left and then arrest a villager to the left
			i.e.: "5 5 r mS mE mS tE"
			This move will select a villager who is a hidden assassin at line 5, column 5
			Reveal that this is an assassin, make it move down, right, down
			then attack the king to the right once
			Third it has to end is turn
			ending command is :
			  - "end"
			
			MORE =>
			
			multi-move : 
			i.e.: "9 8 mW mW + 7 7 mS mE kS" ENTER
				  "end" ENTER
			is the same as :
			i.e.: "9 8 mW mW" ENTER
				  "7 7 mS mE kS" ENTER
				  "end" ENTER
			
			First way (with +) is recommended as it is not possible to cancel
			a move after ENTER
			
			Player can re-select a piece that has already been moved by its new
			coordinates
			i.e.: "9 8 mW + 9 7 mW" ENTER
				  "end" ENTER
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
						humanMoveList[i] = humanMoveList[i].split(' ')#regex ' + ' ou '+'
#-###################################################################################################
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