import os
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance (initialized by the application)
db = SQLAlchemy()

def init_db(app):
	"""Initialize the SQLAlchemy `db` with the Flask app and set DB URI."""
	# Caminho absoluto para a base de dados
	db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'luxurywheels.db'))
	app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	db.init_app(app)



