#importation des bibliothèques
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from backend import db, login_manager,app
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ARRAY  #import database

#Configuration des tables de la base de données
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
# Créer un objet de connexion à la base de données

class User(db.Model, UserMixin):
    # Postgresql n'autorise pas les noms de table "user".
    __tablename__ = "admin1"  # la tables admin1 de les utilisateurs

    #Ajouter des colonnes pour la table
    # id type is serial on postgre
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
        
    #Comment notre objet est imprimé
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def get_id(self):
        return self.id


class Article(db.Model):

    __tablename__ = "article2"
      
      #Ajouter des colonnes pour la table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    link = db.Column(db.Text)
    authors = db.Column(db.Text)
    references = db.Column(ARRAY(db.Integer))
    year = db.Column(db.Integer)
#Comment notre objet est imprimé
    def __repr__(self):
        return f"Article('{self.id}', '{self.title}')"
