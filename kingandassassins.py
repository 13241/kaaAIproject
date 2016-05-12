#!/usr/bin/env python3
# kingandassassins.py
# Author: Sébastien Combéfis
# Version: April 29, 2016

#top
import argparse
import json
import random
import socket
import sys
import traceback
import copy
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

#vouees a disparaitre (global variable = mauvaise idee)
#-###################################################################################################
metax =9
metay =9

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

	def __init__(self, initialstate=KA_INITIAL_STATE):#initfun
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
			print(move)
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
				if p == 'king' and BOARD[nx][ny] == 'R':
					raise game.InvalidMoveException('{}: the king cannot move on a roof'.format(move))
				#if p in {'assassin'} + POPULATION and player != 0:
#-###################################################################################################
				if p in {'assassin'} | POPULATION and player != 0:
					raise game.InvalidMoveException('{}: villagers and assassins can only be moved by player 0'.format(move))
				if p in {'king', 'knight'} and player != 1:
					raise game.InvalidMoveException('{}: the king and knights can only be moved by player 1'.format(move))
				# Move granted if cell is free
				if new is None:
					cost = 0
					if BOARD[x][y] == BOARD[nx][ny]:
						cost = 1
					elif BOARD[x][y] == 'G':
						cost = 1 if p == 'assassin' else 2
					else:
						cost = 0 if p == 'assassin' else 1
					if p == 'king' and self.APKING >= cost:
						self.APKING-=cost
					elif p == 'knight' and self.APKNIGHT >= cost:
						self.APKNIGHT-=cost
					elif p in {'assassin'} | POPULATION and self.APCOM >= cost:
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
					if BOARD[x][y] == 'R' or BOARD[nx][ny] == 'R':
						knightIsUp = True
					while (BOARD[nx][ny] == 'G' or knightIsUp) and new is not None and new != 'knight' and new != 'king':
						news.append((nx,ny))
						if BOARD[nx][ny] == 'G':
							knightIsUp = False
						nx, ny = self._getcoord((nx, ny, d))
						if nx<0 or ny<0 or nx>9 or ny>9:
							break
						new = people[nx][ny]
						if new is None and (BOARD[nx][ny] == 'G' or knightIsUp):
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
				if target not in POPULATION:
					raise game.InvalidMoveException('{}: only villagers can be arrested'.format(move))
				if BOARD[tx][ty] == 'R' and BOARD[x][y] == 'G':
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
				if BOARD[tx][ty] == 'R' and BOARD[x][y] == 'G':
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

	def __init__(self, verbose=False):#initfun
		super().__init__('King & Assassins', 2, KingAndAssassinsState(), verbose=verbose)
		self._state._state['hidden'] = {
			'assassins': None,
			'cards': random.sample(CARDS, len(CARDS))
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
			if not assassin in POPULATION:
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

	def __init__(self, name, server, verbose=False):
		self.__name = name
		self.assassins = []
		self.CODESACTIONS = {'m':'move', 'r':'reveal', 't':'attack', 'a':'arrest', 'k':'kill'}
		self.DIRECTIONS = {
			'E': (0, 1),
			'W': (0, -1),
			'S': (1, 0),
			'N': (-1, 0)
		}
		self.INVDIRECTIONS = {
			(0, 1):'E',
			(0, -1):'W',
			(1, 0):'S',
			(-1, 0):'N'
		}
		self.CUFFS = False
		self.TESTSECONDKILL = 0
		self.ABORTKILL = False
		super().__init__(server, KingAndAssassinsState, verbose=verbose)

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
		return a tuple of coordinates deplaced in a certain DIRECTION (N, S, E, W)
		'''
		return tuple(coord[i] + self.DIRECTIONS[coord[2]][i] for i in range(2))
	
	def _validMove(self, people, move):#validmovefun
		'''
		the purpose of this function is to determine whether a move will pass the
		kingAndAssassinsState._update(...) method without raising an error (except for cost error)
		it returns a tuple containing 2 parameters : 
		- the cost of the move
		- whether the move is legal or not (True/False)
		
		WARNING : a valid move can raise an error in the _update method if there is not enough
		AP left for this move
		'''
		player = self._playernb
		if move[0] == 'move':#validmovemove
			x, y, d = int(move[1]), int(move[2]), move[3]
			if x<0 or y <0 or x>9 or y>9:
				return (0,False) #cannot select out of the map
			p = people[x][y]
			if p is None:
				return (0,False) #there is no one to move
			nx, ny = self._getcoord((x, y, d))
			if nx<0 or ny <0 or nx>9 or ny>9:
				return (0,False) #cannot move/act out of the map
			new = people[nx][ny]
			if p == 'king' and ((x, y, d) == (2, 2, 'N') or (x, y, d) == (4, 1, 'W')):
				return (1, True)
			# King, assassins, villagers can only move on a free cell
			if p != 'knight' and new is not None:
				return (0,False) #cannot move on a cell that is not free
			if p == 'king' and BOARD[nx][ny] == 'R':
				return (0,False) #the king cannot move on a roof
			if p in {'assassin'} | POPULATION and player != 0:
				return (0,False) #villagers and assassins can only be moved by player 0
			if p in {'king', 'knight'} and player != 1:
				return (0,False) #the king and knights can only be moved by player 1
			# Move granted if cell is free
			if new is None:
				cost = 0
				if BOARD[x][y] == BOARD[nx][ny]:
					cost = 1
				elif BOARD[x][y] == 'G':
					cost = 1 if p == 'assassin' else 2
				else:
					cost = 0 if p == 'assassin' else 1
				return (cost, True)
			# If cell is not free, check if the knight can push villagers
			else:
				news = [(x,y)]
				pushable = False
				knightIsUp = False
				if BOARD[x][y] == 'R' or BOARD[nx][ny] == 'R':
					knightIsUp = True
				while (BOARD[nx][ny] == 'G' or knightIsUp) and new is not None and new != 'knight' and new != 'king':
					news.append((nx,ny))
					if BOARD[nx][ny] == 'G':
						knightIsUp = False
					nx, ny = self._getcoord((nx, ny, d))
					if nx<0 or ny<0 or nx>9 or ny>9:
						break
					new = people[nx][ny]
					if new is None and (BOARD[nx][ny] == 'G' or knightIsUp):
						pushable = True
				if pushable:
					return (1, True)
				else:
					return (0,False) #The knight can not push this way
		# ('arrest', x, y, dir): arrests the villager in direction dir with knight at position (x, y)
		elif move[0] == 'arrest':#validmovearrest
			if player != 1:
				return (0,False) #arrest action only possible for player 1
			if not self.CUFFS:
				return (0,False) #arrest action only possible if the drawn card says so
			x, y, d = int(move[1]), int(move[2]), move[3]
			arrester = people[x][y]
			if arrester != 'knight':
				return (0,False) #the attacker is not a knight
			tx, ty = self._getcoord((x, y, d))
			target = people[tx][ty]
			if target not in POPULATION:
				return (0,False) #only villagers can be arrested
			if BOARD[tx][ty] == 'R' and BOARD[x][y] == 'G':
				return (0,False) #arrest action impossible from below
			return (1, True)				
		# ('kill', x, y, dir): kills the assassin/knight in direction dir with knight/assassin at position (x, y)
		elif move[0] == 'kill':#validmovekill
			x, y, d = int(move[1]), int(move[2]), move[3]
			killer = people[x][y]
			cost = 0
			if killer == 'assassin' and player != 0:
				return (0,False) #kill action for assassin only possible for player 0
			if killer == 'knight' and player != 1:
				return (0,False) #kill action for knight only possible for player 1
			tx, ty = self._getcoord((x, y, d))
			target = people[tx][ty]
			if target is None:
				return (0,False) #there is no one to kill
			if BOARD[tx][ty] == 'R' and BOARD[x][y] == 'G':
				return (0,False) #kill action impossible from below
			if killer == 'assassin' and target == 'knight':
				cost = 1 + self.TESTSECONDKILL
				return (cost, True)
			elif killer == 'knight' and target == 'assassin':
				return (1, True)
			else:
				return (0,False) #forbidden kill
		# ('attack', x, y, dir): attacks the king in direction dir with assassin at position (x, y)
		elif move[0] == 'attack':#validmoveattack
			if player != 0:
				return (0,False) #attack action only possible for player 0
			x, y, d = int(move[1]), int(move[2]), move[3]
			attacker = people[x][y]
			if attacker != 'assassin':
				return (0,False) #the attacker is not an assassin
			tx, ty = self._getcoord((x, y, d))
			target = people[tx][ty]
			if target != 'king':
				return (0,False) #only the king can be attacked
			return (2, True)
		# ('reveal', x, y): reveals villager at position (x,y) as an assassin
		elif move[0] == 'reveal':#validmovereveal
			if player != 0:
				return (0,False) #action only possible for player 0
			x, y = int(move[1]), int(move[2])
			p = people[x][y]
			if p not in hidden['assassins']:
				return (0,False) #the specified villager is not an assassin
			return (0, True)
	
	def _updateCopy(self, people, kingsState, move):#updatecopyfun
		'''
		this method's purpose is to simulate a move on a copy of people positions
		to check the new state of the game. 
		
		Warnings : 
		The move MUST return True when called with _validMove
		people may be modified
		'''
		if move[0] == 'move':#updatecopymove
			x, y, d = int(move[1]), int(move[2]), move[3]
			p = people[x][y]
			nx, ny = self._getcoord((x, y, d))
			new = people[nx][ny]
			# Move granted if cell is free
			if new is None or p == 'king':
				people[x][y], people[nx][ny] = people[nx][ny], people[x][y]
			# If cell is not free the knight can push villagers
			else:
				news = [(x,y)]
				while new is not None:
					news.append((nx,ny))
					nx, ny = self._getcoord((nx, ny, d))
					new = people[nx][ny]
				while len(news)>0:
					loc = news.pop()
					people[loc[0]][loc[1]], people[nx][ny] = people[nx][ny], people[loc[0]][loc[1]]
					nx, ny = loc[0], loc[1]
		# ('arrest', x, y, dir): arrests the villager in direction dir with knight at position (x, y)
		elif move[0] == 'arrest':#updatecopyarrest
			x, y, d = int(move[1]), int(move[2]), move[3]
			tx, ty = self._getcoord((x, y, d))
			people[tx][ty] = None		
		# ('kill', x, y, dir): kills the assassin/knight in direction dir with knight/assassin at position (x, y)
		elif move[0] == 'kill':#updatecopykill
			x, y, d = int(move[1]), int(move[2]), move[3]
			killer = people[x][y]
			tx, ty = self._getcoord((x, y, d))
			if killer == 'assassin':
				self.TESTSECONDKILL = 1
			people[tx][ty] = None
		# ('attack', x, y, dir): attacks the king in direction dir with assassin at position (x, y)
		elif move[0] == 'attack':#updatecopyattack
			kingsState = 'injured' if kingsState == 'healthy' else 'dead'
		# ('reveal', x, y): reveals villager at position (x,y) as an assassin
		elif move[0] == 'reveal':#updatecopyreveal
			x, y = int(move[1]), int(move[2])
			people[x][y] = 'assassin'
		return (people, kingsState)
	
	def _prettyCommand(self, commands):#prettycommandfun
		'''
		this function convert a string command as described in kingAndAssassinsHumanClient class
		into a list of commands as described in _nextmove from kingAndAssassinsClient class
		'''
		finalCommandsList = []
		commands = commands.strip(' +')
		commandsList = commands.split(' + ')
		for i in range(len(commandsList)):
			commandsList[i] = commandsList[i].split(' ')#regex ' + ' ou '+'
			x = commandsList[i][0]
			y = commandsList[i][1]
			actionsList = commandsList[i][2:len(commandsList[i])]
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
		return finalCommandsList
	
	def _validObjective(self, people, kingsState, coord, commands, AP):#validobjectivefun
		'''
		this function tests a set of actions (commands) on the piece at coord for the price of AP
		it returns a tuple :
		(True, movesList, APremaining, peopleCopy, kingsState) if the set of actions can be done
		(False, validCommands, APremaining, fatalCommand, lastCoord) if it can not be done
		
		people is not modified
		'''
		moves = str(x)+' '+str(y)+' '+commands
		validCommands = ''
		movesList = self._prettyCommands(moves)
		peopleCopy = copy.deepcopy(people)
		for i in range(len(movesList)):
			response = self._validMove(peopleCopy, movesList[i])
			if response[1] and AP-response[0]>=0:
				AP-=response[0]
				updated = self._updateCopy(peopleCopy, kingsState, movesList[i])
				peopleCopy, kingsState = updated[0], updated[1]
				validCommands=commands[0:3*i+3]
			else:
				loc = (movesList[i][1], movesList[i][2])
				return (False, validCommands, AP, commands[3*i:3*i+3], loc)
		return (True, movesList, AP, peopleCopy, kingsState)
	
	def _stateObjective(self, people, kingsState, coord, target, objective, AP):#stateobjectivefun
		
		pass
	
	def _nextmove(self, state):#nextmovefun
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
			people = state['people']
			peopleCopy = copy.deepcopy(people)
			previousPeopleCopy = copy.deepcopy(people)
			if state['card'] is not None:
				self.CUFFS = state['card'][2]
			global metax
			global metay
			if state['card'] is None:
				self.assassins.append(people[7][1])
				self.assassins.append(people[1][7])
				self.assassins.append(people[2][1])
				return json.dumps({'assassins': [people[7][1], people[1][7], people[2][1]]}, separators=(',', ':'))
			else:
				if self._playernb == 0:
					commands = ''
					finalCommandsList = self._prettyCommand(commands)
					return json.dumps({'actions': finalCommandsList}, separators=(',', ':'))
				else:
					commands = ''
					APki = state['card'][0]
					xking, yking = metax, metay
					kingCommand = str(xking)+' '+str(yking)+' '
					commands+=kingCommand
					current = 'mN '
					total = ''
					while APki>0:
						coord = (xking, yking, current[1])
						kingCommand = str(xking)+' '+str(yking)+' '
						command = self._prettyCommand(kingCommand+current)[0]
						response = self._validMove(peopleCopy, command)
						if response[1] and APki-response[0]>=0:
							APki-=response[0]
							self._updateCopy(peopleCopy, copy.copy(state['king']), command)
							newcoord = self._getcoord(coord)
							xking, yking = newcoord[0], newcoord[1]
							total+=current
							current = 'mN '
						else:
							current = 'mW '
					metax, metay = xking, yking
					commands+=total
					finalCommandsList = self._prettyCommand(commands)
					return json.dumps({'actions': finalCommandsList}, separators=(',', ':'))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			a = input("Enter")

class KingAndAssassinsHumanClient(game.GameClient):#humanclass
	'''Class representing a client for the King & Assassins game'''

	def __init__(self, name, server, verbose=False):#initfun
		self.CODESACTIONS = {'m':'move', 'r':'reveal', 't':'attack', 'a':'arrest', 'k':'kill'}
		self.DIRECTIONS = {
			'E': (0, 1),
			'W': (0, -1),
			'S': (1, 0),
			'N': (-1, 0)
		}
		self.POPULATION = {
			'monk', 'plumwoman', 'appleman', 'hooker', 'fishwoman', 'butcher',
			'blacksmith', 'shepherd', 'squire', 'carpenter', 'witchhunter', 'farmer'
		}
		self.__name = name
		super().__init__(server, KingAndAssassinsState, verbose=verbose)

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
		KingAndAssassinsServer(verbose=args.verbose).run()
	elif args.component == 'client':
		KingAndAssassinsClient(args.name, (args.host, args.port), verbose=args.verbose)
	elif args.component == 'humanClient':
		KingAndAssassinsHumanClient(args.name, (args.host, args.port), verbose=args.verbose)
	a = input("Enter")
#bottom