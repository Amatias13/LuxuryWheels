from datetime import date, timedelta
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
    isActive = db.Column(db.Integer, default=1)
    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updatedAt = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

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
        - existe uma reserva confirmada/pendente que se sobrepoe ao intervalo solicitado

        Comportamento:
        - Se `start_date` e `end_date` forem fornecidos, `isActive` é ignorado
          (disponibilidade é determinada por sobreposição de reservas e
          checks técnicos como revisão/legalização). Isto permite editar uma
          reserva existente usando `exclude_reservation_id` sem que o campo
          `isActive` bloqueie a operação.
        - Se não forem fornecidas datas, `isActive` é respeitado para indicar
          se o veículo está no catálogo ativo.
        """
        today = date.today()
        # Technical checks always apply
        if self.nextRevisionDate and self.nextRevisionDate < today:
            return False
        if self.lastLegalizationDate and self.lastLegalizationDate < today - timedelta(
            days=365
        ):
            return False

        # If dates provided, determine availability based on reservations overlap
        # (ignore `isActive` in this case to allow editing existing reservations).
        if start_date and end_date:
            if has_reservation_overlap(self.idVehicle, start_date, end_date, exclude_reservation_id=exclude_reservation_id):
                return False
            return True

        # No dates provided: respect isActive as catalogue flag
        if not self.isActive:
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
            "isActive": self.isActive,
            # Por omissão, considerar disponível (detalhes por data são
            # avaliados quando o intervalo é fornecido nas rotas).
            "available": True,
        }
