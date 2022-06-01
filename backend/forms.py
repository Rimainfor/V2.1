#importation des bibliothèques
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from backend.models import User


class RegistrationForm(FlaskForm):  # creation de la classe registration 
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):  #Fonction qui valide username 
        user = User.query.filter_by(username=username.data).first() #vérifier si l'utilisateur existe
        if user:
            raise ValidationError("That username is taken. Please choose a different one.")  #affichier un message d' erreur

    def validate_email(self, email): #Fonction qui valide l'email
        user = User.query.filter_by(email=email.data).first() #vérifier si l'e_mail existe
        if user:
            raise ValidationError("That email is taken. Please choose a different one.") #affichier un message d' erreur


class LoginForm(FlaskForm):  # creation de la classe login 
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):  # creation de la classe de MSJ de le compt de l'utilisateur
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])

    submit = SubmitField("Update")

    def validate_username(self, username): #Fonction qui valide username
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first() #vérifier si l'utilisateur existe
            if user:
                raise ValidationError("That username is taken. Please choose a different one.")

    def validate_email(self, email):    #Fonction qui valide l'email
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()   #vérifier si l'e_mail existe
            if user:
                raise ValidationError("That email is taken. Please choose a different one.")


class SearchForm(FlaskForm):   # creation de la classe de recherche
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Search")

class RequestResetForm(FlaskForm):  # creation de la classe de Demande de réinitialisation de PSW
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()  #vérifier si l'e_mail existe
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):   # creation de la classe de réinitialisation de PSW
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')