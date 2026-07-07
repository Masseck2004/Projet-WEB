-- Schema de la base de donnees du site vitrine de l'UFR STA

PRAGMA foreign_keys = ON;

-- Comptes administrateurs (back-office)
CREATE TABLE IF NOT EXISTS admin_users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

-- Departements
CREATE TABLE IF NOT EXISTS departements (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nom          TEXT NOT NULL,
    description  TEXT,
    responsable  TEXT,
    contact      TEXT
);

-- Formations (rattachees a un departement)
CREATE TABLE IF NOT EXISTS formations (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    departement_id        INTEGER NOT NULL,
    nom                   TEXT NOT NULL,
    niveau                TEXT,
    duree                 TEXT,
    conditions_admission  TEXT,
    debouches             TEXT,
    FOREIGN KEY (departement_id) REFERENCES departements (id) ON DELETE CASCADE
);

-- Programme detaille : un module rattache a un semestre d'une formation
CREATE TABLE IF NOT EXISTS programme_modules (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    formation_id  INTEGER NOT NULL,
    semestre      INTEGER NOT NULL,
    nom_module    TEXT NOT NULL,
    FOREIGN KEY (formation_id) REFERENCES formations (id) ON DELETE CASCADE
);

-- Actualites (seminaires, conferences, soutenances, appels, resultats)
CREATE TABLE IF NOT EXISTS actualites (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    titre             TEXT NOT NULL,
    date_publication  TEXT NOT NULL,
    description       TEXT,
    photo             TEXT,
    categorie         TEXT DEFAULT 'actualite'
);

-- Activites (journal des activites - module principal)
CREATE TABLE IF NOT EXISTS activites (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    titre          TEXT NOT NULL,
    date_activite  TEXT NOT NULL,
    lieu           TEXT,
    organisateur   TEXT,
    description    TEXT,
    type_activite  TEXT DEFAULT 'activite'
);

CREATE TABLE IF NOT EXISTS activite_photos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    activite_id   INTEGER NOT NULL,
    filename      TEXT NOT NULL,
    FOREIGN KEY (activite_id) REFERENCES activites (id) ON DELETE CASCADE
);

-- Galerie photos organisee par albums
CREATE TABLE IF NOT EXISTS albums (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    titre        TEXT NOT NULL,
    description  TEXT,
    date_album   TEXT
);

CREATE TABLE IF NOT EXISTS album_photos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id   INTEGER NOT NULL,
    filename   TEXT NOT NULL,
    FOREIGN KEY (album_id) REFERENCES albums (id) ON DELETE CASCADE
);

-- Enseignants
CREATE TABLE IF NOT EXISTS enseignants (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    nom                  TEXT NOT NULL,
    grade                TEXT,
    departement_id       INTEGER,
    email                TEXT,
    domaines_recherche   TEXT,
    photo                TEXT,
    FOREIGN KEY (departement_id) REFERENCES departements (id) ON DELETE SET NULL
);

-- Messages recus via le formulaire de contact
CREATE TABLE IF NOT EXISTS messages_contact (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nom        TEXT NOT NULL,
    email      TEXT NOT NULL,
    sujet      TEXT,
    message    TEXT NOT NULL,
    date_envoi TEXT NOT NULL,
    lu         INTEGER DEFAULT 0
);
