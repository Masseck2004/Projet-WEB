import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    g,
    abort,
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "change-moi-avant-la-mise-en-production"
)
app.config["DATABASE"] = os.path.join(BASE_DIR, "database", "ufr_sta.db")
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "images", "uploads")
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 Mo max par fichier

# Gestion de la connexion a la base
def get_db():
    """Ouvre (ou reutilise) une connexion sqlite3 pour la requete en cours."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id

# Outils divers
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def save_uploaded_photo(file_storage):
    """Enregistre une photo uploadee et renvoie son nom de fichier.
    Renvoie 'placeholder.svg' si aucun fichier valide n'a ete fourni."""
    if file_storage and file_storage.filename and allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)
        # On prefixe par un timestamp pour eviter les collisions de noms
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return f"uploads/{filename}"
    return "placeholder.svg"


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Veuillez vous connecter pour acceder a l'administration.", "error")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


@app.context_processor
def inject_globals():
    """Variables disponibles dans tous les templates (ex: le bandeau
    d'actualites affiche dans l'en-tete de chaque page)."""
    ticker_items = query_db(
        "SELECT id, titre FROM actualites ORDER BY date_publication DESC LIMIT 6"
    )
    return {
        "current_year": datetime.now().year,
        "nom_ufr": "UFR Sciences et Technologies Avancées (STA)",
        "ticker_items": ticker_items,
    }


# PARTIE PUBLIQUE (visiteurs)
@app.route("/")
def index():
    dernieres_actualites = query_db(
        "SELECT * FROM actualites ORDER BY date_publication DESC LIMIT 3"
    )
    departements = query_db("SELECT * FROM departements")
    return render_template(
        "index.html",
        actualites=dernieres_actualites,
        departements=departements,
    )


# Departements 
@app.route("/departements")
def departements():
    deps = query_db("SELECT * FROM departements ORDER BY nom")
    return render_template("departements.html", departements=deps)


@app.route("/departements/<int:dep_id>")
def departement_detail(dep_id):
    dep = query_db("SELECT * FROM departements WHERE id = ?", (dep_id,), one=True)
    if dep is None:
        abort(404)
    formations_dep = query_db(
        "SELECT * FROM formations WHERE departement_id = ? ORDER BY nom", (dep_id,)
    )
    return render_template(
        "departement_detail.html", departement=dep, formations=formations_dep
    )

#  Formations 
@app.route("/formations")
def formations():
    formations_list = query_db(
        """SELECT formations.*, departements.nom AS departement_nom
           FROM formations
           JOIN departements ON formations.departement_id = departements.id
           ORDER BY departements.nom, formations.nom"""
    )
    return render_template("formations.html", formations=formations_list)


@app.route("/formations/<int:formation_id>")
def formation_detail(formation_id):
    formation = query_db(
        """SELECT formations.*, departements.nom AS departement_nom
           FROM formations
           JOIN departements ON formations.departement_id = departements.id
           WHERE formations.id = ?""",
        (formation_id,),
        one=True,
    )
    if formation is None:
        abort(404)
    modules = query_db(
        "SELECT * FROM programme_modules WHERE formation_id = ? ORDER BY semestre, id",
        (formation_id,),
    )
    # On regroupe les modules par semestre pour faciliter l'affichage
    programme = {}
    for m in modules:
        programme.setdefault(m["semestre"], []).append(m["nom_module"])
    return render_template(
        "formation_detail.html", formation=formation, programme=programme
    )


# Actualites 
@app.route("/actualites")
def actualites():
    liste = query_db("SELECT * FROM actualites ORDER BY date_publication DESC")
    return render_template("actualites.html", actualites=liste)


@app.route("/actualites/<int:actu_id>")
def actualite_detail(actu_id):
    actu = query_db("SELECT * FROM actualites WHERE id = ?", (actu_id,), one=True)
    if actu is None:
        abort(404)
    return render_template("actualite_detail.html", actualite=actu)


#  Activites (module principal) 
@app.route("/activites")
def activites():
    liste = query_db("SELECT * FROM activites ORDER BY date_activite DESC")
    return render_template("activites.html", activites=liste)


@app.route("/activites/<int:activite_id>")
def activite_detail(activite_id):
    activite = query_db("SELECT * FROM activites WHERE id = ?", (activite_id,), one=True)
    if activite is None:
        abort(404)
    photos = query_db(
        "SELECT * FROM activite_photos WHERE activite_id = ?", (activite_id,)
    )
    return render_template(
        "activite_detail.html", activite=activite, photos=photos
    )


# Galerie photos
@app.route("/galerie")
def galerie():
    albums = query_db("SELECT * FROM albums ORDER BY date_album DESC")
    # petite miniature par album (premiere photo trouvee)
    albums_avec_couverture = []
    for album in albums:
        couverture = query_db(
            "SELECT filename FROM album_photos WHERE album_id = ? LIMIT 1",
            (album["id"],),
            one=True,
        )
        albums_avec_couverture.append(
            {**dict(album), "couverture": couverture["filename"] if couverture else "placeholder.svg"}
        )
    return render_template("galerie.html", albums=albums_avec_couverture)


@app.route("/galerie/<int:album_id>")
def album_detail(album_id):
    album = query_db("SELECT * FROM albums WHERE id = ?", (album_id,), one=True)
    if album is None:
        abort(404)
    photos = query_db("SELECT * FROM album_photos WHERE album_id = ?", (album_id,))
    return render_template("album_detail.html", album=album, photos=photos)

# Enseignants
@app.route("/enseignants")
def enseignants():
    liste = query_db(
        """SELECT enseignants.*, departements.nom AS departement_nom
           FROM enseignants
           LEFT JOIN departements ON enseignants.departement_id = departements.id
           ORDER BY enseignants.nom"""
    )
    return render_template("enseignants.html", enseignants=liste)

# Contact
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        sujet = request.form.get("sujet", "").strip()
        message = request.form.get("message", "").strip()

        if not nom or not email or not message:
            flash("Merci de remplir au minimum votre nom, votre email et votre message.", "error")
            return render_template("contact.html", form_data=request.form)

        execute_db(
            "INSERT INTO messages_contact (nom, email, sujet, message, date_envoi) "
            "VALUES (?, ?, ?, ?, ?)",
            (nom, email, sujet, message, datetime.now().strftime("%Y-%m-%d %H:%M")),
        )
        flash("Votre message a bien ete envoye. Nous reviendrons vers vous rapidement.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html", form_data={})

# PARTIE ADMINISTRATION (back-office)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = query_db(
            "SELECT * FROM admin_users WHERE username = ?", (username,), one=True
        )
        if user and check_password_hash(user["password_hash"], password):
            session["admin_logged_in"] = True
            session["admin_username"] = user["username"]
            flash(f"Bienvenue, {user['username']} !", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Identifiant ou mot de passe incorrect.", "error")

    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Vous avez ete deconnecte.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    stats = {
        "actualites": query_db("SELECT COUNT(*) AS c FROM actualites", one=True)["c"],
        "activites": query_db("SELECT COUNT(*) AS c FROM activites", one=True)["c"],
        "albums": query_db("SELECT COUNT(*) AS c FROM albums", one=True)["c"],
        "formations": query_db("SELECT COUNT(*) AS c FROM formations", one=True)["c"],
        "messages": query_db("SELECT COUNT(*) AS c FROM messages_contact", one=True)["c"],
    }
    return render_template("admin/dashboard.html", stats=stats)


# Administration : Actualites (CRUD complet -> modele a suivre)
@app.route("/admin/actualites")
@login_required
def admin_actualites():
    liste = query_db("SELECT * FROM actualites ORDER BY date_publication DESC")
    return render_template("admin/actualites_list.html", actualites=liste)


@app.route("/admin/actualites/ajouter", methods=["GET", "POST"])
@login_required
def admin_actualite_ajouter():
    if request.method == "POST":
        photo = save_uploaded_photo(request.files.get("photo"))
        execute_db(
            "INSERT INTO actualites (titre, date_publication, description, photo, categorie) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                request.form["titre"],
                request.form["date_publication"],
                request.form.get("description", ""),
                photo,
                request.form.get("categorie", "actualite"),
            ),
        )
        flash("Actualite ajoutee avec succes.", "success")
        return redirect(url_for("admin_actualites"))

    return render_template("admin/actualite_form.html", actualite=None)


@app.route("/admin/actualites/modifier/<int:actu_id>", methods=["GET", "POST"])
@login_required
def admin_actualite_modifier(actu_id):
    actu = query_db("SELECT * FROM actualites WHERE id = ?", (actu_id,), one=True)
    if actu is None:
        abort(404)

    if request.method == "POST":
        nouveau_fichier = request.files.get("photo")
        if nouveau_fichier and nouveau_fichier.filename:
            photo = save_uploaded_photo(nouveau_fichier)
        else:
            photo = actu["photo"]  # on garde l'ancienne photo si rien n'est envoye

        execute_db(
            "UPDATE actualites SET titre=?, date_publication=?, description=?, photo=?, categorie=? "
            "WHERE id=?",
            (
                request.form["titre"],
                request.form["date_publication"],
                request.form.get("description", ""),
                photo,
                request.form.get("categorie", "actualite"),
                actu_id,
            ),
        )
        flash("Actualite modifiee avec succes.", "success")
        return redirect(url_for("admin_actualites"))

    return render_template("admin/actualite_form.html", actualite=actu)


@app.route("/admin/actualites/supprimer/<int:actu_id>", methods=["POST"])
@login_required
def admin_actualite_supprimer(actu_id):
    execute_db("DELETE FROM actualites WHERE id = ?", (actu_id,))
    flash("Actualite supprimee.", "success")
    return redirect(url_for("admin_actualites"))


# Administration : Activites
@app.route("/admin/activites")
@login_required
def admin_activites():
    liste = query_db("SELECT * FROM activites ORDER BY date_activite DESC")
    return render_template("admin/activites_list.html", activites=liste)


@app.route("/admin/activites/ajouter", methods=["GET", "POST"])
@login_required
def admin_activite_ajouter():
    if request.method == "POST":
        activite_id = execute_db(
            "INSERT INTO activites (titre, date_activite, lieu, organisateur, description, type_activite) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                request.form["titre"],
                request.form["date_activite"],
                request.form.get("lieu", ""),
                request.form.get("organisateur", ""),
                request.form.get("description", ""),
                request.form.get("type_activite", "activite"),
            ),
        )
        fichiers = request.files.getlist("photos")
        for fichier in fichiers:
            if fichier and fichier.filename:
                nom_fichier = save_uploaded_photo(fichier)
                execute_db(
                    "INSERT INTO activite_photos (activite_id, filename) VALUES (?, ?)",
                    (activite_id, nom_fichier),
                )
        flash("Activite ajoutee avec succes.", "success")
        return redirect(url_for("admin_activites"))

    return render_template("admin/activite_form.html")

@app.route("/admin/activites/supprimer/<int:activite_id>", methods=["POST"])
@login_required
def admin_activite_supprimer(activite_id):
    execute_db("DELETE FROM activites WHERE id = ?", (activite_id,))
    flash("Activite supprimee.", "success")
    return redirect(url_for("admin_activites"))

@app.route("/admin/activites/modifier/<int:activite_id>", methods=["GET", "POST"])
@login_required
def admin_activite_modifier(activite_id):
    activite = query_db("SELECT * FROM activites WHERE id = ?", (activite_id,), one=True)
    if activite is None:
        abort(404)

    if request.method == "POST":
        execute_db(
            "UPDATE activites SET titre=?, date_activite=?, lieu=?, organisateur=?, "
            "description=?, type_activite=? WHERE id=?",
            (
                request.form["titre"],
                request.form["date_activite"],
                request.form.get("lieu", ""),
                request.form.get("organisateur", ""),
                request.form.get("description", ""),
                request.form.get("type_activite", "activite"),
                activite_id,
            ),
        )

        # Les nouvelles photos envoyees viennent s'ajouter a la galerie existante
        fichiers = request.files.getlist("photos")
        for fichier in fichiers:
            if fichier and fichier.filename:
                nom_fichier = save_uploaded_photo(fichier)
                execute_db(
                    "INSERT INTO activite_photos (activite_id, filename) VALUES (?, ?)",
                    (activite_id, nom_fichier),
                )

        flash("Activite modifiee avec succes.", "success")
        return redirect(url_for("admin_activites"))

    photos = query_db(
        "SELECT * FROM activite_photos WHERE activite_id = ?", (activite_id,)
    )
    return render_template(
        "admin/activite_form.html", activite=activite, photos=photos
    )


@app.route("/admin/activites/photo/supprimer/<int:photo_id>", methods=["POST"])
@login_required
def admin_activite_photo_supprimer(photo_id):
    photo = query_db(
        "SELECT * FROM activite_photos WHERE id = ?", (photo_id,), one=True
    )
    if photo is None:
        abort(404)
    activite_id = photo["activite_id"]
    execute_db("DELETE FROM activite_photos WHERE id = ?", (photo_id,))
    flash("Photo supprimee de l'activite.", "success")
    return redirect(url_for("admin_activite_modifier", activite_id=activite_id))


# Administration : Formations
@app.route("/admin/formations")
@login_required
def admin_formations():
    liste = query_db(
        """SELECT formations.*, departements.nom AS departement_nom
           FROM formations
           JOIN departements ON formations.departement_id = departements.id
           ORDER BY departements.nom, formations.nom"""
    )
    return render_template("admin/formations_list.html", formations=liste)


@app.route("/admin/formations/ajouter", methods=["GET", "POST"])
@login_required
def admin_formation_ajouter():
    departements_list = query_db("SELECT * FROM departements ORDER BY nom")

    if request.method == "POST":
        execute_db(
            "INSERT INTO formations "
            "(departement_id, nom, niveau, duree, conditions_admission, debouches) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                request.form["departement_id"],
                request.form["nom"],
                request.form.get("niveau", ""),
                request.form.get("duree", ""),
                request.form.get("conditions_admission", ""),
                request.form.get("debouches", ""),
            ),
        )
        flash("Formation ajoutee avec succes.", "success")
        return redirect(url_for("admin_formations"))

    return render_template("admin/formation_form.html", departements=departements_list)


@app.route("/admin/formations/supprimer/<int:formation_id>", methods=["POST"])
@login_required
def admin_formation_supprimer(formation_id):
    execute_db("DELETE FROM formations WHERE id = ?", (formation_id,))
    flash("Formation supprimee.", "success")
    return redirect(url_for("admin_formations"))

@app.route("/admin/formations/modifier/<int:formation_id>", methods=["GET", "POST"])
@login_required
def admin_formation_modifier(formation_id):
    formation = query_db(
        "SELECT * FROM formations WHERE id = ?", (formation_id,), one=True
    )
    if formation is None:
        abort(404)

    if request.method == "POST":
        execute_db(
            "UPDATE formations SET departement_id=?, nom=?, niveau=?, duree=?, "
            "conditions_admission=?, debouches=? WHERE id=?",
            (
                request.form["departement_id"],
                request.form["nom"],
                request.form.get("niveau", ""),
                request.form.get("duree", ""),
                request.form.get("conditions_admission", ""),
                request.form.get("debouches", ""),
                formation_id,
            ),
        )
        flash("Formation modifiee avec succes.", "success")
        return redirect(url_for("admin_formation_modifier", formation_id=formation_id))

    departements_list = query_db("SELECT * FROM departements ORDER BY nom")
    modules = query_db(
        "SELECT * FROM programme_modules WHERE formation_id = ? ORDER BY semestre, id",
        (formation_id,),
    )
    programme = {}
    for m in modules:
        programme.setdefault(m["semestre"], []).append(m)

    return render_template(
        "admin/formation_form.html",
        formation=formation,
        departements=departements_list,
        programme=programme,
    )


@app.route("/admin/formations/<int:formation_id>/modules/ajouter", methods=["POST"])
@login_required
def admin_module_ajouter(formation_id):
    formation = query_db(
        "SELECT id FROM formations WHERE id = ?", (formation_id,), one=True
    )
    if formation is None:
        abort(404)

    nom_module = request.form.get("nom_module", "").strip()
    semestre = request.form.get("semestre", "").strip()
    if nom_module and semestre:
        execute_db(
            "INSERT INTO programme_modules (formation_id, semestre, nom_module) "
            "VALUES (?, ?, ?)",
            (formation_id, semestre, nom_module),
        )
        flash("Module ajoute au programme.", "success")
    else:
        flash("Merci d'indiquer un semestre et un nom de module.", "error")

    return redirect(url_for("admin_formation_modifier", formation_id=formation_id))


@app.route("/admin/formations/modules/supprimer/<int:module_id>", methods=["POST"])
@login_required
def admin_module_supprimer(module_id):
    module = query_db(
        "SELECT * FROM programme_modules WHERE id = ?", (module_id,), one=True
    )
    if module is None:
        abort(404)
    formation_id = module["formation_id"]
    execute_db("DELETE FROM programme_modules WHERE id = ?", (module_id,))
    flash("Module supprime du programme.", "success")
    return redirect(url_for("admin_formation_modifier", formation_id=formation_id))


# Administration : Galerie
@app.route("/admin/galerie")
@login_required
def admin_galerie():
    albums = query_db("SELECT * FROM albums ORDER BY date_album DESC")
    return render_template("admin/galerie_list.html", albums=albums)


@app.route("/admin/galerie/ajouter", methods=["GET", "POST"])
@login_required
def admin_album_ajouter():
    if request.method == "POST":
        album_id = execute_db(
            "INSERT INTO albums (titre, description, date_album) VALUES (?, ?, ?)",
            (
                request.form["titre"],
                request.form.get("description", ""),
                request.form.get("date_album", datetime.now().strftime("%Y-%m-%d")),
            ),
        )
        fichiers = request.files.getlist("photos")
        for fichier in fichiers:
            if fichier and fichier.filename:
                nom_fichier = save_uploaded_photo(fichier)
                execute_db(
                    "INSERT INTO album_photos (album_id, filename) VALUES (?, ?)",
                    (album_id, nom_fichier),
                )
        flash("Album ajoute avec succes.", "success")
        return redirect(url_for("admin_galerie"))

    return render_template("admin/album_form.html")


@app.route("/admin/galerie/supprimer/<int:album_id>", methods=["POST"])
@login_required
def admin_album_supprimer(album_id):
    execute_db("DELETE FROM albums WHERE id = ?", (album_id,))
    flash("Album supprime.", "success")
    return redirect(url_for("admin_galerie"))

@app.route("/admin/galerie/<int:album_id>")
@login_required
def admin_album_detail(album_id):
    album = query_db("SELECT * FROM albums WHERE id = ?", (album_id,), one=True)
    if album is None:
        abort(404)
    photos = query_db("SELECT * FROM album_photos WHERE album_id = ?", (album_id,))
    return render_template("admin/album_detail.html", album=album, photos=photos)


@app.route("/admin/galerie/photo/supprimer/<int:photo_id>", methods=["POST"])
@login_required
def admin_album_photo_supprimer(photo_id):
    photo = query_db(
        "SELECT * FROM album_photos WHERE id = ?", (photo_id,), one=True
    )
    if photo is None:
        abort(404)
    album_id = photo["album_id"]
    execute_db("DELETE FROM album_photos WHERE id = ?", (photo_id,))
    flash("Photo supprimee de l'album.", "success")
    return redirect(url_for("admin_album_detail", album_id=album_id))


# Gestion des erreurs
@app.errorhandler(404)
def page_non_trouvee(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    if not os.path.exists(app.config["DATABASE"]):
        print("Base de donnees introuvable. Lancez d'abord : python init_db.py")
    app.run(debug=True)
