#action
'''
Two possible situations:
	{'actions': [
		(action, x, y (, dir)),
		...]}
	dictionary with a key 'actions' whose value is a list of tuple containing informations to execute an action : 
		action : characterize an action
			'move' : moves person at position (x,y) of one cell in direction dir
			'arrest' : arrests the villager in direction dir with knight at position (x, y)
			'kill' : kills the assassin/knight in direction dir with knight/assassin at position (x, y)
			'attack' : attacks the king in direction dir with assassin at position (x, y)
			'reveal' : reveals villager at position (x, y) as an assassin
		x : index of a line (int)
		y : index of a column (int)
		dir : characterize a direction
			'N' : north
			'S' : south
			'E' : east
			'W' : west

	OR

	{'assassins': [
		name, 
		...]}
	dictionary with a key 'assassins' whose value is a list of villagers' names : 
		name : see POPULATION >element
'''

#command
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

#CARDS
'''
(
	(AP king, AP knight, Fetter, AP population/assassins),
	...)
tuple containing tuple containing informations given by the cards drawn each turn : 
	AP king : action points for the king (int)
	AP knight : action points for the knights (int)
	Fetter : indicate wheter the knights can imprison a villager this turn (True) or not (False)
	AP population/assassins : action points for the population/assassins (int)
'''

#POPULATION
'''
{
	name,
	...}
set of string corresponding to the names of the villagers :
	name : name of a villager (str)
'''

#BOARD
'''
(
	(ground-level, ...),
	...)
tuple (lines) containing tuple (columns) of string characterizing the landscape of the game (roofs or ground) :
	ground level :
		'G' : ground
		'R' : roof
'''

#KNIGHTS
'''
{
	(x, y),
	...}
set containing the coordinates of the knights (tuple)
	see action >elements
'''

#VILLAGERS
'''
{
	(x, y),
	...}
set containing the coordinates of the villagers (tuple)
	see action >elements
'''

#PEOPLE
'''
[
	[(x, y), ...],
	...]
list of list containing the coordinates of the pawns
	see action >elements
'''

#KA_INITIAL_STATE
'''
{
	'board': see BOARD,
	'people': see PEOPLE,
	'castle': [(2, 2, 'N'), (4, 1, 'W')],
	'card': see CARDS >element,
	'king': 'healthy',
	'lastopponentmove': see action,
	'arrested': [] see POPULATION >elements,
	'killed': {
		'knights': 0,
		'assassins': 0
	}
dictionary whose keys characterize the state of the game during a turn
'''