from __future__ import annotations

from datetime import date, datetime

from geoalchemy2 import Geography
from sqlalchemy import (
    Date,
    DateTime,
    Double,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


# ---------- Reference data ----------
class Address(Base):
    """Stores sender/recipient/depot addresses."""

    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String(100))
    line1: Mapped[str] = mapped_column(String(255))
    line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    zip_code: Mapped[str] = mapped_column(String(20))
    country_code: Mapped[str] = mapped_column(String(2))
    lat: Mapped[float | None] = mapped_column(Double)
    lon: Mapped[float | None] = mapped_column(Double)

    # Geodesic point; use geography for meter-based distances on Earth
    geom: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=True
    )


class Depot(Base):
    """Operational depot / facility."""

    __tablename__ = "depots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    address_id: Mapped[int | None] = mapped_column(ForeignKey("addresses.id"))

    address: Mapped[Address | None] = relationship()
    drivers: Mapped[list[Driver]] = relationship(back_populates="depot")
    vehicles: Mapped[list[Vehicle]] = relationship(back_populates="depot")


class Driver(Base):
    """Driver assigned to a depot."""

    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30))
    depot_id: Mapped[int | None] = mapped_column(ForeignKey("depots.id"))

    depot: Mapped[Depot | None] = relationship(back_populates="drivers")


class Vehicle(Base):
    """Vehicle with optional capacity hints."""

    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plate: Mapped[str] = mapped_column(String(20), unique=True)
    capacity_kg: Mapped[int | None] = mapped_column(Integer)
    capacity_dm3: Mapped[int | None] = mapped_column(Integer)
    depot_id: Mapped[int | None] = mapped_column(ForeignKey("depots.id"))

    depot: Mapped[Depot | None] = relationship(back_populates="vehicles")


# ---------- Shipments & parcels ----------
ShipmentStatus = Enum("CREATED", "IN_TRANSIT", "DELIVERED", name="shipment_status")


class Shipment(Base):
    """Customer shipment; may contain multiple parcels."""

    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reference: Mapped[str] = mapped_column(String(64), index=True)
    service_level: Mapped[str] = mapped_column(String(20))  # e.g., STD/EXP
    status: Mapped[str] = mapped_column(ShipmentStatus, default="CREATED", index=True)

    sender_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    recipient_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))

    planned_delivery_date: Mapped[date | None] = mapped_column(Date)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sender: Mapped[Address] = relationship(foreign_keys=[sender_address_id])
    recipient: Mapped[Address] = relationship(foreign_keys=[recipient_address_id])
    parcels: Mapped[list[Parcel]] = relationship(back_populates="shipment")


class Parcel(Base):
    """Physical parcel belonging to a shipment."""

    __tablename__ = "parcels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shipment_id: Mapped[int] = mapped_column(ForeignKey("shipments.id"))
    barcode: Mapped[str] = mapped_column(String(64), index=True)
    weight_kg: Mapped[float | None] = mapped_column(Double)
    volume_dm3: Mapped[float | None] = mapped_column(Double)

    shipment: Mapped[Shipment] = relationship(back_populates="parcels")
    events: Mapped[list[TrackingEvent]] = relationship(back_populates="parcel")


Index("ix_parcels_shipment_barcode", Parcel.shipment_id, Parcel.barcode, unique=True)


# ---------- Routes & stops ----------
StopType = Enum("PICKUP", "DELIVERY", name="stop_type")


class Route(Base):
    """Daily route operated by a depot/driver/vehicle."""

    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    depot_id: Mapped[int] = mapped_column(ForeignKey("depots.id"))
    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("vehicles.id"))
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"))
    route_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Stop(Base):
    """A sequenced stop in a route, optionally bound to a shipment."""

    __tablename__ = "stops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    sequence: Mapped[int] = mapped_column(Integer, index=True)
    stop_type: Mapped[str] = mapped_column(StopType)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    planned_time: Mapped[datetime | None] = mapped_column(DateTime)
    actual_time: Mapped[datetime | None] = mapped_column(DateTime)
    shipment_id: Mapped[int | None] = mapped_column(ForeignKey("shipments.id"))


Index("ix_stops_route_seq", Stop.route_id, Stop.sequence, unique=True)


# ---------- Tracking events ----------
class TrackingEvent(Base):
    """Event stream for a parcel (e.g., COLLECTED, IN_DEPOT, DELIVERED)."""

    __tablename__ = "tracking_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parcel_id: Mapped[int] = mapped_column(ForeignKey("parcels.id"))
    code: Mapped[str] = mapped_column(String(32), index=True)
    description: Mapped[str | None] = mapped_column(String(255))
    event_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lat: Mapped[float | None] = mapped_column(Double)
    lon: Mapped[float | None] = mapped_column(Double)
    location_name: Mapped[str | None] = mapped_column(String(100))

    parcel: Mapped[Parcel] = relationship(back_populates="events")
