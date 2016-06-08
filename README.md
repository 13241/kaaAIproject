# kaaAIproject
The game King and Assassins with AI, single player, two players and launcher. You can run the tests too.

On Windows : launch kaalauncher.py

On MacOS : find a valid command for your terminal to use kaalauncher.py
		   or launch 3 terminals manually
		   
# Commentaires

La version du jeu a été modifiée de telle sorte que toutes les règles 
soient présentes et fonctionnelles (contrairement à la version inachevée sur
le repo du cours)

La réflexion sur l'IA en est au stade suivant :
	etat actuel : PathFinding pour tous les pions quel que soit le terrain et le nombre d'AP.
	Les fonctions de pathfinding trouvent le chemin le plus court pour effectuer tout type d'action, 
	sont capables d'effectuer des détours, de tuer des obstacles (si possible).
	
Vous pouvez jouer au jeu sans IA, pour ce faire, lancez des clients "humanClient". Un mode d'emploi
du mode sans IA est présent dans le fichier glossary.py : #command

Vous pouvez lancer les tests contenus dans test.py à partir du launcher (qui ne fonctionne que sous windows). 
Une description des tests est présente dans chaque classe qui les représente sous forme de commentaire.
Un schéma des tests est présent dans réflexion IA.xlsx.
Vous pouvez aussi lancer des tests manuellement, pour ce faire : à la place de lancer un serveur avec la commande 
"server", utilisez : "testxServer" où x est un numéro. 
Pour les clients, utilisez : "testxClient". (le même test doit être utilisé pour les 3)

Des schémas de réflexion se trouvent dans le fichier exel reflexion IA. 
	
# processus

la méthode _nextmove détermine des "objectifs" pour les pions, c'est-à-dire
que pour un pion donné, elle détermine une action à faire sur une certaine
case (qui peut être à une distance plus grande que 1 du pion)

ces objectifs seront déterminés à partir de fonctions "radar" qui évalueront
(seule celle du roi existe déjà) les menaces où les gènes pour un pion, et
les classeront par ordre de priorité. Les objectifs prioritaires sont traités
en premiers. S'il n'y a pas d'objectif particulier à remplir, les pions se dirigeront
vers un état qui les rapproche de la victoire.

elle appelle ensuite la méthode _minimizeObjective pour un objectif. Cette
méthode permet de déterminer le coùt le moins cher pour effectuer l'objectif
en appelant successivement la méthode _stateObjective avec des paramètres
différents

pour chaque série de paramètres, on appelle _stateObjective pour cet objectif. Cette
méthode recherche un chemin permettant au pion d'aller effectuer l'action
voulue sur la case voulue. Le format de ce chemin est décrit dans
glossary.py (voir hashtag command)

pour chaque chemin, on vérifie qu'il est réalisable en passant par la 
méthode _validObjective. Cette méthode utilise :

_prettyCommands qui va convertir le chemin dans un format compatible
avec le serveur (liste d'actions)

_validMove qui vérifie qu'une action est légale dans l'état actuel du jeu

_updateCopy qui met à jour une copie de l'état actuel du jeu pour chaque
move validé par _validMove

# état actuel de l'IA

les villageois et les chevaliers se mettent en formation "coeur", c'est la
fête. Le roi, ivre, décide de rentrer au chateau en zigzaguant dans la foule.
Les assassins font la grêve.

# UPDATES

06/06/2016 : Désormais, un nouveau log des updates s'ajoutera au précédent au lieu
de fusionner avec.

# UPDATE 08/06/2016

Mise à jour des commentaires en anglais (il y a surement plein de fautes désolé)

# UPDATE 06/06/2016

Ajout de _radarKingDefensive, _getcoords ainsi que test4. Ces méthodes permettent
de chercher et de classer les menaces pour le roi sur le terrain de jeu par
ordre de priorité. Beaucoup de fonctionnalités radar sont prévues, et verront
le jour dans de nouvelles fonctions (ou fusionneront avec celle-ci). Le test
vérifie que la fonction fonctionne correctement.

radars prévus : radarKingOffensive/Defensive, radarKnightOffensive/Defensive,
radarVillagerOffensive/Defensive

# UPDATE 06/06/2016 et précédentes

CERTAINES INFORMATIONS MENTIONEES CI-DESSUS PEUVENT ETRE OBSOLETES

Le PATHFINDING (methode _stateObjective) gère désormais les détours, peu
importe le nombre.

Le PATHFINDING cherche désormais le moyen le moins cher d'atteindre une 
destination (+effectuer une action) grace à la méthode _minimizeObjective

Le PATHFINDING gère désormais les pushes des chevaliers. 

Le PATHFINDING gère désormais le kill des assassins ou des chevaliers
lors de la recherche d'un chemin.

Ce qu'il manque : la gestion coordonnée de tous les pions du joueur (et pas seulement
qu'un seul)

GROS aménagement du code principal pour effectuer des tests, 
utiliser le launcher sous windows pour lancer les tests