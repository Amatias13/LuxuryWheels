from flask import Blueprint, render_template, request
from datetime import date, timedelta


def make_list_blueprint(bp_name, route_path, model, template, context_key='items',
                         extra_models=None, per_page=8):
    """Blueprint com paginacao, filtros de pesquisa e modelos extra."""
    bp = Blueprint(bp_name, __name__)

    @bp.route(route_path)
    def list_view():
        page = request.args.get('page', 1, type=int)
        search = request.args.get('car_search', '').strip()
        type_filter = request.args.get('type_filter', type=int)
        category_filter = request.args.get('category_filter', type=int)
        max_price = request.args.get('max_price', type=float)
        capacity_filter = request.args.get('capacity_filter', type=int)

        query = model.query

        # T5: excluir veiculos com revisao vencida ou legalizacao > 1 ano
        """ if hasattr(model, 'nextRevisionDate'):
            today = date.today()
            one_year_ago = today - timedelta(days=365)
            query = query.filter(
                model.nextRevisionDate >= today,
                model.lastLegalizationDate >= one_year_ago,
                model.isActive == 1,
            ) """

        # Filtros de pesquisa
        if search and hasattr(model, 'model'):
            from models.Vehicle_Brand import VehicleBrand
            brand_ids = [b.idBrand for b in VehicleBrand.query.filter(
                VehicleBrand.name.ilike(f'%{search}%')
            ).all()]
            query = query.filter(
                db_or(model.model.ilike(f'%{search}%'),
                      model.idBrand.in_(brand_ids))
            )

        if type_filter and hasattr(model, 'idType'):
            query = query.filter(model.idType == type_filter)

        if category_filter and hasattr(model, 'idCategory'):
            query = query.filter(model.idCategory == category_filter)

        if max_price and hasattr(model, 'dailyRate'):
            query = query.filter(model.dailyRate <= max_price)

        if capacity_filter and hasattr(model, 'capacity'):
            query = query.filter(model.capacity >= capacity_filter)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        data = [o.to_dict() for o in pagination.items]

        context = {
            context_key: data,
            'pagination': pagination,
            'search': search,
            'type_filter': type_filter,
            'category_filter': category_filter,
            'max_price': max_price,
            'capacity_filter': capacity_filter,
        }

        if extra_models:
            for key, extra_model in extra_models.items():
                context[key] = [o.to_dict() for o in extra_model.query.all()]

        return render_template(template, **context)

    return bp


def db_or(*args):
    from sqlalchemy import or_
    return or_(*args)
