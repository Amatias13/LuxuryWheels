import os
from flask import Flask, render_template
from database import init_db, db

app = Flask(__name__, static_folder="templates/assets", static_url_path="/assets")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-muda-em-producao")

init_db(app)

import models as _models_pkg

_models_pkg.load_models()

with app.app_context():
    db.create_all()

from routes.users import bp as users_bp
from routes.reservations import bp as reservations_bp
from routes.payment_methods import bp as payment_methods_bp

app.register_blueprint(users_bp)
app.register_blueprint(reservations_bp)
app.register_blueprint(payment_methods_bp)

from routes.generic_views import make_list_blueprint
from models import Vehicle, VehicleType, VehicleCategory, VehicleBrand, Testimonial

app.register_blueprint(
    make_list_blueprint(
        "vehicles",
        "/car-list",
        Vehicle,
        "car-list.html",
        context_key="vehicles",
        extra_models={
            "types": VehicleType,
            "categories": VehicleCategory,
            "brands": VehicleBrand,
            "testimonials": Testimonial,
        },
    )
)

from routes.generic_api import register_models as register_generic_models

model_classes = [getattr(_models_pkg, name) for name in _models_pkg.__all__]
register_generic_models(app, model_classes, prefix="/api")


@app.route("/")
def home():
    featured = [v.to_dict() for v in Vehicle.query.all()]
    types = [t.to_dict() for t in VehicleType.query.all()]
    testimonials = [t.to_dict() for t in Testimonial.query.filter_by(isActive=1).all()]
    return render_template(
        "index.html",
        title="Home",
        featured=featured,
        types=types,
        testimonials=testimonials,
    )


@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contacto")