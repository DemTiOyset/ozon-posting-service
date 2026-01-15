from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    String, Integer, DateTime, Boolean,
    Index, text, DOUBLE
)
from sqlalchemy.orm import Mapped, mapped_column

from application.db import Base


class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    posting_number: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    seller_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    offer_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    commission_amount: Mapped[float] = mapped_column(
        DOUBLE,
        nullable=False,
    )

    commission_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    payout: Mapped[float] = mapped_column(
        DOUBLE,
        nullable=False,
    )

    price: Mapped[float] = mapped_column(
        DOUBLE,
        nullable=False,
    )

    customer_price: Mapped[float] = mapped_column(
        DOUBLE,
        nullable=False,
    )

    total_discount_percent: Mapped[float] = mapped_column(
        DOUBLE,
        nullable=False,
    )

    total_discount_value: Mapped[float] = mapped_column(
        DOUBLE,
        nullable=False,
    )

    sku: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    last_event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    shipment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    delivery_date_begin: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    delivery_date_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    is_finished: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    is_returned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    __table_args__ = (
        Index("ix_order_lines_order", "posting_number"),
    )

