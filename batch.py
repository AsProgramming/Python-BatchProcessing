#!/usr/bin/env python3.5
#  -*-coding:Utf-8 -*
#################################################
################  TP2 batch.py  #################
#												#
#   Programme qui lit un fichier de commande,   #
#   verifie si les commandes sont valides.      #
#   Affiche les commandes echouees a l'ecran    #
#   et les details dans un log d'erreurs.       #
#												#
########## Programmeur: Edwin Andino ############
#################################################

import os, sys

def main():

	fichier = verificationInit(sys.argv)	

	listeCommande =  recupererCommande(sys.argv)

	taille = len(listeCommande)

	tabBool = creationTab(taille, 0)

	commandeParallel(listeCommande, taille, fichier, tabBool)

##########
###	Methode qui verifie si les arguments necessaire sont present
##  @rg les noms de fichiers contenu dans sys.argv passer au debut du programme 
##########
def verificationInit(argumentsInitial):
	if(len(argumentsInitial) != 3):
		print("Usage: batch.py <fichier commande> <fichier sortie>", file=sys.stderr)
		sys.exit(1)
	else:
		fich = verifierSortie(argumentsInitial)
	return fich
##########
###	Methode qui verifie si le dossier de sortie existe ou non
##  @rg le nom de fichier
##########
def verifierSortie(chemin):
	chemin_fic = "./" + chemin[2]
	if os.path.isfile(chemin_fic):
		fichierSortie = open(chemin[2], "w")
	else:
		os.system("touch {0}".format(chemin[2]))
		fichierSortie = open(chemin[2], "w")

	return fichierSortie
##########
###	Methode qui met le dossier de commande dans un tableau
##  @rg le fichier entree par l'utilisateur
##########	
def recupererCommande(leFichier):
	fichier = open(sys.argv[1], "r")
	contenu = fichier.read().splitlines()
	return contenu

##########
###	Methode qui initialise le tableau necessaire
## @rg la taille du tableau a cree 
## @rg l'indice de distinction pour un tab de int ou de booleen 
##########
def creationTab(taille, indice):
	tab = []
	if indice == 0:
		for i in range(taille):
			tab.append(False)
	else:
		for i in range(taille):
			tab.append(-1)
	return tab
##########
###	Methode qui part les processus en parrallel
## @rg le tableau des commandes a executer
## @rg la taille du tableau a cree 
## @rg le fichier de sortie
## @rg le tableau de booleen pour les reussite et echecs des commandes
##########	
def commandeParallel(listeCommande, taille, fichier, tab):
	lire, ecrire = os.pipe()
	tube = os.pipe()
	os.dup2(tube[1], 2)
	sys_stdout = os.dup(1)
	os.close(1)
	for indice in range(taille):
		pid = os.fork()

		if pid == 0:
			os.close(lire)
			ecrivain = os.fdopen(ecrire, 'w')
			vrai = commandesSequentielle(listeCommande[indice], fichier, tube, sys_stdout)
			tab[indice] = vrai
			os.dup(sys_stdout)
			print("{} {}\n".format(indice, vrai), file=ecrivain, end="")
			ecrivain.close()
			os.close(sys_stdout)
			sys.exit(0)	

	os.dup(sys_stdout)
	os.close(ecrire)
	lecture = os.fdopen(lire)
	ligne = lecture.read()
	tabFinal = ligne.splitlines()
	lecture.close()
	for indice in range(taille):
		status, code = os.wait()
		valeur = tabFinal[indice].split(" ")
		if code == 0:
			tab[int(valeur[0])] = valeur[1]

	affichageTachesCompleter(taille, tab)
##########
###	Methode qui passe les commandes du tableau en sequences tableau necessaire
## @rg le tableau de commande 
## @rg le fichier de sortie 
## @rg le tube pour les erreur
## @rg l'indice du standard ouput pour l'impression des resultats  
##########
def commandesSequentielle(tab, fichier, tube, sys_stdout):
	os.dup(sys_stdout)
	continuer = True
	ct = 0
	ligne = tab.split(" _ ")
	tailleLigne = len(ligne)
	tabEchec = creationTab(tailleLigne, 1)

	for i in range(tailleLigne):
		cmd = ligne[i].split(" ")
		taille = len(cmd)
		verifier = os.system("which " + cmd[0] + " > /dev/null")

		if verifier == 0:
			ct += 1
			if ct == taille - 1:
				continuer = False
			pid = os.fork()
			if pid == 0:
				os.close(tube[0])
				os.execvp(cmd[0], cmd)
				sys.exit(0)
			else:
				pid, status = os.wait()

				if status == 0:
					tabEchec[i] = 1
				else:
					os.close(tube[1])
					litErreur = os.fdopen(tube[0])
					tabEchec[i] = 0
					erreur = litErreur.readline()
					imprimerFichier(fichier, ligne, i, erreur, sys_stdout)
					afficherSommaire(tabEchec, ligne, tailleLigne, sys_stdout)
					return True
		else:
			tabEchec[i] = 0
			erreur = "Erreur, ce programme est introuvable "
			imprimerFichier(fichier, ligne, i, erreur, sys_stdout)
			afficherSommaire(tabEchec, ligne, tailleLigne, sys_stdout)	
			return True

		
	return continuer
##########
###	Methode qui affiche le resultat des commandes
## @rg le tableau pour gerer les success, echec et interruption
## @rg la taille du tableau a cree 
## @rg la ligne de commande en execution 
## @rg l'indice du standard ouput pour l'impression des resultats
##########
def afficherSommaire(tab, ligne, taille, sys_stdout):

	os.dup(sys_stdout)
	print("-----------------------------------"
		+"------------------------------------\n"
		+"Taches echouee")
	if taille == 1:
		print(str(ligne[0])+" : echec")
	else:
		for i in range(taille):
			if tab[i] == 1:
				print(str(ligne[i])+" : success")
			elif tab[i] == 0:
				print(str(ligne[i])+" : echec")
			else:
				print(str(ligne[i])+" : interrompue")
##########
###	Methode qui affiche le resultat des taches completees
## @rg le tableau de booleen pour differencier les taches completees des autres
## @rg la taille du tableau de commandes
##########
def affichageTachesCompleter(taille, tab):
	ctTrue = taille
	for i in range(taille):
		if tab[i] == 'True':
			ctTrue -= 1	
	print("-----------------------------------"
		+"------------------------------------\n"
		+str(ctTrue) + " tache(s) sur " 
		+str(taille)+" on ete completees")
##########
###	Methode qui imprime dans le fichier de sortie les erreurs des commandes en echecs
## @rg le fichier de sortie
## @rg la ligne de commande en execution 
## @rg l'indice de la ligne de commande en execution
## @rg l'erreur produite et a imprimer 
## @rg l'indice du ouput pour generer l'impression dans le dossier
##########
def imprimerFichier(fichier, ligne, i, erreur, sys_stdout):
	os.dup(sys_stdout)
	fichier.write("-----------------------------------"
	+"------------------------------------\n"
	+"Commande avec erreur : {} \n{}".format(ligne[i], erreur))

if __name__ == "__main__":
	main()