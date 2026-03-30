from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import logging
from database import db
from models import (
    Reservation,
    Vehicle,
    PaymentMethod,
    ReservationExtra,
    Testimonial,
    Payment,
)
from models.Status import ReservationStates

bp = Blueprint("reservations", __name__)


@bp.route("/reservation", methods=["GET"])
def reservation():
    vehicle_id = request.args.get("vehicle_id")
    vehicle = Vehicle.query.get(vehicle_id) if vehicle_id else None
    # Ler possíveis filtros de datas (ISO: YYYY-MM-DD)
    start_date = None
    end_date = None
    start_raw = request.args.get("startDate")
    end_raw = request.args.get("endDate")
    if start_raw and end_raw:
        try:
            from datetime import date

            start_date = date.fromisoformat(start_raw)
            end_date = date.fromisoformat(end_raw)
        except (ValueError, TypeError) as e:
            logging.debug("Invalid date filter provided: %s", e)
            start_date = None
            end_date = None
    # Se foi fornecido um id mas não existe veículo correspondente
    if vehicle_id and not vehicle:
        flash("Veículo não encontrado.", "modal-error")
        return redirect(url_for("vehicles.list_view"))
    # If a specific vehicle was requested but it's not available, block access
    if vehicle_id and vehicle:
        try:
            if not vehicle.is_available(start_date, end_date):
                flash("Veículo indisponível.", "modal-error")
                return redirect(url_for("vehicles.list_view"))
        except Exception as e:
            # if availability check errors, be conservative and block
            logging.exception("Error checking vehicle availability")
            flash("Veículo indisponível.", "modal-error")
            return redirect(url_for("vehicles.list_view"))
    # Disponibilidade do veículo (para controlar botão no template)
    vehicle_available = True
    if vehicle:
        try:
            vehicle_available = vehicle.is_available(start_date, end_date)
        except Exception as e:
            logging.exception("Error computing vehicle availability")
            vehicle_available = False
    payment_methods = [p.to_dict() for p in PaymentMethod.query.all()]
    extras = [e.to_dict() for e in ReservationExtra.query.filter_by(isActive=1).all()]
    # Listar apenas veículos ativos. Se datas forem fornecidas, filtrar
    # apenas veículos disponíveis nesse intervalo.
    vehicles_q = Vehicle.query.filter_by(isActive=1).all()
    vehicles = []
    for v in vehicles_q:
        try:
            if start_date and end_date:
                if not v.is_available(start_date, end_date):
                    continue
        except Exception as e:
            # Em caso de erro ao validar disponibilidade, pular o veículo
            logging.exception("Error validating vehicle availability for list")
            continue
        vehicles.append(v.to_dict())
    testimonials = [t.to_dict() for t in Testimonial.query.filter_by(isActive=1).all()]
    return render_template(
        "reservation.html",
        title="Reserva",
        vehicle=vehicle,
        payment_methods=payment_methods,
        extras=extras,
        vehicles=vehicles,
        startDate=start_raw,
        endDate=end_raw,
        testimonials=testimonials,
        vehicle_available=vehicle_available,
    )


@bp.route("/my-reservations")
def my_reservations():
    if "user_id" not in session:
        flash("Faça login para ver as suas reservas", "modal-error")
        return redirect(url_for("users.login", next=request.url))

    reservations = Reservation.query.filter_by(idUser=session["user_id"]).all()
    data = []
    for r in reservations:
        d = r.to_dict()
        vehicle = Vehicle.query.get(r.idVehicle)
        d["vehicle_model"] = vehicle.model if vehicle else "N/A"
        d["vehicle_image"] = vehicle.imageUrl if vehicle else None
        d["vehicle_brand"] = vehicle.brand.name if vehicle and vehicle.brand else ""
        # estado da reserva em texto (usar constantes centrais)
        statuses = {
            ReservationStates.PENDING: "Pendente",
            ReservationStates.CONFIRMED: "Confirmada",
            ReservationStates.CANCELLED: "Cancelada",
            ReservationStates.COMPLETED: "Concluída",
        }
        d["status_name"] = statuses.get(r.idReservationStatus, "Pendente")
        d["can_edit"] = r.idReservationStatus not in (
            ReservationStates.CANCELLED,
            ReservationStates.COMPLETED,
        )
        data.append(d)

    return render_template(
        "my_reservations.html", title="As minhas reservas", reservations=data
    )


@bp.route("/reserve", methods=["POST"])
def reserve():
    if "user_id" not in session:
        flash("Faça login para fazer uma reserva", "modal-error")
        return redirect(url_for("users.login", next=request.url))
    try:
        vehicle_id_str = request.form.get("vehicle_id")
        if not vehicle_id_str:
            raise ValueError("Veículo inválido")

        try:
            vehicle_id = int(vehicle_id_str)
        except (TypeError, ValueError):
            raise ValueError("Veículo inválido")

        data = {
            "idUser": session["user_id"],
            "idVehicle": vehicle_id,
            "startDate": request.form.get("startDate"),
            "endDate": request.form.get("endDate"),
        }
        payment_method_id = request.form.get("idPaymentMethod")
        # ler extras selecionados (lista)
        extras_selected = request.form.getlist("extras")

        if not data["startDate"] or not data["endDate"]:
            raise ValueError("Datas de início e fim são obrigatórias")
        if not payment_method_id:
            raise ValueError("Selecione um método de pagamento")

        # Criar reserva (inclui extras; marca veiculo como inativo - T4)
        reservation, vehicle, total_price = Reservation.create(
            data, extras=extras_selected
        )
        db.session.add(reservation)
        db.session.flush()  # obter o id da reserva antes do commit

        # Persistir extras selecionados (ligação reserva <-> extra)
        from models.Reservation_Extras_Link import ReservationExtrasLink
        from models.Reservation_Extra import ReservationExtra

        for ex_id in extras_selected:
            try:
                ex_id_int = int(ex_id)
            except (TypeError, ValueError):
                continue
            ex_obj = ReservationExtra.query.get(ex_id_int)
            if ex_obj:
                # calcular dias a partir da reserva criada
                try:
                    total_days = (reservation.endDate - reservation.startDate).days
                except (TypeError, AttributeError) as e:
                    logging.exception("Error computing total_days for extras link")
                    total_days = 0
                link = ReservationExtrasLink(
                    idReservation=reservation.idReservation,
                    idExtra=ex_obj.idExtra,
                    dailyPrice=ex_obj.dailyPrice,
                    totalPrice=(ex_obj.dailyPrice * total_days),
                )
                db.session.add(link)

        # Criar pagamento
        payment, reservation = Payment.create(
            reservation.idReservation, payment_method_id, total_price
        )
        db.session.add(payment)
        db.session.commit()

        flash(f"Reserva confirmada! Total: {total_price:.2f}€", "modal")
        return redirect(url_for("reservations.my_reservations"))

    except (ValueError, TypeError) as e:
        db.session.rollback()
        # show important errors in modal
        flash(str(e) or "Erro ao criar reserva", "modal-error")
        return redirect(
            url_for("reservations.reservation")
            + f"?vehicle_id={request.form.get('vehicle_id')}"
        )


@bp.route("/reservation/<int:rid>/cancel", methods=["POST"])
def cancel_reservation(rid):
    if "user_id" not in session:
        flash("Faça login para cancelar uma reserva", "modal-error")
        return redirect(url_for("users.login", next=request.url))
    try:
        reservation = Reservation.cancel(rid, session["user_id"])
        db.session.commit()
        flash("Reserva cancelada com sucesso.", "modal")
    except ValueError as e:
        flash(str(e), "modal-error")
    return redirect(url_for("reservations.my_reservations"))


@bp.route("/reservation/<int:rid>/edit", methods=["GET", "POST"])
def edit_reservation(rid):
    if "user_id" not in session:
        flash("Faça login para editar uma reserva", "modal-error")
        return redirect(url_for("users.login", next=request.url))

    reservation = Reservation.query.filter_by(
        idReservation=rid, idUser=session["user_id"]
    ).first_or_404()

    if request.method == "POST":
        try:
            updated = Reservation.update_dates(
                rid,
                session["user_id"],
                request.form.get("startDate"),
                request.form.get("endDate"),
            )
            db.session.commit()
            flash(f"Reserva atualizada! Novo total: {updated.totalPrice:.2f}€", "modal")
            return redirect(url_for("reservations.my_reservations"))
        except ValueError as e:
            flash(str(e), "modal-error")

    vehicle = Vehicle.query.get(reservation.idVehicle)
    return render_template(
        "edit_reservation.html",
        title="Editar Reserva",
        reservation=reservation,
        vehicle=vehicle,
    )
