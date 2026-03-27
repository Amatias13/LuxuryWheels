from flask import Blueprint, render_template


def make_list_blueprint(bp_name, route_path, model, template, context_key='items'):
    """Create a lightweight blueprint that renders a list template for `model`.

    - `bp_name`: blueprint name (e.g. 'vehicles')
    - `route_path`: URL path for list view (e.g. '/car-list')
    - `model`: SQLAlchemy model class
    - `template`: template filename to render
    - `context_key`: key to pass list into template
    """
    bp = Blueprint(bp_name, __name__)

    @bp.route(route_path)
    def list_view():
        # Keep view very small: fetch from model and pass to template
        objs = model.query.all()
        try:
            data = [o.to_dict() for o in objs]
        except Exception:
            data = objs
        return render_template(template, **{context_key: data})

    return bp
