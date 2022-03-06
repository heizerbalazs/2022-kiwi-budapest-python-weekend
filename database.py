from datetime import timedelta
from sqlalchemy.pool import NullPool
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence, Column, Integer, String, TEXT, FLOAT, BigInteger
import models
Base = declarative_base()

USER = 'balazs_heizer'
PASSWORD = '4b83d16639c3438da6583529d90864df'
SERVER = 'sql.pythonweekend.skypicker.com'
DBNAME = 'pythonweekend'

DATABASE_URL = (
    f"postgresql://{USER}:{PASSWORD}@{SERVER}/{DBNAME}"
    f"?application_name={USER}_local_dev"
)


class Journey(Base):
    # name of the table
    __tablename__ = f"journeys_{USER}"
    id = Column(Integer, primary_key=True)
    source_id = Column(BigInteger)
    source = Column(TEXT)
    destination_id = Column(BigInteger)
    destination = Column(TEXT)
    departure_datetime = Column(TIMESTAMP)
    arrival_datetime = Column(TIMESTAMP)
    carrier = Column(TEXT)
    vehicle_type = Column(TEXT)
    price = Column(FLOAT)
    currency = Column(String(3))
    free_seats = Column(Integer)
    carrier = Column(TEXT)


# class CommonJourney(Base):
#     # name of the table
#     __tablename__ = "journeys"
#     id = Column(Integer, primary_key=True)
#     source = Column(TEXT)
#     destination = Column(TEXT)
#     departure_datetime = Column(TIMESTAMP)
#     arrival_datetime = Column(TIMESTAMP)
#     carrier = Column(TEXT)
#     vehicle_type = Column(TEXT)
#     price = Column(FLOAT)
#     currency = Column(String(3))
#     free_seats: Column(Integer)
#     carrier: Column(TEXT)


# echo=True shows debug information
# NullPool closes unused connections immediately
engine = create_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool
)

Base.metadata.create_all(engine)


def get_all_journeys():
    with Session(engine) as session:
        # Get all data available
        journeys = session.query(Journey).all()
        return convert_to_model(journeys)


def get_journyes(source, destination, departure):
    with Session(engine) as session:
        journeys = session\
            .query(Journey)\
            .filter(Journey.source == source)\
            .filter(Journey.destination == destination)\
            .filter(Journey.departure_datetime >= departure)\
            .all()

        return convert_to_model(journeys)


def save_journeys(journeys):
    with Session(engine) as session:

        # add newly created object to the session
        session.add_all(journeys)
        # execute in the DB
        session.commit()


def convert_to_model(journeys):
    if len(journeys) > 0:
        return [models.Journey.from_orm(journey) for journey in journeys]
    else:
        return None

# if __name__ == '__main__':
#     from sqlalchemy.orm import aliased
#     leg1 = aliased(Journey, name="leg1")
#     leg2 = aliased(Journey, name="leg2")
#     with Session(engine) as session:
#         result = session.query(
#             leg1, leg2
#         ).join(
#             leg2,
#             leg1.destination == leg2.source
#         ).all()

#         for row in result:
#             print((
#                 "found combination: "
#                 f"{row.leg1.departure_datetime} - "
#                 f"{row.leg1.source}-{row.leg1.destination}"
#                 " + "
#                 f"{row.leg2.source}-{row.leg2.destination}"
#             ))
