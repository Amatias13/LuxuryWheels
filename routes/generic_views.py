from flask import Blueprint, render_template, request
from datetime import date, timedelta
import logging

# Ensure models are loaded and import common model classes at module level
from models import ensure_loaded
ensure_loaded()
from models import VehicleBrand


def make_list_blueprint(bp_name, route_path, model, template, context_key='items',
                         extra_models=None, per_page=8):
    """Blueprint com paginacao, filtros de pesquisa e modelos extra."""
    bp = Blueprint(bp_name, __name__)

    @bp.route(route_path)
    def list_view():
        page = request.args.get('page', 1, type=int)
        # Helper: obter último valor não-vazio para um argumento (lida com chaves duplicadas)
        def last_nonempty_arg(name, cast=None):
            vals = request.args.getlist(name)
            if not vals:
                return None
            for v in reversed(vals):
                if v is None:
                    continue
                s = str(v).strip()
                if s == '':
                    continue
                if cast:
                    try:
                        return cast(s)
                    except (ValueError, TypeError):
                        return None
                return s

        search = (last_nonempty_arg('car_search') or '').strip()
        # Ler datas opcionais para filtrar disponibilidade
        start_raw = last_nonempty_arg('startDate')
        end_raw = last_nonempty_arg('endDate')
        start_date = None
        end_date = None
        if start_raw and end_raw:
            try:
                start_date = date.fromisoformat(start_raw)
                end_date = date.fromisoformat(end_raw)
            except (ValueError, TypeError) as e:
                logging.debug("Invalid date filters: %s", e)
                start_date = None
                end_date = None
        type_filter = last_nonempty_arg('type_filter', cast=int)
        category_filter = last_nonempty_arg('category_filter', cast=int)
        max_price = last_nonempty_arg('max_price', cast=float)
        # capacity_filter may be '9+' in UI; tratar esse caso
        cap_raw = last_nonempty_arg('capacity_filter')
        capacity_filter = None
        if cap_raw:
            if str(cap_raw).endswith('+'):
                try:
                    capacity_filter = int(str(cap_raw).replace('+', ''))
                except (ValueError, TypeError):
                    capacity_filter = None
            else:
                try:
                    capacity_filter = int(cap_raw)
                except (ValueError, TypeError):
                    capacity_filter = None

        query = model.query

        # T5: excluir veiculos com revisao vencida ou legalizacao > 1 ano
        if hasattr(model, 'nextRevisionDate'):
            today = date.today()
            one_year_ago = today - timedelta(days=365)
            query = query.filter(
                model.nextRevisionDate >= today,
                model.lastLegalizationDate >= one_year_ago,
                model.isActive == 1,
            )

        # Filtros de pesquisa
        if search and hasattr(model, 'model'):
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
        # Filtrar indisponíveis no intervalo (se fornecido). Nota: isto filtra
        # apenas os itens da página atual — pode reduzir o número real mostrado.
        data = []
        for o in pagination.items:
            try:
                # Se houver um intervalo pedido, validar disponibilidade e
                # preencher o campo `available` no dicionário do veículo.
                od = o.to_dict()
                if start_date and end_date and hasattr(o, 'is_available'):
                    try:
                        od['available'] = o.is_available(start_date, end_date)
                        if not od['available']:
                            continue
                    except Exception as e:
                        # Em caso de erro ao validar disponibilidade, saltar o veículo
                        logging.exception("Error checking availability for item in list")
                        continue
            except Exception as e:
                logging.exception("Error processing item for listing")
                continue
            data.append(od)

        context = {
            context_key: data,
            'pagination': pagination,
            'search': search,
            'startDate': start_raw,
            'endDate': end_raw,
            'type_filter': type_filter,
            'category_filter': category_filter,
            'max_price': max_price,
            'capacity_filter': capacity_filter,
        }

        if extra_models:
            for key, extra_model in extra_models.items():
                try:
                    context[key] = [o.to_dict() for o in extra_model.query.all()]
                except Exception as e:
                    logging.exception("Error loading extra model %s", key)
                    context[key] = []

        return render_template(template, **context)

    return bp


def db_or(*args):
    from sqlalchemy import or_
    return or_(*args)
