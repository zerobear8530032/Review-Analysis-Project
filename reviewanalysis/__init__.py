from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from reviewanalysis.scrappers import AmazonScrapper
from reviewanalysis.scrappers import FlipKartScrapper
from pyngrok import ngrok
app = Flask(__name__)
ngrok.set_auth_token("2ocsOkAtir0rfQIM3f6cdYVQNfZ_3MVnEmcdLzhSETy5yu7gW")
public_url=ngrok.connect(5000).public_url
print(public_url)
app.config["SECRET_KEY"] = "9e166102899e65f779885fafe818473a"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
db = SQLAlchemy(app)
bcrypt =Bcrypt(app)
login_manager = LoginManager(app)
# Importing routes after creating the Flask app instance
login_manager.login_view='login'
login_manager.login_message_category='info'
app.config['MAIL_SERVER']="smtp.googlemail.com"
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']="saboorabdul627@gmail.com"
app.config['MAIL_PASSWORD']="axcakapeekqjzpzm"
mail = Mail(app)
amazon = AmazonScrapper()
flipkart = FlipKartScrapper()

from reviewanalysis import routes
app.app_context().push()
