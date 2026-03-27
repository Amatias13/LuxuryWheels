from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models import Reservation, Vehicle

bp = Blueprint("reservations", __name__)

@bp.route("/reservation", methods=["GET"])
def reservation():
    vehicle_id = request.args.get("vehicle_id")
    vehicle = Vehicle.query.get(vehicle_id) if vehicle_id else None
    return render_template("reservation.html", title="Reserva", vehicle=vehicle)


@bp.route("/my-reservations")
def my_reservations():
    if "user_id" not in session:
        flash("Faca login para ver as suas reservas", "error")
        return redirect(url_for("users.login"))
    reservations = Reservation.query.filter_by(idUser=session["user_id"]).all()
    return render_template(
        "my_reservations.html", title="As minhas reservas", reservations=reservations
    )


@bp.route("/reserve", methods=["POST"])
def reserve():
    if "user_id" not in session:
        flash("Faca login para fazer uma reserva", "error")
        return redirect(url_for("users.login"))
    try:
        data = {
            "idUser": session["user_id"],
            "idVehicle": int(request.form.get("vehicle_id")),
            "startDate": request.form.get("startDate"),
            "endDate": request.form.get("endDate"),
        }
        reservation = Reservation.create(data)
        db.session.add(reservation)
        db.session.commit()
        flash("Reserva criada com sucesso!")
        return redirect(url_for("reservations.my_reservations"))
    except (ValueError, TypeError) as e:
        flash(str(e) or "Erro ao criar reserva", "error")
        return redirect(
            url_for("reservations.reservation")
            + f"?vehicle_id={request.form.get('vehicle_id')}"
        )
