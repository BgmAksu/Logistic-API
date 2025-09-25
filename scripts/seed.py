from __future__ import annotations

import random
from datetime import date, datetime, timedelta

from faker import Faker
from sqlalchemy import func, select, text

from app import models
from app.db import SessionLocal

fake = Faker()


def ensure_geom(db):
    # Backfill geom from lat/lon for all addresses
    db.execute(
        text(
            "UPDATE addresses "
            "SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326) "
            "WHERE lat IS NOT NULL AND lon IS NOT NULL AND geom IS NULL"
        )
    )
    db.commit()


def mk_address(city, lat, lon):
    return models.Address(
        name=fake.company(),
        line1=fake.street_address(),
        line2=None,
        city=city,
        zip_code=fake.postcode(),
        country_code="NL",
        lat=lat,
        lon=lon,
    )


def run():
    db = SessionLocal()
    try:
        # Addresses (Amsterdam / Rotterdam / Utrecht area)
        if db.scalar(select(func.count(models.Address.id))) < 6:
            addrs = [
                mk_address("Amsterdam", 52.372, 4.900),
                mk_address("Amsterdam", 52.368, 4.903),
                mk_address("Rotterdam", 51.922, 4.479),
                mk_address("Rotterdam", 51.928, 4.490),
                mk_address("Utrecht", 52.092, 5.119),
                mk_address("Utrecht", 52.101, 5.123),
            ]
            db.add_all(addrs)
            db.commit()

        ensure_geom(db)

        # Depots
        if db.scalar(select(func.count(models.Depot.id))) == 0:
            addr_ids = [a.id for a in db.execute(select(models.Address)).scalars().all()]
            depots = [
                models.Depot(name="AMS Depot", address_id=addr_ids[0]),
                models.Depot(name="RTM Depot", address_id=addr_ids[2]),
                models.Depot(name="UTC Depot", address_id=addr_ids[4]),
            ]
            db.add_all(depots)
            db.commit()

        # Drivers & Vehicles
        if db.scalar(select(func.count(models.Driver.id))) == 0:
            depots = db.execute(select(models.Depot)).scalars().all()
            for d in depots:
                for _i in range(2):
                    db.add(models.Driver(name=fake.name(), email=fake.email(), depot_id=d.id))
                for _i in range(2):
                    db.add(
                        models.Vehicle(
                            plate=f"{d.name[:3].upper()}-{fake.pyint(100,999)}",
                            capacity_kg=1200,
                            capacity_dm3=6000,
                            depot_id=d.id,
                        )
                    )
            db.commit()

        # Shipments & Parcels
        if db.scalar(select(func.count(models.Shipment.id))) == 0:
            addr = db.execute(select(models.Address)).scalars().all()
            for i in range(20):
                sender = random.choice(addr)
                recipient = random.choice(addr)
                shp = models.Shipment(
                    reference=f"REF-{1000+i}",
                    service_level=random.choice(["STD", "EXP"]),
                    status=random.choice(["CREATED", "IN_TRANSIT"]),
                    sender_address_id=sender.id,
                    recipient_address_id=recipient.id,
                    planned_delivery_date=date.today() + timedelta(days=random.randint(0, 2)),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(shp)
                db.flush()
                # 1-3 parcels
                for j in range(random.randint(1, 3)):
                    db.add(
                        models.Parcel(
                            shipment_id=shp.id,
                            barcode=f"PKG-{i:04d}-{j}",
                            weight_kg=round(random.uniform(0.5, 10.0), 2),
                            volume_dm3=round(random.uniform(5, 50), 1),
                        )
                    )
            db.commit()

        # Tracking events (some delivered)
        parcels = db.execute(select(models.Parcel)).scalars().all()
        for p in parcels[:10]:
            ev1 = models.TrackingEvent(parcel_id=p.id, code="COLLECTED", description="Picked up")
            ev2 = models.TrackingEvent(parcel_id=p.id, code="DELIVERED", description="Delivered")
            db.add_all([ev1, ev2])
            p.shipment.status = "DELIVERED"
            p.shipment.delivered_at = datetime.utcnow()
        db.commit()

        # Simple route with stops (for route-length)
        if db.scalar(select(func.count(models.Route.id))) == 0:
            depots = db.execute(select(models.Depot)).scalars().all()
            vehicles = db.execute(select(models.Vehicle)).scalars().all()
            drivers = db.execute(select(models.Driver)).scalars().all()
            addr = db.execute(select(models.Address)).scalars().all()

            r = models.Route(
                depot_id=depots[0].id,
                vehicle_id=vehicles[0].id,
                driver_id=drivers[0].id,
                route_date=date.today(),
                created_at=datetime.utcnow(),
            )
            db.add(r)
            db.flush()
            seq = 1
            for a in random.sample(addr, 4):
                db.add(
                    models.Stop(
                        route_id=r.id,
                        sequence=seq,
                        stop_type="DELIVERY",
                        address_id=a.id,
                        planned_time=datetime.utcnow() + timedelta(minutes=15 * seq),
                    )
                )
                seq += 1
            db.commit()

        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
