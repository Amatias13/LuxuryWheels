import os
from flask import Flask, render_template
from database import init_db, db

app = Flask(__name__, static_folder="templates/assets", static_url_path="/assets")

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
from models import User

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
        # Enable searching by vehicle model and by brand name (best-effort)
        search_fields=["model"],
        brand_lookup={
            "model": VehicleBrand,
            "name_field": "name",
            "id_field": "idBrand",
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


@app.context_processor
def inject_current_user():
    from flask import session

    user = None
    user_id = session.get("user_id")
    if user_id:
        try:
            user = User.query.get(int(user_id))
        except Exception as e:
            import logging

            logging.exception("Error loading current user")
            user = None
    # always expose if there is a session, even if the object fails to load
    return {
        "current_user": user,
        "is_logged_in": bool(user_id),
    }
