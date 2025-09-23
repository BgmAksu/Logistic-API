# Pydantic models used for request/response validation.

from __future__ import annotations
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


# ---------- Address ----------
class AddressIn(BaseModel):
    name: Optional[str] = None
    line1: str
    line2: Optional[str] = None
    city: str
    zip_code: str
    country_code: str = Field(min_length=2, max_length=2)
    lat: Optional[float] = None
    lon: Optional[float] = None

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
    planned_delivery_date: Optional[date] = None

class ShipmentOut(BaseModel):
    id: int
    reference: str
    service_level: str
    status: str
    planned_delivery_date: Optional[date] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ---------- Parcel ----------
class ParcelIn(BaseModel):
    shipment_id: int
    barcode: str
    weight_kg: Optional[float] = None
    volume_dm3: Optional[float] = None

class ParcelOut(BaseModel):
    id: int
    shipment_id: int
    barcode: str
    weight_kg: Optional[float] = None
    volume_dm3: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


# ---------- Tracking ----------
class TrackingEventIn(BaseModel):
    parcel_id: int
    code: str               # e.g., COLLECTED, IN_DEPOT, OUT_FOR_DELIVERY, DELIVERED
    description: Optional[str] = None
    event_time: Optional[datetime] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    location_name: Optional[str] = None

class TrackingEventOut(TrackingEventIn):
    id: int
    model_config = ConfigDict(from_attributes=True)