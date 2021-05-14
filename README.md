## Projet IA Abalone ##

## Noms et matricules

    Imane OURRAOUI 18316

    Quentin JADOUL 18155

## Strategie

    Listage des moves:

    - L'ia va lister tout les mouvements possibles, sans bad moves ni suicides

    - Elle va également générer tout les moves offensifs (Offensif = adversaire poussé hors du plateau)

    - Elle génère une troisième liste, contenant les moves offensifs d'un train de trois billes poussant deux billes (Long Attack). De cette maniere, si l'adveraire ne bouge pas, un autre move offensif est possible.

    Choix du move:

    - Si il existe au moins un move longAttack elle va choisir aléatoirement parmi ceux ci

    - Si il existe au moins un move offensif elle va choisir aléatoirement parmi ceux ci

    - Sinon elle choisit aléatoirement parmi les moves classiques


## Bibliothèques utilisés

    - Random:
        Ce module qui regroupe des fonctions permettant de simuler le hasard. Par exemple choisir un entier aléatoire, choisir une valeur dans une liste, mélanger une liste,...
    - Sys:
        Ce module fournit un accès à certaines variables utilisées et maintenues par l'interpréteur, et à des fonctions interagissant fortement avec ce dernier.
        Permet par exemple un accès direct aux arguments de la ligne de commande, via la liste sys.argv
    - Socket:
        Les sockets servent à établir une transmission de flux de données (octets) entre deux machines ou applications, dans ce cas si entre le client (L'ia) et le serveur.

