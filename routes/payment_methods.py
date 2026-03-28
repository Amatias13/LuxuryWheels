from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import PaymentMethod

bp = Blueprint("payment_methods", __name__)


@bp.route("/payment-methods", methods=["GET", "POST"])
def payment_methods():
    if request.method == "POST":
        name = request.form.get("methodName")
        if not name:
            flash("Nome do método é obrigatório", "modal-error")
            return redirect(url_for("payment_methods.payment_methods"))
        if PaymentMethod.query.filter_by(methodName=name).first():
            flash("Método já existe", "modal-error")
            return redirect(url_for("payment_methods.payment_methods"))
        pm = PaymentMethod(methodName=name)
        db.session.add(pm)
        db.session.commit()
        flash("Método de pagamento adicionado", "modal")
        return redirect(url_for("payment_methods.payment_methods"))

    methods = [m.to_dict() for m in PaymentMethod.query.all()]
    return render_template("payment_methods.html", methods=methods)


@bp.route("/payment-methods/<int:pm_id>/update", methods=["POST"])
def update_payment_method(pm_id):
    pm = PaymentMethod.query.get_or_404(pm_id)
    new_name = request.form.get("methodName")
    if not new_name:
        flash("Nome do método é obrigatório", "modal-error")
        return redirect(url_for("payment_methods.payment_methods"))
    existing = PaymentMethod.query.filter_by(methodName=new_name).first()
    if existing and existing.idPaymentMethod != pm.idPaymentMethod:
        flash("Já existe um método com esse nome", "modal-error")
        return redirect(url_for("payment_methods.payment_methods"))
    pm.methodName = new_name
    db.session.commit()
    flash("Método atualizado", "modal")
    return redirect(url_for("payment_methods.payment_methods"))


@bp.route("/payment-methods/<int:pm_id>/delete", methods=["POST"])
def delete_payment_method(pm_id):
    pm = PaymentMethod.query.get_or_404(pm_id)
    db.session.delete(pm)
    db.session.commit()
    flash("Método eliminado", "modal")
    return redirect(url_for("payment_methods.payment_methods"))
