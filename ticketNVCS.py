# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# ---------------------------- LIBRAIRIES -------------------------------
import datetime, os, re

# --------------------------- DECLARATIONS ------------------------------
class Ticket_Main:
    def __init__(self):
        self.date_time = None
        self.category = None
        self.physical_name = None
        self.mission_name = None
        self.line_interface_name = None
        self.destination_interface_name = None
        self.origin_ia_code = None
        self.origin_number = None
        self.priority = None
        self.destination_ia_code = None
        self.destination_number = None
        self.number_of_retries = None
        self.call_acceptance_delay = None
        self.call_start_date_time = None
        self.call_duration = None
        self.reroute_number = None
        self.end_cause = None
        self.call_type = None
        self.call_type_direction = None
        self.call_type_type = None
        self.call_type_conf = None
        self.call_type_transfer = None
        self.call_type_diversion = None
        self.call_type_callfwd = None
        self.trunk_group_sip_pool = None
        self.simultaneous_trunk_group_calls = None
        self.simultaneous_transit_calls = None
        self.number_of_ringing_calls = None
        self.transit_counter = None
        self.sip_pool_level = None
        self.destination_name = None
        self.destination_level = None
    # les differents segments de la ligne du fichier stat forment les attributs d'un objet ticket de communication
    # cette fontion permet d'initialiser un ticket vierge

    def __init__(self, ligne_de_comm):
        [self.date_time,
         self.category,
         self.physical_name,
         self.mission_name,
         self.line_interface_name,
         self.destination_interface_name,
         self.origin_ia_code,
         self.origin_number,
         self.priority,
         self.destination_ia_code,
         self.destination_number,
         self.number_of_retries,
         self.call_acceptance_delay,
         self.call_start_date_time,
         self.call_duration,
         self.reroute_number,
         self.end_cause,
         self.call_type,
         self.trunk_group_sip_pool,
         self.simultaneous_trunk_group_calls,
         self.simultaneous_transit_calls,
         self.number_of_ringing_calls,
         self.transit_counter,
         self.sip_pool_level,
         self.destination_name,
         self.destination_level,
         null] = ligne_de_comm.split(";")
        # separe les differents attributs du call type en sous attributs
        [self.call_type_direction,
         self.call_type_type,
         self.call_type_conf,
         self.call_type_transfer,
         self.call_type_diversion,
         self.call_type_callfwd] = self.call_type.split(",")
    # Cette fonction permet d'extraire les attributs d'une ligne d'un fichier Stat pour les mettre dans le
    # ticket de communication instancié lors de l'initialisation

    def to_string(self):
        return (self.date_time + " " +
              self.category + " " +
              self.physical_name + " " +
              self.mission_name + " " +
              self.line_interface_name + " " +
              self.destination_interface_name + " " +
              self.origin_ia_code + " " +
              self.origin_number + " " +
              self.priority + " " +
              self.destination_ia_code + " " +
              self.destination_number + " " +
              self.number_of_retries + " " +
              self.call_acceptance_delay + " " +
              self.call_start_date_time + " " +
              self.call_duration + " " +
              self.reroute_number + " " +
              self.end_cause + " " +
              self.call_type + " " +
              self.trunk_group_sip_pool + " " +
              self.simultaneous_trunk_group_calls + " " +
              self.simultaneous_transit_calls + " " +
              self.number_of_ringing_calls + " " +
              self.transit_counter + " " +
              self.sip_pool_level + " " +
              self.destination_name + " " +
              self.destination_level)
    # renvoi la composition brut du ticket de comm sous forme de str

    def get_date_time(self):
        date_format = datetime.datetime.fromisoformat(self.date_time)
        return date_format
    # Prend l'attribut date_time de l'objet au format str et le renvoi au format horaire standard de python datetime
    # qui permet de faire des opérations sur des donéees horaires
# Classe permettant l'interpretation d'un ticket de communication qui à l'origine est sous forme d'une
# ligne d'attributs séparée par des ' ; '

def trouve_comm_main(iteration_recherchee, nom_fichier_avec_chemin_et_extension):
    validation = False
    liste_comm = list()
    # on ouvre le fichier txt avec les comm brutes dedans
    if os.path.isfile(nom_fichier_avec_chemin_et_extension):
        with open(nom_fichier_avec_chemin_et_extension, "r") as fichier:
            # on extrait toutes les lignes de ce fichier
            fichier_image = fichier.readlines()
            # on transforme chaque ligne possedant l'iteration recherchee en objet Ticket_Main qu'on met en liste
            for ligne in fichier_image:
                if iteration_recherchee in ligne:
                    # on vérifie si la dernière ligne est conforme (au cas où le fichier aurait été pris en pleine ecriture)
                    if ligne == fichier_image[-1]:
                        if re.match('.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;',ligne):
                            ticket = Ticket_Main(ligne)
                            liste_comm.append(ticket)
                            validation = True
                    else:
                        ticket = Ticket_Main(ligne)
                        liste_comm.append(ticket)
                        validation = True
        # on renvoi la liste des comm ainsi crée
    return validation, liste_comm
# Fonction qui permet de trouver les lignes de comm dans un fichier contenant une iteration specifique
# elle retourne une liste d'objets de type Ticket_Main et un booleen qui est vrai si la fonction a trouvé
# ce qu'elle cherchait dans le fichier (Main pour NVCS Main)
# en mettant TELEPHONE comme iteration on retrouve alors toutes les communications telephone du Main

def filtre_temps(debut_interval, fin_interval, liste_comm):
    liste_comm_interval = list()
    trouve = False
    # on verifie si chaque comm est dans l'interval de temps donné
    for comm in liste_comm:
        if debut_interval < comm.get_date_time() < fin_interval:
            #quand un ticket est trouvé on l'ajoute et trouve = True pour annoncer qu'au moins 1 ticket a été trouvé
            liste_comm_interval.append(comm)
            trouve = True
    # on retourne la liste filtree sans les comm qui sont hors de l'interval
    return trouve, liste_comm_interval
# fonction qui enlève de la liste les comm qui ne sont pas compris dans l'interval de temps donné
# debut et fin interval doivent être donnés au format classique python datetime
# le filtre prends en compte l'heure et non

def nom_stat_date(date):
    #date sous forme "YYYY-MM-DD HH:MM:SS"
    date_intermediaire = str(date)
    date_intermediaire,null = date_intermediaire.split(" ")
    # on a enlevé la partie horaire
    annee,mois,jour = date_intermediaire.split("-")
    nom_fichier = "Stat"+annee+mois+jour+".txt"
    # nom de fichier sous la forme StatYYYYMMDD.txt
    return nom_fichier
# renvoi le nom formaliser d'un fichier stat en fonction de sa date

def parcourir_fichier_stat(date_debut, date_fin, iteration_recherchee):
    # si par mégarde les variable de l'interval sont inversée à l'appel de la fonction
    if date_debut > date_fin:
        date_echange = date_fin
        date_fin = date_debut
        date_debut = date_echange
    # date_cpt va s'incrementer de la date de début à la date de fin de maniere a chercher dans chaque
    # fichier journalier dans l'interval
    date_cpt = date_debut
    trouve = False
    # un_jour correpond à un delta temporel de 1 jour, date + un_jour == le lendemain meme heure
    un_jour = datetime.timedelta(days=1)
    liste_comm_fichier = list()
    liste_comm_totale = list()
    #on met la date de fin à 23h59,59s,999us pour faire en sorte que si date_cpt et date_fin sont au meme jour
    # alors date_cpt < date_fin dans tous les cas
    date_fin_cpt = date_fin.replace(hour=23,minute=59,second=59,microsecond=999)
    while(date_cpt < date_fin_cpt):
        # nom du fichier sous forme StatYYYYMMDD.txt dans le repertoire /Stat
        nom_fichier = "Stat/"+nom_stat_date(date_cpt)
        #recherche dans le fichier specifié
        comm_trouve, liste_comm_fichier = trouve_comm_main(iteration_recherchee,nom_fichier)
        if comm_trouve:
            # si des comm ont été trouvé dans le fichier actuel on les ajoute dans la liste totale et on annonce
            # qu'on a trouvé au moins un ticket via cette fonction avec trouve = True
            liste_comm_totale = liste_comm_totale + liste_comm_fichier
            trouve = True
        # on incremente la date pour chercher dans le fichier du jour d'apres
        date_cpt = date_cpt + un_jour
    # on filtre maintenant en fonction de l'heure, on avait deja filtre en fonction de la date
    if trouve:
        trouve, liste_comm_totale = filtre_temps(date_debut,date_fin,liste_comm_totale)
    return trouve, liste_comm_totale
# fonction qui renvoi une liste des ticket de comm comprenant une iteration recherchee
# et qui se trouve dans l'interval de temps donné, cette fonction ouvre plusieurs fichier
# de stat pour son bon fonctionnement

def filtre_duree_appel(liste_comm,duree_min, duree_max):
    liste_comm_filtree = list()
    trouve = False
    # si par megarde l'utilisateur a rentré max < min alors on les inverse
    if duree_min > duree_max:
        a = duree_max
        duree_max = duree_min
        duree_min = a
    # on verifie pour chaque ticket si il est compris dans l'interval de temps
    for comm in liste_comm:
        if duree_min < datetime.time.fromisoformat(comm.call_duration) < duree_max:
            # si oui on l'ajoute et on dit qu'on a trouvé au moins 1 ticket avec trouve = True
            liste_comm_filtree.append(comm)
            trouve = True
            print(comm.call_duration)
    return trouve, liste_comm_filtree
# Cette fontion permet de filtrer la liste de comm en entrée en fonction de l'interval de temps duree_min et duree max
# cette fonction renvoi la liste de comm en enlevant les tickets qui ne correspondent pas

def filtre_tentatives(liste_comm):
    liste_comm_filtree = list()
    trouve = False
    for comm in liste_comm:
        print(comm.to_string())
        if int(comm.number_of_retries) > 0:
            liste_comm_filtree.append(comm)
            trouve = True;
    return trouve, liste_comm_filtree
# Cette fontion permet de filtrer la liste de comm en fonction du nombre de re-tentatives de connexion
# elle ne peut pas être filtrer en mot clé car il faut number_of_retries > 0 et non = "0"

def filtre_mot_cle(liste_comm,**mot_cle_attribut):
    liste_comm_finale = list()
    liste_comm_finale = liste_comm
    liste_comm_filtree = list()
    trouve = False
    for attribut, mot in mot_cle_attribut.items():
        # pour chaque parametre variable (kwargs) on fait un filtrage
        for comm in liste_comm_finale:
            # on teste chaque comm de la liste avec getattr qui trouve un attribut d'une classe correspondant à une chaine
            if getattr(comm,attribut) == mot:
                # si le ticket est valide pour l'attribut en cours alors on l'ajoute à la liste temporaire
                # au dernier attribut teste si on trouve au moins 1 ticket qui rassemble tous les critere alors on
                # annonce qu'au moins un ticket a été trouvé avec trouve = True
                trouve = True
                liste_comm_filtree.append(comm)
        #on vide les listes pour avoir seulement le produit du dernier filtrage enregistré et pouvoir faire le prochain
        liste_comm_finale = []
        liste_comm_finale = liste_comm_filtree
        liste_comm_filtree = []
    return trouve, liste_comm_finale
# Cette fonction permet de filtrer la liste de comm en entrée en fonction des parametres variable selectionnés
# les mot_cle_attribut correspondent à des attribut de la classe Ticket_Comm, par exemple si on appelle
# filtre_mot_cle(liste_comm,end_cause = "END_BY_EXTERNAL_USER", physical_name = "PHIP_RENAR_1") alors
# on aura en retour la liste des comm qui correspondent à ces critères et qui sont dans liste_comm

