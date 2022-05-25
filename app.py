# ---------------------------- LIBRAIRIES -------------------------------
from flask import Flask, render_template, request, make_response
import datetime, pdfkit
from ticketNVCS import Ticket_Main, parcourir_fichier_stat, filtre_mot_cle, filtre_duree_appel, filtre_tentatives


# --------------------------- DECLARATIONS ------------------------------
app = Flask(__name__)
# Aucune idée de l'utilité dans Flask mais pas important de toute façon


affichage_criteres = \
    {
        'physical_name': "NOM DE PO",
        'mission_name':"MISSION",
        'line_interface_name': "",
        'destination_interface_name': "",
        'origin_ia_code': "",
        'origin_number': "NUM ORIGINE",
        'priority': "PRIORITE",
        'destination_ia_code': "",
        'destination_number': "NUM DESTINATION",
        'number_of_retries': "NOMBRE DE RE-TENTATIVES",
        'call_acceptance_delay': "",
        'call_start_date_time': "",
        'call_duration': "DUREE DE L'APPEL",
        'reroute_number': "",
        'end_cause': "END CAUSE",
        'call_type': "",
        'call_type_direction': "DIRECTION DE L'APPEL",
        'call_type_type': "",
        'call_type_conf': "",
        'call_type_transfer': "TRANSFER",
        'call_type_diversion': "",
        'call_type_callfwd': "FORWARD",
        'trunk_group_sip_pool': "",
        'simultaneous_trunk_group_calls': "",
        'simultaneous_transit_calls': "",
        'number_of_ringing_calls': "",
        'transit_counter': "",
        'sip_pool_level': "",
        'destination_name': "",
        'destination_level': ""
    }
# Ce dictionnaire permet de transcrire les parametres en chaine de caracteres pour l'affichage des tickets
# il ne sert à rien d'autre en soit et peut etre remplacé par un fichier de conf

def mise_en_forme_formulaire(dictionnaire):
    #mets en forme l'interval de temps de recherche puis les enleve du formulaire
    date_debut = datetime.datetime.fromisoformat(dictionnaire['date_debut'] + " " + dictionnaire['temps_debut'])
    date_fin = datetime.datetime.fromisoformat(dictionnaire['date_fin'] + " " + dictionnaire['temps_fin'])
    dictionnaire.pop('date_debut')
    dictionnaire.pop('temps_debut')
    dictionnaire.pop('date_fin')
    dictionnaire.pop('temps_fin')
    #enleve les critères vides résiduels du formulaire (c'est une sécurité)
    list_critere_a_enlever = list()
    for a in dictionnaire:
        if dictionnaire[a] == "":
            list_critere_a_enlever.append(a)
    for x in list_critere_a_enlever:
        dictionnaire.pop(x)
    filtrage_tentatives = False
    # regarde si il faut filtrer le nombre de tentative de connexion
    if 'number_of_retries' in dictionnaire:
        filtrage_tentatives = True
        dictionnaire.pop('number_of_retries')
    #gère la duree de l'appel avec un interval de temps puis les enleve du formulaire
    filtrage_duree = False;
    min_second = "0"
    min_minutes = "0"
    min_hour = "0"
    if 'duree_min_m' in dictionnaire or 'duree_min_s' in dictionnaire:
        filtrage_duree = True;
        if 'duree_min_m' in dictionnaire:
            min_minutes = dictionnaire['duree_min_m']
            dictionnaire.pop('duree_min_m')
        if 'duree_min_s' in dictionnaire:
            min_second = dictionnaire['duree_min_s']
            dictionnaire.pop('duree_min_s')
    max_second= "0"
    max_minutes = "0"
    max_hour = "0"
    if 'duree_max_m' in dictionnaire or 'duree_max_s' in dictionnaire:
        filtrage_duree = True;
        if 'duree_max_m' in dictionnaire:
            max_minutes = dictionnaire['duree_max_m']
            dictionnaire.pop('duree_max_m')
        if 'duree_max_s' in dictionnaire:
            max_second = dictionnaire['duree_max_s']
            dictionnaire.pop('duree_max_s')
    else:
        max_hour = "10"
        # on renvoi filtrage_duree qui est vrai si l'utilisateur a rentré une donnée, si il n'y pas de borne superieur
        # alors on cherche les duree inferieur à 10h (c'est large)
    duree_max = datetime.time(hour=int(max_hour),minute=int(max_minutes),second=int(max_second))
    duree_min = datetime.time(minute=int(min_minutes),second=int(min_second))
    return date_debut,date_fin,duree_min,duree_max,filtrage_duree,filtrage_tentatives, dictionnaire
# Cette fonction permet d'extraire à partir du formulaire de recherche différents élements afin de
# pouvoir appeler les différentes fonctions de filtre des tickets
# elle renvoie l'interval de temps de la recherche (date_debut,date_fin), des booleen pour activer
# les filtres autres que le filtre par mot clé (durée d'appel par exemple) ainsi que le formulaire avec seulement
# les mots clés pour le fitlre par mot clé

def conf_to_list(chemin_fichier_conf):
    with open(chemin_fichier_conf, "r") as fic:
        conf_brut = fic.readlines()
        conf = list()
        for ligne in conf_brut:
            ligne = ligne.strip('\n')
            conf.append(ligne)
    return conf
# Cette fonction exploite les fichiers de config du formulaire pour les utiliser dans les pages HTML


# ------------------------------ APPLICATION -----------------------------------------------------

@app.route("/")
def index():
    # mettre ici les imports de fichier et les initialisations
    return render_template("base.html")
# renvoi vers base.html qui est la page de sélection du système/categorie (MAIN BACKUP / RADIO TELEPHONE)

@app.route("/set-form", methods=['get','post'])
def set_form():
    if request.method == "POST":
        systeme = request.form['systeme']
        categorie = request.form['category']
        if systeme == "MAIN":
            if categorie == "TELEPHONE":
                missions = conf_to_list("conf/MISSION.txt")
                PO = conf_to_list("conf/PO.txt")
                return render_template("form_main_tel.html",listeMissions = missions, listePO = PO, date_ajd=datetime.date.today())
            else:
                return render_template("form_main_radio")
        else:
            if categorie == "TELEPHONE":
                return render_template("form_backup_tel.html")
            else:
                return render_template("form_backup_radio")
# Après choix du système on renvoi vers un formulaire pour filtrer les tickets de communications
# Ce formulaire dépend du choix dans base.html

@app.route("/recherche-main-tel", methods=['get','post'])
def recherche_Main_Tel():
    if request.method == "POST":
        liste_ticket = list()
        search_form = request.form.to_dict()
        date_debut, date_fin, duree_min, duree_max, filtrage_duree, filtrage_tentatives, search_form = mise_en_forme_formulaire(search_form)
        valide, liste_ticket = parcourir_fichier_stat(date_debut, date_fin, "TELEPHONE")
        if valide and search_form:
            # on a retirer tout les attribut qui ne sont pas des mots clé dans le dictionnaire
            valide, liste_ticket = filtre_mot_cle(liste_ticket,**search_form)
        if valide and filtrage_duree:
            # on filtre le reste avec des fonctions à part
            valide, liste_ticket = filtre_duree_appel(liste_ticket, duree_min, duree_max)
            search_form['call_duration']="AFF DUREE APPEL"
        if valide and filtrage_tentatives:
            valide, liste_ticket = filtre_tentatives(liste_ticket)
            # on ajoute cette mention au dictionnaire pour que le HTML le considere comme un parametre de recherche
            # afin d'afficher en vert et dans le bandeau retrécie du ticket la valeur de re-tentative, meme chose pour
            # la call duration plus haut
            search_form['number_of_retries']="AFF NB RETRIES"
        if valide:
            pdf_render = render_template("/recherche_pdf.html",tickets=liste_ticket,systeme="MAIN",category="TELEPHONE",date=datetime.datetime.now(),len=len)
            return render_template("/recherche-main-tel.html",tickets=liste_ticket,criteres=search_form,aff_critere=affichage_criteres,getattr=getattr,len=len,listeMissions = conf_to_list("conf/MISSION.txt"), listePO = conf_to_list("conf/PO.txt"),pdf = pdf_render)
        else:
            return render_template("/recherche_vide.html")
# Après choix des critères la recherche est effectuée et le filtrage est fait grace aux fonctions
# et aux classes disponibles dans TicketNVCS.py

@app.route("/ticket.pdf", methods=['get','post'])
def pdf():
    if request.method == 'POST':
        pdf = pdfkit.from_string(request.form['pdf'], False)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=ticketsNVCS'+str(datetime.datetime.now())+'.pdf'
        return response
# Cette route permet d'enregistrer la recherche au format PDF