from datetime import date, timedelta, datetime, time
from database import db
from models.Status import ReservationStates
from models.helpers import has_reservation_overlap, has_reservation_on


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
    km = db.Column(db.Integer, nullable=False, server_default="0")
    imageUrl = db.Column(db.String)
    lastRevisionDate = db.Column(db.Date, nullable=False)
    nextRevisionDate = db.Column(db.Date, nullable=False)
    lastLegalizationDate = db.Column(db.Date, nullable=False)
    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updatedAt = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # Relationships to access brand/category/type names directly in templates and APIs without extra queries
    brand = db.relationship("VehicleBrand", foreign_keys=[idBrand], lazy="joined")
    category = db.relationship(
        "VehicleCategory", foreign_keys=[idCategory], lazy="joined"
    )
    vtype = db.relationship("VehicleType", foreign_keys=[idType], lazy="joined")

    def is_available(self, start_date=None, end_date=None, exclude_reservation_id=None):
        """Verifica se o veiculo esta disponivel.
        Indisponivel se:
        - nextRevisionDate < hoje
        - lastLegalizationDate < hoje - 1 ano
        - existe uma reserva confirmada/pendente que se sobrepoe ao intervalo solicitado

        Comportamento:
        - Se `start_date` e `end_date` forem fornecidos
          a disponibilidade é determinada por sobreposição de reservas e
          checks técnicos como revisão/legalização. Isto permite editar uma
          reserva existente usando `exclude_reservation_id` para ignorar a própria reserva na validação de disponibilidade.
        - Se não forem fornecidas datas, a disponibilidade é determinada apenas pelos checks técnicos.
        """
        today = date.today()
        # Technical checks always apply
        if self.nextRevisionDate and self.nextRevisionDate < today:
            return False
        if self.lastLegalizationDate and self.lastLegalizationDate < today - timedelta(
            days=365
        ):
            return False
        # If dates/datetimes provided, determine availability based on reservations overlap.
        # Accept `date` or `datetime` objects. When no explicit dates are provided,
        # default to today..today+1.
        from datetime import datetime
        if not start_date or not end_date:
            start_dt = datetime.combine(today, time.min)
            end_dt = start_dt + timedelta(days=1)
        else:
            # normalize inputs to datetimes
            if isinstance(start_date, datetime):
                start_dt = start_date
            else:
                start_dt = datetime.combine(start_date, time.min)
            if isinstance(end_date, datetime):
                end_dt = end_date
            else:
                end_dt = datetime.combine(end_date, time.min)

        if has_reservation_overlap(
            self.idVehicle, start_dt, end_dt, exclude_reservation_id=exclude_reservation_id
        ):
            return False
        return True

    def has_reservation_between(self, start_date, end_date, ignore_statuses=(3,)):
        """Retorna True se existir uma reserva (não em estados ignorados) que se sobreponha ao intervalo fornecido."""
        return has_reservation_overlap(self.idVehicle, start_date, end_date, exclude_reservation_id=None, ignore_statuses=ignore_statuses)

    def has_reservation_on(self, day):
        """Verifica se existe alguma reserva que inclua o dia (date object)."""
        return has_reservation_on(self.idVehicle, day)

    def to_dict(self):
        return {
            "id": self.idVehicle,
            "model": self.model,
            "brand": self.brand.name if self.brand else None,
            "category": self.category.name if self.category else None,
            "type": self.vtype.name if self.vtype else None,
            "dailyRate": self.dailyRate,
            "capacity": self.capacity,
            "km": int(self.km) if getattr(self, "km", None) is not None else 0,
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
            
            # By default, consider available (date-specific details are evaluated when interval is provided in routes).
            "available": True,
        }
