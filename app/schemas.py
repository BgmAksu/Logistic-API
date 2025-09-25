# Pydantic models used for request/response validation.

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- Address ----------
class AddressIn(BaseModel):
    name: str | None = None
    line1: str
    line2: str | None = None
    city: str
    zip_code: str
    country_code: str = Field(min_length=2, max_length=2)
    lat: float | None = None
    lon: float | None = None


class AddressOut(AddressIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Shipment ----------
class ShipmentIn(BaseModel):
    reference: str
    service_level: str
    status: str = "CREATED"
    sender_address_id: int
    recipient_address_id: int
    planned_delivery_date: date | None = None


class ShipmentOut(BaseModel):
    id: int
    reference: str
    service_level: str
    status: str
    planned_delivery_date: date | None = None
    delivered_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ---------- Parcel ----------
class ParcelIn(BaseModel):
    shipment_id: int
    barcode: str
    weight_kg: float | None = None
    volume_dm3: float | None = None


class ParcelOut(BaseModel):
    id: int
    shipment_id: int
    barcode: str
    weight_kg: float | None = None
    volume_dm3: float | None = None
    model_config = ConfigDict(from_attributes=True)


# ---------- Tracking ----------
class TrackingEventIn(BaseModel):
    parcel_id: int
    code: str  # e.g., COLLECTED, IN_DEPOT, OUT_FOR_DELIVERY, DELIVERED
    description: str | None = None
    event_time: datetime | None = None
    lat: float | None = None
    lon: float | None = None
    location_name: str | None = None


class TrackingEventOut(TrackingEventIn):
    id: int
    model_config = ConfigDict(from_attributes=True)
