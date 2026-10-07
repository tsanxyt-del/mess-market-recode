"""Market record document shape (MongoDB, PyMongo — no ORM).

Collection: market_records
Fields: purchase_date(datetime), year, month, item_id, item_name,
        quantity, unit, rate, total, bill_file, remark,
        created_at, updated_at, deleted_at
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MarketRecord:
    purchase_date: datetime
    item_id: str
    item_name: str
    quantity: float
    unit: str
    rate: float
    total: float = 0.0
    bill_file: str = ""
    remark: str = ""
    year: int = 0
    month: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def __post_init__(self):
        if self.purchase_date:
            self.year = self.purchase_date.year
            self.month = self.purchase_date.month
        # Backend is source of truth for total — never trust browser value.
        self.total = round(float(self.quantity) * float(self.rate), 2)

    def to_doc(self):
        return {
            "purchase_date": self.purchase_date,
            "year": self.year,
            "month": self.month,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "quantity": float(self.quantity),
            "unit": self.unit,
            "rate": float(self.rate),
            "total": float(self.total),
            "bill_file": self.bill_file or "",
            "remark": self.remark or "",
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at,
        }
