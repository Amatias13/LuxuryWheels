from database import db

class Payment(db.Model):
    __tablename__ = "Payment"
    idPayment = db.Column(db.Integer, primary_key=True)
    idReservation = db.Column(db.Integer, db.ForeignKey('Reservation.idReservation'), nullable=False)
    idPaymentMethod = db.Column(db.Integer, db.ForeignKey('Payment_Method.idPaymentMethod'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paymentDate = db.Column(db.DateTime, nullable=False)
    idPaymentStatus = db.Column(db.Integer, db.ForeignKey('Payment_Status.idPaymentStatus'), nullable=False)
