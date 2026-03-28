from database import db


class PaymentMethod(db.Model):
    __tablename__ = "Payment_Method"
    idPaymentMethod = db.Column(db.Integer, primary_key=True)
    methodName = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {"id": self.idPaymentMethod, "methodName": self.methodName}
