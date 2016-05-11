from kingandassassins import *



'''
POPULATION = {
	'monk', 'plumwoman', 'appleman', 'hooker', 'fishwoman', 'butcher',
	'blacksmith', 'shepherd', 'squire', 'carpenter', 'witchhunter', 'farmer'
}
listPopul = [item for item in POPULATION]
print(listPopul[2:5])

cost = 1 if True else 2
print(cost)
'''

'''
humanMove = "mo ap pl\n"
print(humanMove.strip("\n"))
print(humanMove.split("+"))
humanMove = set(acronym for acronym in humanMove.split(' '))
humanMove = [POPULATION_el for acronym in humanMove for POPULATION_el in POPULATION if acronym==POPULATION_el[0:2]]
print(humanMove)

print(humanMove[-2])

test = [(i,j) for i in range(10) for j in range(3)] #deuxieme for inclus dans le premier avec cette ecriture
print(test)


'''


DIRECTIONS = {
		(0, 1):'E',
		(0, -1):'W',
		(1, 0):'S',
		(-1, 0):'N'
	}
print(DIRECTIONS[(0,1)])