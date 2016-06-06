# kaaAIproject
The game King and Assassins with AI, single player, two players and launcher

On Windows : launch kaalauncher.py

On MacOS : find a valid command for your terminal to use kaalauncher.py
		   or launch 3 terminals manually
		   
# Commentaires

La version du jeu a été modifiée de telle sorte que toutes les règles 
soient présentes et fonctionnelles (contrairement à la version inachevée sur
le repo du cours)

La réflexion sur l'IA en est au stade suivant :
	etat actuel : PathFinding pour le ROI et les VILLAGEOIS (non assassins)
	utilise uniquement la distance minimale (pas de prise en compte des AP, pas de manoeuvre d'évitement ayant un cout de deplacement)
	=> doit encore énormément évoluer
	
Vous pouvez jouer au jeu sans IA, pour ce faire, lancez des clients "humanClient"
et utilisez le commentaire de la methode _nextmove de la classe kingAndAssassinsHumanClient
pour la syntaxe à utiliser pour jouer les tours
	
# processus

la méthode _nextmove détermine des "objectifs" pour les pions, c'est-à-dire
que pour un pion donné, elle détermine une action à faire sur une certaine
case (qui peut être à une distance plus grande que 1 du pion)

elle appelle ensuite la méthode _stateObjective pour cet objectif. Cette
méthode recherche un chemin permettant au pion d'aller effectuer l'action
voulue sur la case voulue. Le format de ce chemin est décrit dans
la méthode _nextmove de la classe kingAndAssassinshumanClient

pour chaque chemin, on vérifie qu'il est réalisable en passant par la 
méthode _validObjective. Cette méthode utilise :

_prettyCommands qui va convertir le chemin dans un format compatible
avec le serveur (liste d'actions)

_validMove qui vérifie qu'une action est légale dans l'état actuel du jeu

_updateCopy qui met à jour une copie de l'état actuel du jeu pour chaque
move validé par _validMove


la réflexion pour la recherche du chemin se trouve dans le fichier exel 
reflexion IA. 

réflexion utilisée : 

on commence par parcourir toute la distance en colonnes pour arriver 
à une position verticale par rapport à la cible.

On parcourt ensuite cette distance verticale.

Si un mouvement dans la direction horizontale échoue, on le remplace
par un mouvement dans la direction verticale.

Si mouvement dans la direction verticale échoue, on annule le précédent
mouvement dans la direction horizontale, on rajoute tous les derniers
mouvements dans la direction verticale + 2, et on ajoute ensuite
un mouvement dans la direction horizontale.
On reprend l'algorithme de base.


# état actuel de l'IA

les villageois et les chevaliers se mettent en formation "coeur", c'est la
fête. Le roi, ivre, décide de rentrer au chateau en zigzaguant dans la foule.
Les assassins font la grêve.

# UPDATES

06/06/2016 : Désormais, un nouveau log des updates s'ajoutera au précédent au lieu
de fusionner avec.

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

à restructurer : réflexion IA.xlsx ainsi que la fonction _stateObjective

Les commentaires des fonctions ne sont plus tous à jour.