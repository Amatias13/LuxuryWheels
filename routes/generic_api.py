from flask import Blueprint, request, jsonify
from database import db
from datetime import date, datetime
from decimal import Decimal
import uuid
import logging


def serialize_value(v):
    """Convert common non-JSON-native types to serializable forms."""
    # None, primitives
    if v is None or isinstance(v, (str, bool, int, float)):
        return v
    # Dates/datetimes
    if isinstance(v, (date, datetime)):
        try:
            return v.isoformat()
        except Exception as e:
            logging.exception("Error serializing datetime")
            return str(v)
    # Decimal -> float
    if isinstance(v, Decimal):
        try:
            return float(v)
        except (TypeError, ValueError) as e:
            logging.exception("Error converting Decimal to float")
            return str(v)
    # UUID
    if isinstance(v, uuid.UUID):
        return str(v)
    # bytes
    if isinstance(v, (bytes, bytearray)):
        try:
            return v.decode("utf-8")
        except Exception as e:
            logging.exception("Error decoding bytes")
            return str(v)
    # dict/list/tuple -> recurse
    if isinstance(v, dict):
        return {k: serialize_value(val) for k, val in v.items()}
    if isinstance(v, (list, tuple)):
        return [serialize_value(x) for x in v]
    # Fallback
    try:
        return str(v)
    except Exception as e:
        logging.exception("Error stringifying value")
        return None


def serialize_model(obj):
    """Serialize a SQLAlchemy model or object to JSON-safe primitives.

    If the object implements `to_dict()` it will be used and its values
    will be converted via `serialize_value`.
    """
    if hasattr(obj, "to_dict"):
        d = obj.to_dict() or {}
        return {k: serialize_value(v) for k, v in d.items()}
    data = {}
    for col in obj.__table__.columns:
        data[col.name] = serialize_value(getattr(obj, col.name))
    return data


def create_from_dict(model, data):
    """If the model has its own create() method, use that (logic in model).
    Otherwise use generic behavior.
    """
    if hasattr(model, "create"):
        res = model.create(data)
        # Support model.create returning either a single instance or
        # a tuple/list with additional data (e.g. (instance, extra1, ...)).
        if isinstance(res, (list, tuple)):
            # try to find the first element that is an instance of the model
            for item in res:
                if isinstance(item, model):
                    return item
            # fallback: return first element
            return res[0]
        return res
    cols = {c.name for c in model.__table__.columns}
    return model(**{k: v for k, v in data.items() if k in cols})


def register_models(app, model_classes, prefix="/api"):
    bp = Blueprint("generic_api", __name__, url_prefix=prefix)

    for model in model_classes:
        name = (
            model.__tablename__ if hasattr(model, "__tablename__") else model.__name__
        ).lower()

        # GET /api/<model>        -> details of all items, with optional filters in body
        # POST /api/<model>       -> create a new item with data in body
        def list_create(model=model):
            if request.method == "GET":
                items = model.query.all()
                return jsonify([serialize_model(i) for i in items])
            data = request.get_json() or {}
            try:
                obj = create_from_dict(model, data)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            db.session.add(obj)
            db.session.commit()
            return jsonify(serialize_model(obj)), 201

        bp.add_url_rule(
            f"/{name}", f"{name}_list_create", list_create, methods=["GET", "POST"]
        )

        # GET /api/<model>/<id>   -> details of one item
        # PUT /api/<model>/<id>   -> updates an item
        # DELETE /api/<model>/<id>-> deletes an item
        def get_update_delete(id, model=model):
            obj = model.query.get_or_404(id)
            if request.method == "GET":
                return jsonify(serialize_model(obj))
            if request.method == "PUT":
                data = request.get_json() or {}
                for k, v in data.items():
                    if hasattr(obj, k):
                        setattr(obj, k, v)
                db.session.commit()
                return jsonify(serialize_model(obj))
            db.session.delete(obj)
            db.session.commit()
            return ("", 204)

        bp.add_url_rule(
            f"/{name}/<int:id>",
            f"{name}_item",
            get_update_delete,
            methods=["GET", "PUT", "DELETE"],
        )

        # POST /api/<model>/find          -> filter items by fields
        def find(model=model):
            payload = request.get_json() or {}
            filters = payload.get("filters", {})
            items = model.query.filter_by(**filters).all()
            return jsonify([serialize_model(i) for i in items])

        bp.add_url_rule(f"/{name}/find", f"{name}_find", find, methods=["POST"])

        # POST /api/<model>/find_by_ids   -> filter items by a list of ids
        def find_by_ids(model=model):
            payload = request.get_json() or {}
            ids = payload.get("ids", [])
            if not isinstance(ids, (list, tuple)):
                return jsonify({"error": "ids must be a list"}), 400
            pk = list(model.__table__.primary_key.columns)[0].name
            items = model.query.filter(getattr(model, pk).in_(ids)).all()
            return jsonify([serialize_model(i) for i in items])

        bp.add_url_rule(
            f"/{name}/find_by_ids", f"{name}_find_by_ids", find_by_ids, methods=["POST"]
        )

    app.register_blueprint(bp)
