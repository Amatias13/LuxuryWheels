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
    lastRevisionDate = db.Column(db.Date, nullable=False)
    nextRevisionDate = db.Column(db.Date, nullable=False)
    lastLegalizationDate = db.Column(db.Date, nullable=False)
    isActive = db.Column(db.Integer, default=1)
    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relacoes para aceder a nome da marca, categoria e tipo diretamente
    brand = db.relationship("VehicleBrand", foreign_keys=[idBrand], lazy="joined")
    category = db.relationship(
        "VehicleCategory", foreign_keys=[idCategory], lazy="joined"
    )
    vtype = db.relationship("VehicleType", foreign_keys=[idType], lazy="joined")

    def is_available(self, start_date=None, end_date=None, exclude_reservation_id=None):
        """Verifica se o veiculo esta disponivel.
        Indisponivel se:
        - isActive == 0 (reservado)
        - nextRevisionDate < hoje
        - lastLegalizationDate < hoje - 1 ano
        - existe uma reserva confirmada/pendente que se sobrepoe ao intervalo solicitado (se fornecido)
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

        # Se não forem fornecidas datas, apenas valida checks gerais acima
        if not (start_date and end_date):
            return True

        # Checar sobreposição com reservas existentes (ignorar reservas canceladas - status 3)
        from models.Reservation import Reservation

        # start_date/end_date devem ser date objects
        for r in (
            Reservation.query.filter_by(idVehicle=self.idVehicle)
            .filter(Reservation.idReservationStatus != 3)
            .all()
        ):
            # ignorar reserva corrente se pedida
            if exclude_reservation_id and getattr(r, 'idReservation', None) == exclude_reservation_id:
                continue
            # existe sobreposição se sd < r.endDate e ed > r.startDate
            if start_date < r.endDate and end_date > r.startDate:
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
