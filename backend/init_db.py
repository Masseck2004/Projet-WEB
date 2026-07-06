import os
import sqlite3
from datetime import date
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "ufr_sta.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")


def init_db():
    # On repart d'une base vierge pour eviter les doublons
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    cur = conn.cursor()

    # Compte administrateur
    cur.execute(
        "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
        ("admin", generate_password_hash("admin123")),
    )

    # Departements
    departements = [
        (
            "Informatique",
            "Le département Informatique forme des étudiants aux métiers du "
            "développement logiciel, des réseaux, de la Data et de la "
            "cybersécurite.",
            "Dr Amadou Dahirou GUEYE",
            "dahirou.gueye@uam.edu.sn"
        ),
        (
            "Mathématiques",
            "Le département Mathématiques propose des formations solides en "
            "mathématiques fondamentales et appliquées, statistiques et "
            "modélisation.",
            "Dr Thierno Mohamadane Mansour SOW",
            "thierno.sow@uam.edu.sn"
        ),
        (
            "Physique",
            "Le département Physique forme des étudiants en physique "
            "fondamentale, énergie et instrumentation.",
            "Dr Makha NDAO",
            "makha.ndao@uam.edu.sn"
        ),
    ]
    cur.executemany(
        "INSERT INTO departements (nom, description, responsable, contact) "
        "VALUES (?, ?, ?, ?)",
        departements,
    )

    # id des departements (1 = Informatique, 2 = Mathematiques, 3 = Physique)
    dep_info, dep_math, dep_phys = 1, 2, 3

    # Formations
    formations = [
        (
            dep_info,
            "Licence Informatique",
            "Licence (L1-L3)",
            "3 ans",
            "Baccalauréat scientifique ou technique",
            "Développeur Web/Mobile, administrateur Système/Réseau, "
            "Poursuite en Master.",
        ),
        (
            dep_info,
            "Master Informatique",
            "Master (M1-M2)",
            "2 ans",
            "Licence en Informatique ou équivalent",
            "Ingénieur logiciel, Chef de projet IT, Chercheur, "
            "Data scientist.",
        ),
        (
            dep_math,
            "Licence Mathématiques",
            "Licence (L1-L3)",
            "3 ans",
            "Baccalauréat scientifique",
            "Enseignement, Statistique, Poursuite en Master.",
        ),
        (
            dep_math,
            "Master Mathématiques",
            "Master (M1-M2)",
            "2 ans",
            "Licence en Mathématiques ou équivalent",
            "Chercheur, Enseignant-chercheur, Data Analyst.",
        ),
        (
            dep_phys,
            "Licence Physique",
            "Licence (L1-L3)",
            "3 ans",
            "Baccalauréat scientifique",
            "Enseignement, Métrologie, Poursuite en Master.",
        ),
        (
            dep_phys,
            "Master Physique",
            "Master (M1-M2)",
            "2 ans",
            "Licence en Physique ou équivalent",
            "Recherche, Energie, instrumentation industrielle.",
        ),
    ]
    cur.executemany(
        "INSERT INTO formations "
        "(departement_id, nom, niveau, duree, conditions_admission, debouches) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        formations,
    )

    # Programme detaille 
    programme_licence_info = [
        (1, 1, "Algorithmique et Programmation"),
        (1, 1, "Logique combinatoire "),
        (1, 1, "Mathématiques 1"),
        (1, 1, "Anglais 1"),
        (1, 1, "Histoire des sciences 1"),
        (1, 1, "Français"),
        (1, 1, "Physique 1"),
        (1, 2, "Architecture des ordinateurs"),
        (1, 2, "Langage C"),
        (1, 2, "Mathématiques 2"),
        (1, 2, "Anglais 2"),
        (1, 2, "Histoire des sciences 2"),
        (1, 2, "Matlab"),
        (1, 2, "Physique 2"),
        (1, 3, "Base de données (PostgreSQL)"),
        (1, 3, "Programmation Objet (Python)"),
        (1, 3, "Mathématiques 3"),
        (1, 3, "Physique 3"),
        (1, 3, "Anglais 3"),
        (1, 3, "Initialisation au logiciel R"),
        (1, 3, "Pré-Spécialisation (Introduction à la Cybersécurité, Data-Science, Modélisation, Sciences des Matériaux)"),
        (1, 4, "Algorithme avancé"),
        (1, 4, "Introduction à la Data-Science"),
        (1, 4, "Systéme d'exploitation"),
        (1, 4, "Mathématiques 4"),
        (1, 4, "Physique 4"),
        (1, 4, "Analyse du Signal"),
        (1, 4, "Anglais 4"),
        (1, 4, "Projet Personnel"),
        (1, 5, "Data Science"),
        (1, 5, "Génie Logiciel"),
        (1, 5, "UML"),
        (1, 5, "Introduction aux Réseaux"),
        (1, 5, "Internet des Objets (IOT)"),
        (1, 5, "Java Avancé"),
        (1, 5, "Programmation WEB (HTML5, CSS3)"),
        (1, 5, "Analyse de données"),
        (1, 5, "Recherche Opérationnelle (RO)"),
        (1, 5, "Anglais technique"),
        (1, 5, "Technique de Rédaction Scientifique"),
        (1, 5, "Leadership et Développement Personnel")
    ]
    programme_licence_math = [
        (3, 1, "Analyse 1"),
        (3, 1, "Algèbre 1"),
        (3, 1, "Statistique descriptive"),
        (3, 1, "Physique 1"),
        (3, 1, "Informatique 1"),
        (3, 1, "Anglais 1"),
        (3, 1, "Histoire des sciences 1"),
        (3, 1, "Français"),
        (3, 2, "Analyse 2"),
        (3, 2, "Algèbre 2"),
        (3, 2, "Calcul Numérique 1"),
        (3, 2, "Physique 2"),
        (3, 2, "Informatique 2"),
        (3, 2, "Anglais 2"),
        (3, 2, "Histoire des sciences 2"),
        (3, 2, "Matlab"),
        (3, 3, "Analyse 3"),
        (3, 3, "Algèbre 3"),
        (3, 3, "Analyse Numérique matricielle"),
        (3, 3, "Informatique 3"),
        (3, 3, "Physique 3"),
        (3, 3, "Anglais 3"),
        (3, 3, "Initialisation au logiciel R"),
        (3, 3, "Pré-Spécialisation (Introduction à la Cybersécurité, Data-Science, Modélisation, Sciences des Matériaux)"),
        (3, 4, "Analyse 4"),
        (3, 4, "Algèbre 4"),
        (3, 4, "Probabilité"),
        (3, 4, "Informatique 4"),
        (3, 4, "Physique 4"),
        (3, 4, "Analyse du Signal"),
        (3, 4, "Anglais 4"),
        (3, 4, "Projet Personnel"),
        (3, 5, "Statistique inférentielle"),
        (3, 5, "Analyse 5"),
        (3, 5, "Variables complexes"),
        (3, 5, "Mesure et intégration"),
        (3, 5, "Optimisation linéaire"),
        (3, 5, "Initiation aux Solveurs"),
        (3, 5, "Informatique 5"),
        (3, 5, "Anglais technique"),
        (3, 5, "Leadership et Développement Personnel"),
        (3, 5, "Technique de Rédaction Scientifique")
    ]
    programme_licence_phys = [
        (5, 1, "Electricité"),
        (5, 1, "Mécanique du point"),
        (5, 1, "Anglais 1"),
        (5, 1, "Histoire des sciences 1"),
        (5, 1, "Français"),
        (5, 1, "Mathématiques 1"),
        (5, 1, "Informatique 1"),
        (5, 2, "Magnétostatique & Régimes Variables"),
        (5, 2, "Optique Géométrique"),
        (5, 2, "Mathématiques 2"),
        (5, 2, "Informatique 2"),
        (5, 2, "Anglais 2"),
        (5, 2, "Histoire des sciences 2"),
        (5, 2, "Matlab"),
        (5, 3, "Mécanique Générale"),
        (5, 3, "Thermodynamique"),
        (5, 3, "Informatique 3"),
        (5, 3, "Mathématiques 3"),
        (5, 3, "Anglais 3"),
        (5, 3, "Initialisation au logiciel R"),
        (5, 3, "Pré-Spécialisation (Introduction à la Cybersécurité, Data-Science, Modélisation, Sciences des Matériaux)"),
        (5, 4, "Mécanique quantique"),
        (5, 4, "Relativité restreinte"),
        (5, 4, "Informatique 4"),
        (5, 4, "Mathématiques 4"),
        (5, 4, "Analyse du Signal"),
        (5, 4, "Anglais 4"),
        (5, 4, "Projet Personnel"),
        (5, 5, "Mécanqiue Analytique"),
        (5, 5, "Physique statistique"),
        (5, 5, "Thermodynamique et propriétés de la matiére"),
        (5, 5, "Mathématiques 5"),
        (5, 5, "Atomistique et liaisons chimiques"),
        (5, 5, "Thermochimie et équilibre chimique"),
        (5, 5, "Electromagnétisme"),
        (5, 5, "Physique Quantique 1"),
        (5, 5, "Anglais technique"),
        (5, 5, "Leadership et Développement Personnel"),
        (5, 5, "Technique de Rédaction Scientifique")
    ]
    cur.executemany(
        "INSERT INTO programme_modules (formation_id, semestre, nom_module) "
        "VALUES (?, ?, ?)",
        programme_licence_info
        + programme_licence_math
        + programme_licence_phys,
    )

    # Actualites
    actualites = [
        (
            "Recrutement - Enseignant(e)s-chercheur(e)s",
            "2026-06-10",
            "L’UFR STA lance un appel à candidatures pour le recrutement d’enseignant(e)s-chercheur(e)s" 
            "afin de renforcer son équipe pédagogique et de soutenir le développement de la recherche "
            "scientifique. Les candidats intéressés sont invités à consulter les conditions de candidature" 
            "et à soumettre leur dossier avant le 30 Juillet 2026.",
            "uam.jpeg",
            "appel",
        ),
        (
            "Formation des étudiants primo-entrants en civisme et citoyenneté",
            "2024-03-24",
            "Une formation destinée aux étudiants primo-entrants s’est tenue le 24 mars 2024"
            " à l’amphithéâtre Macky Sall. Cette activité visait à sensibiliser les nouveaux"
            " étudiants aux valeurs du civisme, de la citoyenneté et de la responsabilité, afin" 
            "de favoriser leur intégration et leur engagement au sein de la communauté universitaire.",
            "civisme.jpeg",
            "formation",
        ),
        (
            "Conférence : Les mathématiques au service de la société",
            "2026-05-15",
            "Une conférence intitulée « Les mathématiques au service de la société » "
            "a été organisée afin de mettre en lumière l’importance des mathématiques dans" 
            "la résolution des problèmes contemporains. Elle a permis de montrer leurs applications" 
            "dans des domaines variés tels que la santé, l’économie, les technologies et l’environnement.",
            "conference-math.jpeg",
            "conference",
        ),
    ]
    cur.executemany(
        "INSERT INTO actualites (titre, date_publication, description, photo, categorie) "
        "VALUES (?, ?, ?, ?, ?)",
        actualites,
    )

    # Activites (module principal du projet)
    cur.execute(
        "INSERT INTO activites "
        "(titre, date_activite, lieu, organisateur, description, type_activite) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            "Formation en Data Science",
            "2026-03-15",
            "ODC",
            "Membres de l'ODC",
            "En mars 2025, une formation certifiante en Data Science a été organisée par l’ODC de l’UAM." 
            "Cette formation a permis aux participants d’acquérir des compétences fondamentales en analyse de données," 
            "en visualisation et en apprentissage automatique, à travers des séances théoriques et des travaux pratiques "
            "encadrés par des formateurs spécialisés.",
            "atelier",
        ),
    )
    activite_id = cur.lastrowid
    cur.executemany(
        "INSERT INTO activite_photos (activite_id, filename) VALUES (?, ?)",
        [(activite_id, "odc.jpeg")],
    )

    cur.execute(
        "INSERT INTO activites "
        "(titre, date_activite, lieu, organisateur, description, type_activite) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            "Visite académique et échange scientifique à AIMS Sénégal",
            "2026-05-09",
            "AIMS (Mbour)",
            "UFR STA",
            "Dans le cadre du programme « Initiation à la modélisation mathématique », les étudiants de Licence 3 "
            "Mathématiques et Modélisation de l’UFR STA – Université Amadou Mahtar Mbow de Dakar (UAM) effectueront une" 
            "visite académique à l’Institut Africain des Sciences Mathématiques (AIMS) – Sénégal, le samedi 09 mai 2026 à partir de 16h."
            "Cet événement vise à renforcer les liens entre l’université et l’un des centres d’excellence en mathématiques en Afrique, à "
            "travers des échanges scientifiques, des présentations de travaux de modélisation et des discussions sur les enjeux de la recherche" 
            "et de l’innovation. Les participants auront l’occasion de découvrir les infrastructures d’AIMS, d’interagir avec des chercheurs et de" 
            "partager leurs expériences autour de la thématique « Ensemble pour l’excellence, l’innovation et le développement durable »."
            "La rencontre se tiendra à AIMS – Sénégal, situé route de Joal (Centre IRD), BP 1418 Mbour-Thiès, et rassemblera étudiants et "
            "encadrants autour d’un programme alliant rigueur académique, collaborations interdisciplinaires et ouverture sur les défis scientifiques actuels.",
            "Evénement",
        ),
    )
    activite_id_2 = cur.lastrowid
    cur.executemany(
        "INSERT INTO activite_photos (activite_id, filename) VALUES (?, ?)",
        [(activite_id_2, "aims1.jpeg"), (activite_id_2, "aims2.jpeg"),
         (activite_id_2, "aims3.jpeg"), (activite_id_2, "aims4.jpeg")],
    )

    # Galerie photos / albums
    cur.execute(
        "INSERT INTO albums (titre, description, date_album) VALUES (?, ?, ?)",
        ("Journée d'excellence de l'UFR STA 2026", "La Journée d’excellence de l’UFR STA est un" 
        "événement culturel et académique qui met en valeur l’UFR à travers la présentation de ses "
        "activités, de ses formations et des projets innovants réalisés par les étudiants. Cette journée"
        " est également marquée par la récompense des meilleurs élèves en reconnaissance de leurs performances"
        " académiques. Elle se déroule dans une ambiance conviviale et culturelle, en présence des enseignants"
        " et du personnel pédagogique, favorisant ainsi les échanges entre étudiants et encadrants.", "2026-05-09"),
    )
    album_id = cur.lastrowid
    cur.executemany(
        "INSERT INTO album_photos (album_id, filename) VALUES (?, ?)",
        [(album_id, "culturelle1.jpeg"), (album_id, "culturelle2.jpeg"),
         (album_id, "culturelle3.jpeg"), (album_id, "culturelle4.jpeg"),
         (album_id, "culturelle5.jpeg"), (album_id, "culturelle6.jpeg"),
         (album_id, "culturelle7.jpeg"), (album_id, "culturelle8.jpeg"),
         (album_id, "culturelle9.jpeg"), (album_id, "culturelle10.jpeg"),
         (album_id, "culturelle11.jpeg"), (album_id, "culturelle12.jpeg")],
    )

    cur.execute(
        "INSERT INTO albums (titre, description, date_album) VALUES (?, ?, ?)",
        ("Inauguration de l'UNIPOD", "À travers l’Agenda national de transformation " 
        "« Sénégal 2050 », le pays ambitionne de devenir « une société numérique et un hub"
        " de services à forte valeur ajoutée », conformément à sa stratégie digitale intitulée "
        "« New Deal Technologique ».Pour accompagner cette vision, le PNUD Sénégal a lancé l’initiative"
        " Timbuktoo, destinée à encourager et promouvoir un entrepreneuriat innovant, évolutif et à fort "
        "impact porté par les jeunes Sénégalais. Cette dynamique se matérialise par la création du Pôle"
        " Universitaire. d’Innovation et de Technologie (UNIPOD) de Diamniadio.", "2026-04-27"),
    )
    album_id_2 = cur.lastrowid
    cur.executemany(
        "INSERT INTO album_photos (album_id, filename) VALUES (?, ?)",
        [(album_id_2, "unipod1.jpeg"), (album_id_2, "unipod2.jpeg"),
         (album_id_2, "unipod3.jpeg"), (album_id_2, "unipod4.jpeg"),
         (album_id_2, "unipod5.jpeg"), (album_id_2, "unipod6.jpeg"),
         (album_id_2, "unipod7.jpeg"), (album_id_2, "unipod8.jpeg")],
    )

    cur.execute(
        "INSERT INTO albums (titre, description, date_album) VALUES (?, ?, ?)",
        ("Présentation des projets IOT", "Les étudiants de Licence 3 de l’UFR STA présentent leurs projets" 
        " en Internet des objets (IoT), conçus dans le cadre de leur formation. Cette activité met en avant" 
        " leur créativité, leurs compétences techniques et leur capacité à développer des solutions innovantes" 
        " répondant à des besoins concrets. Elle constitue également un moment d’échange entre les étudiants, les"
        " enseignants et les visiteurs autour des technologies de l’IoT et de leurs applications.", "2026-05-21"),
    )
    album_id_3 = cur.lastrowid
    cur.executemany(
        "INSERT INTO album_photos (album_id, filename) VALUES (?, ?)",
        [(album_id_3, "iot1.jpeg"), (album_id_3, "iot2.jpeg"),
         (album_id_3, "iot3.jpeg"), (album_id_3, "iot4.jpeg"),
         (album_id_3, "iot5.jpeg"), (album_id_3, "iot6.jpeg"),
         (album_id_3, "iot7.jpeg"), (album_id_3, "iot8.jpeg")],
    )

    # Enseignants
    enseignants = [
        ("Dr Amadou Dahirou GUEYE", "Professeur Titulaire", dep_info, "dahirou.gueye@uam.edu.sn", "Télé-enseignement, IA appliquée à la santé et à la sécurité routière", "Dahirou.jpeg"),
        ("Dr Sada ANNE", "Docteur", dep_info, "sada.anne@uam.edu.sn", "Informatique / IA, spécialisé en imagerie médicale et détection de maladies (notamment AVC et cancer)", "Anne.jpeg"),
        ("Dr Lamine YADE", "Docteur", dep_info, "lamine.yade@uam.edu.sn", "Informatique (TIC), spécialisé en IoT, cloud computing, laboratoires distants, virtualisation et technologies éducatives", "Yade.jpeg"),
        ("Dr Alioune COULIBALY", "Maitre de Conférences Titulaire", dep_math, "alioune.coulibaly@uam.edu.sn", "Equations aux dérivées partielles, Analyse fonctionnelle, Probabilité-Statistique", "Coulibaly.jpeg"),
        ("Dr Thierno Mohamadane Mansour SOW", "Maitre de Conférences Titulaire", dep_math, "thierno.sow@uam.edu.sn", "Analyse non linéaire, Optimisation, Calcul des variations", "Sow.jpeg"),
        ("Dr Makha NDAO", "Maitre de Conférences Titulaire", dep_phys, "makha.ndao@uam.edu.sn", "Biomasse et stockage d'énergie, Polymères et élastomères", "Makha.jpeg"),
        ("Pr Issa SAKHO", "Professeur assimilé", dep_phys, "issa.sakho@uam.edu.sn", "Dynamique physique des systèmes sédimentaires littoraux, Risques littoraux", "Sakho.jpeg"),
        ("Dr Siny NDOYE", "Maitre de Conférences Titulaire", dep_phys, "siny.ndoye@uam.edu.sn", "Dynamique océanique, Upwelling côtier, Pollution marine", "Ndoye.jpeg"),
    ]
    cur.executemany(
        "INSERT INTO enseignants (nom, grade, departement_id, email, domaines_recherche, photo) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        enseignants,
    )

    conn.commit()
    conn.close()
    print(f"Base de données initialisée avec succés : {DB_PATH}")
    print("Compte administrateur crée -> identifiant : admin / mot de passe : admin123")
    print("Pensez a changer ce mot de passe avant toute mise en production.")


if __name__ == "__main__":
    init_db()
