from flask import Blueprint, render_template, request
from datetime import date, timedelta
import logging

# Ensure models are loaded and import common model classes at module level
from models import ensure_loaded
ensure_loaded()


def make_list_blueprint(bp_name, route_path, model, template, context_key='items',
                                                 extra_models=None, per_page=8, search_fields=None,
                                                 brand_lookup=None):
    """Blueprint com paginacao, filtros de pesquisa e modelos extra.
    New optional params:
    - `search_fields`: iterable of attribute names on `model` to perform ilike search.
    - `brand_lookup`: dict with keys `model`, `name_field`, `id_field` used to
        find brand ids to include in search (optional).
    """
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
        # Read optional dates for availability filtering. 
        # If provided, availability is determined by reservation overlap.
        #  If not provided, availability is determined by technical checks (revision/legalization). 
        # This allows editing an existing reservation using `exclude_reservation_id` to ignore the reservation itself in availability validation.
        start_raw = last_nonempty_arg('startDate')
        end_raw = last_nonempty_arg('endDate')
        start_time_raw = last_nonempty_arg('startTime')
        end_time_raw = last_nonempty_arg('endTime')
        # Normalize time strings for UI/timepicker. Convert values like
        # "9" or "9:00" into a standard "HH:MM AM/PM" format so the
        # client-side picker initializes with the correct time instead
        # of falling back to its default (e.g. "12:35").
        from utils import parse_time
        from datetime import time as dt_time
        try:
            if start_time_raw:
                t = parse_time(start_time_raw)
                # format as 12-hour with AM/PM (matches client expectations)
                start_time_raw = t.strftime("%I:%M %p")
        except Exception:
            # leave as-is on parse failure
            pass
        try:
            if end_time_raw:
                t2 = parse_time(end_time_raw)
                end_time_raw = t2.strftime("%I:%M %p")
        except Exception:
            pass
        start_date = None
        end_date = None
        # Accept either both dates or a single date. If only one date is
        # provided, treat the requested interval as that day -> next day
        # (i.e. a single-day reservation) so availability is still checked.
        try:
            if start_raw:
                start_date = date.fromisoformat(start_raw)
            if end_raw:
                end_date = date.fromisoformat(end_raw)
            if start_date and not end_date:
                end_date = start_date + timedelta(days=1)
            if end_date and not start_date:
                start_date = end_date - timedelta(days=1)
            # If times were provided, convert to datetimes later when checking availability
        except (ValueError, TypeError) as e:
            logging.debug("Invalid date filters: %s", e)
            start_date = None
            end_date = None
        type_filter = last_nonempty_arg('type_filter', cast=int)
        category_filter = last_nonempty_arg('category_filter', cast=int)
        brand_filter = last_nonempty_arg('brand_filter', cast=int)
        min_price = last_nonempty_arg('min_price', cast=float)
        max_price = last_nonempty_arg('max_price', cast=float)
        # Optional ordering: 'price_asc' or 'price_desc'
        order_by = last_nonempty_arg('order_by')
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

        # T5: exclude vehicles with overdue revision or legalization > 1 year 
        if hasattr(model, 'nextRevisionDate'):
            today = date.today()
            one_year_ago = today - timedelta(days=365)
            # Always apply technical checks (revision/legalization). Do NOT
            # filter by `isActive` here — availability is computed by
            # `is_available()` so catalog visibility should follow that logic.
            query = query.filter(
                model.nextRevisionDate >= today,
                model.lastLegalizationDate >= one_year_ago,
            )

        # Search filters (configurable)
        if search:
            filters = []
            if search_fields:
                for field in search_fields:
                    if hasattr(model, field):
                        try:
                            filters.append(getattr(model, field).ilike(f'%{search}%'))
                        except Exception:
                            # skip invalid fields
                            pass

            # Optional brand lookup: expects a dict {'model': BrandModel, 'name_field': 'name', 'id_field': 'idBrand'}
            if brand_lookup and isinstance(brand_lookup, dict):
                try:
                    brand_model = brand_lookup.get('model')
                    name_field = brand_lookup.get('name_field')
                    id_field = brand_lookup.get('id_field')
                    if brand_model and name_field and id_field:
                        brand_q = brand_model.query.filter(getattr(brand_model, name_field).ilike(f'%{search}%'))
                        brand_ids = [getattr(b, id_field) for b in brand_q.all()]
                        if hasattr(model, id_field):
                            filters.append(getattr(model, id_field).in_(brand_ids))
                except Exception:
                    # best-effort: ignore brand lookup failures
                    pass

            if filters:
                query = query.filter(db_or(*filters))

        if type_filter and hasattr(model, 'idType'):
            query = query.filter(model.idType == type_filter)

        if brand_filter and hasattr(model, 'idBrand'):
            query = query.filter(model.idBrand == brand_filter)

        if category_filter and hasattr(model, 'idCategory'):
            query = query.filter(model.idCategory == category_filter)

        if min_price is not None and hasattr(model, 'dailyRate'):
            query = query.filter(model.dailyRate >= min_price)
        if max_price is not None and hasattr(model, 'dailyRate'):
            query = query.filter(model.dailyRate <= max_price)

        if capacity_filter and hasattr(model, 'capacity'):
            query = query.filter(model.capacity >= capacity_filter)

        # Apply ordering if requested and supported by the model
        try:
            if order_by:
                # price ordering
                if order_by in ('price_asc', 'price_desc') and hasattr(model, 'dailyRate'):
                    query = query.order_by(model.dailyRate.asc() if order_by == 'price_asc' else model.dailyRate.desc())
                # type/name ordering (string fields)
                elif order_by in ('type_asc', 'type_desc'):
                    if hasattr(model, 'type'):
                        col = getattr(model, 'type')
                        query = query.order_by(col.asc() if order_by == 'type_asc' else col.desc())
                    elif hasattr(model, 'name'):
                        col = getattr(model, 'name')
                        query = query.order_by(col.asc() if order_by == 'type_asc' else col.desc())
                    elif hasattr(model, 'model'):
                        col = getattr(model, 'model')
                        query = query.order_by(col.asc() if order_by == 'type_asc' else col.desc())
                    elif hasattr(model, 'idType'):
                        col = getattr(model, 'idType')
                        query = query.order_by(col.asc() if order_by == 'type_asc' else col.desc())
        except Exception:
            # ignore ordering failures
            pass

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        # Filter unavailable items in the current page based on the provided interval. Note: this only filters items in the current page, which may reduce the actual number shown.
        data = []
        for o in pagination.items:
            try:
                # If an interval is requested, validate availability and fill the `available` field in the vehicle's dictionary.
                od = o.to_dict()
                # Only perform reservation-availability checks when the
                # user supplied an explicit date/time filter. When no
                # date is provided we avoid treating the implicit
                # "now..now+1d" interval as a hard exclusion so
                # search results still show matching vehicles (they
                # will be marked unavailable in the UI instead).
                if hasattr(o, 'is_available'):
                    try:
                        # If the user provided any explicit date/time
                        # filters, calculate availability for that interval
                        # and leave unavailable items out of the results.
                        if start_raw or end_raw or start_time_raw or end_time_raw:
                            from datetime import datetime, time
                            from utils import parse_time

                            now_dt = datetime.now()

                            # Determine sensible defaults for start/end datetimes
                            if not start_date and not end_date:
                                start_arg = now_dt
                                end_arg = now_dt + timedelta(days=1)
                            else:
                                sd = start_date or date.today()
                                ed = end_date or (sd + timedelta(days=1))
                                start_arg = datetime.combine(sd, time.min)
                                end_arg = datetime.combine(ed, time.max)
                                if not start_time_raw and sd == date.today():
                                    start_arg = datetime.combine(sd, now_dt.time())

                            # If explicit times are provided, override the defaults
                            try:
                                if start_time_raw:
                                    st = parse_time(start_time_raw)
                                    sd = start_date or date.today()
                                    start_arg = datetime.combine(sd, st)
                            except Exception:
                                pass
                            try:
                                if end_time_raw:
                                    et = parse_time(end_time_raw)
                                    ed = end_date or (start_date or date.today()) + timedelta(days=1)
                                    end_arg = datetime.combine(ed, et)
                            except Exception:
                                pass

                            od['available'] = o.is_available(start_arg, end_arg)
                            if not od['available']:
                                # when dates provided, skip unavailable vehicles
                                continue
                        else:
                            # No date filters -> don't perform reservation overlap
                            # exclusion. Still expose `available=True` so the
                            # template can render the correct state.
                            od['available'] = True
                    except Exception as e:
                        # In case of error when validating availability, skip the vehicle
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
            'startTime': start_time_raw,
            'endTime': end_time_raw,
            'type_filter': type_filter,
            'category_filter': category_filter,
            'min_price': min_price,
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
