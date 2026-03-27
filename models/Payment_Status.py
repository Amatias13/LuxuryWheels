from database import db


class PaymentStatus(db.Model):
    __tablename__ = 'Payment_Status'
    idPaymentStatus = db.Column(db.Integer, primary_key=True)
    statusName = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {'id': self.idPaymentStatus, 'statusName': self.statusName}
