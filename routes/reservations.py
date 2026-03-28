from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models import (
    Reservation,
    Vehicle,
    PaymentMethod,
    ReservationExtra,
    Testimonial,
    Payment,
)

bp = Blueprint("reservations", __name__)


@bp.route("/reservation", methods=["GET"])
def reservation():
    vehicle_id = request.args.get("vehicle_id")
    vehicle = Vehicle.query.get(vehicle_id) if vehicle_id else None
    # Se foi fornecido um id mas não existe veículo correspondente
    if vehicle_id and not vehicle:
        flash("Veículo não encontrado.", "modal-error")
        return redirect(url_for("vehicles.list_view"))
    # If a specific vehicle was requested but it's not available, block access
    if vehicle_id and vehicle:
        try:
            if not vehicle.is_available():
                flash("Veículo indisponível.", "modal-error")
                return redirect(url_for("vehicles.list_view"))
        except Exception:
            # if availability check errors, be conservative and block
            flash("Veículo indisponível.", "modal-error")
            return redirect(url_for("vehicles.list_view"))
    payment_methods = [p.to_dict() for p in PaymentMethod.query.all()]
    extras = [e.to_dict() for e in ReservationExtra.query.filter_by(isActive=1).all()]
    vehicles = [v.to_dict() for v in Vehicle.query.filter_by(isActive=1).all()]
    testimonials = [t.to_dict() for t in Testimonial.query.filter_by(isActive=1).all()]
    return render_template(
        "reservation.html",
        title="Reserva",
        vehicle=vehicle,
        payment_methods=payment_methods,
        extras=extras,
        vehicles=vehicles,
        testimonials=testimonials,
    )


@bp.route("/my-reservations")
def my_reservations():
    if "user_id" not in session:
        flash("Faça login para ver as suas reservas", "modal-error")
        return redirect(url_for("users.login"))

    reservations = Reservation.query.filter_by(idUser=session["user_id"]).all()
    data = []
    for r in reservations:
        d = r.to_dict()
        vehicle = Vehicle.query.get(r.idVehicle)
        d["vehicle_model"] = vehicle.model if vehicle else "N/A"
        d["vehicle_image"] = vehicle.imageUrl if vehicle else None
        d["vehicle_brand"] = vehicle.brand.name if vehicle and vehicle.brand else ""
        # estado da reserva em texto
        statuses = {1: "Pendente", 2: "Confirmada", 3: "Cancelada", 4: "Concluída"}
        d["status_name"] = statuses.get(r.idReservationStatus, "Pendente")
        d["can_edit"] = r.idReservationStatus not in (3, 4)
        data.append(d)

    return render_template(
        "my_reservations.html", title="As minhas reservas", reservations=data
    )


@bp.route("/reserve", methods=["POST"])
def reserve():
    if "user_id" not in session:
        flash("Faça login para fazer uma reserva", "modal-error")
        return redirect(url_for("users.login"))
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
                except Exception:
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
        return redirect(url_for("users.login"))
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
        return redirect(url_for("users.login"))

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
