#importation des bibliothèques
from flask import render_template, url_for, flash, redirect, request #import toutes les fonctions flask nécessaires
from backend import app, db, bcrypt, mail
from backend.forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchForm, RequestResetForm, ResetPasswordForm
from backend.models import User, Article
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from backend.recommendation import recommender

#Page d'accueil pour tous
@app.route("/") #URL par défaut
@app.route("/home") 
def home(): #Fonction de la page d'accueil
    page = request.args.get("page", 1, type=int)
    articles = Article.query.order_by(Article.year.desc()).paginate(page=page, per_page=10) #pour affichier 10 articles dans chaque page
    return render_template("home.html", posts=articles) #charger la page d'accueil avec les informations

#Page about
@app.route("/about") #URL pour la page about
def about():  #Fonction de la page about
    return render_template("about.html", title="About") #charger la page about avec les informations


@app.route("/register", methods=["GET", "POST"])  #URL pour la page register
def register():   #Fonction de la page register
    if current_user.is_authenticated:
        return redirect(url_for("home")) # retourne la page home
    form = RegistrationForm()
    if form.validate_on_submit(): # vérifier les informations saisi par l'utilisateur
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8") #Obtenir la version hachée
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user) # ajouter a la BD dans la table user
        db.session.commit()   #sauvegarde les changements
        flash("Your account has been created! You are now able to log in", "success") # affichier un message
        return redirect(url_for("login")) # retourne la page login
    return render_template("register.html", title="Register", form=form) #charger la page register avec les informations


@app.route("/login", methods=["GET", "POST"]) #URL pour la page login
def login():  #Fonction de la page login
    if current_user.is_authenticated:  
        return redirect(url_for("home")) # retourne la page home
    form = LoginForm()
    if form.validate_on_submit():  # vérifier les informations saisi par l'utilisateur
        user = User.query.filter_by(email=form.email.data).first()  #vérifier si l'utilisateur existe et obtenir les informations du compte
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home")) 
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")  #Compte utilisateur non vérifié
    return render_template("login.html", title="Login", form=form)  #charger la page login avec les informations


@app.route("/logout") #URL pour la page logout
def logout():   #Fonction de la page logout
    logout_user()
    return redirect(url_for("home")) # retourne la page home

@app.route("/account", methods=["GET", "POST"])  #URL pour la page account
@login_required
def account():
    """
    Description : difinition de la fonction account
    
    """
    form = UpdateAccountForm()
    if form.validate_on_submit():  # pour que l'utilisateur peut modifier l username ou l email 
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()   #sauvegarde les changements
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":  #L'utilisateur charge la page
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template("account.html", title="Account", form=form) #charger la page account avec les informations


@app.route("/post/<post_id>")#URL pour la page post
def post(post_id): # la foction post elle prend en compte id de chaque article pour afficher le bloc de chaque article
    article = Article.query.get_or_404(post_id)

    # Obtenir l'index des articles similaires
    obj = recommender.Recommender(article.id)
    results = obj.get_similar_articles()

    # Récupérer les articles similaires dans la base de données
    related_articles = []
    for i in results:
        tmp = Article.query.filter_by(id=int(i)).first()  #vérifier si l'article existe 
        related_articles.append(tmp)

    return render_template(
        "post.html",
        title=article.title,
        post=article,
        related_articles=related_articles
    )    #charger la page post avec les informations


# Search
@app.route("/search", methods=["POST"]) #URL pour la page search
def search():  #Fonction de la page search
    form = SearchForm()
    articles = Article.query
    page = request.args.get("page", 1, type=int)

    if form.validate_on_submit:
        post.searched = form.searched.data

        articles = articles.filter(
            Article.title.like("%" + post.searched + "%") # pour faire la recherche avec le titre des l'article
        )
        articles = articles.order_by(Article.year.desc()).paginate(page=page, per_page=10) # pour affichier 10 a rticles dans chaque page

        return render_template(
            "search.html", 
            form=form, 
            searched=post.searched, 
            posts=articles
        ) #charger la page de resultat de la recherche avec les informations

def send_reset_email(user): # la fonction qui retourne l email envoyer pour restorer le mot de pass de l utilisateur
    # Générer un lien reset_password_link
    token = user.get_reset_token()
    msg = Message('Password Reset Request',   # le message envoyer a l' utilisateur 
                  sender='srcscholar801@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST']) #URL pour la page reset password
def reset_request(): #Fonction de la page Demande de réinitialisation de mot de pass
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # retourne la page home
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() #vérifier si l'email existe 
        send_reset_email(user) # envoyer um mail a l'utilisateur 
        flash('An email has been sent with instructions to reset your password.', 'info') # le message affichier
        return redirect(url_for('login'))  #réorienter vers la page login
    return render_template('reset_request.html', title='Reset Password', form=form) #charger la page réinitialisation de mot de pass avec les informations



@app.route("/reset_password/<token>", methods=['GET', 'POST']) #URL pour la page de creation de nouvaux mot de pass
def reset_token(token): #Fonction de la page de creation de nouvaux mot de pass
    if current_user.is_authenticated:
        return redirect(url_for('home'))   #réorienter vers la page home
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning') # le message d'alerte affichier
        return redirect(url_for('reset_request')) #réorienter vers la page de renitialisation de PSW
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()  #sauvegarde les changements
        flash('Your password has been updated! You are now able to log in', 'success') # le message de success affichier 
        return redirect(url_for('login')) #réorienter vers la page login
    return render_template('reset_token.html', title='Reset Password', form=form) #charger la page creation de nouvaux mot de pass avec les informations