from datetime import date, timedelta
from database import db


class Vehicle(db.Model):
    __tablename__ = "Vehicle"
    idVehicle = db.Column(db.Integer, primary_key=True)
    idBrand = db.Column(
        db.Integer, db.ForeignKey("Vehicle_Brand.idBrand"), nullable=False
    )
    model = db.Column(db.String, nullable=False)
    idCategory = db.Column(
        db.Integer, db.ForeignKey("Vehicle_Category.idCategory"), nullable=False
    )
    idType = db.Column(db.Integer, db.ForeignKey("Vehicle_Type.idType"), nullable=False)
    dailyRate = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    imageUrl = db.Column(db.String)
    lastRevisionDate = db.Column(db.Date)
    nextRevisionDate = db.Column(db.Date)
    lastLegalizationDate = db.Column(db.Date)
    isActive = db.Column(db.Integer, default=1)
    createdAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)

    # Relacoes para aceder a nome da marca, categoria e tipo diretamente
    brand = db.relationship("VehicleBrand", foreign_keys=[idBrand], lazy="joined")
    category = db.relationship(
        "VehicleCategory", foreign_keys=[idCategory], lazy="joined"
    )
    vtype = db.relationship("VehicleType", foreign_keys=[idType], lazy="joined")

    def is_available(self):
        """T4/T5: verifica se o veiculo esta disponivel.
        Indisponivel se:
        - isActive == 0 (reservado)
        - nextRevisionDate < hoje
        - lastLegalizationDate < hoje - 1 ano
        """
        today = date.today()
        if not self.isActive:
            return False
        if self.nextRevisionDate and self.nextRevisionDate < today:
            return False
        if self.lastLegalizationDate and self.lastLegalizationDate < today - timedelta(
            days=365
        ):
            return False
        return True

    def to_dict(self):
        return {
            "id": self.idVehicle,
            "model": self.model,
            "brand": self.brand.name if self.brand else None,
            "category": self.category.name if self.category else None,
            "type": self.vtype.name if self.vtype else None,
            "dailyRate": self.dailyRate,
            "capacity": self.capacity,
            "imageUrl": self.imageUrl,
            "lastRevisionDate": (
                str(self.lastRevisionDate) if self.lastRevisionDate else None
            ),
            "nextRevisionDate": (
                str(self.nextRevisionDate) if self.nextRevisionDate else None
            ),
            "lastLegalizationDate": (
                str(self.lastLegalizationDate) if self.lastLegalizationDate else None
            ),
            "isActive": self.isActive,
            "available": self.is_available(),
        }
