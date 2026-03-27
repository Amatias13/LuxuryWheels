from database import db

class Payment(db.Model):
    __tablename__ = "Payment"
    idPayment = db.Column(db.Integer, primary_key=True)
    idReservation = db.Column(db.Integer, db.ForeignKey('Reservation.idReservation'), nullable=False)
    idPaymentMethod = db.Column(db.Integer, db.ForeignKey('Payment_Method.idPaymentMethod'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paymentDate = db.Column(db.DateTime, nullable=False)
    idPaymentStatus = db.Column(db.Integer, db.ForeignKey('Payment_Status.idPaymentStatus'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.idPayment,
            'reservation_id': self.idReservation,
            'payment_method_id': self.idPaymentMethod,
            'amount': self.amount,
            'paymentDate': str(self.paymentDate),
            'payment_status_id': self.idPaymentStatus
        }
