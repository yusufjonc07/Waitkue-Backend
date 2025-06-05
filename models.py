from datetime import datetime 
from sqlalchemy import Column, Time, ForeignKey, Integer, Date, String, DateTime, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base 


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role = Column(Text)
    email = Column(Text, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    username = Column(String(50), unique=True)
    password_hash = Column(String(255), nullable=False)
    disabled = Column(Boolean, default=False)
    
    
    
    
    profile = relationship(
        "Client",
        back_populates="user",
        uselist=False,
        lazy="subquery", 
        cascade="all, delete"
    )


class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    firstname = Column(String(50))
    surename = Column(String(50))
    middlename = Column(String(50))
    gender = Column(String(10), default='unknown')
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey('user.id'))
    
    @property
    def fullname(self):
        parts = [self.surename, self.middlename, self.firstname]
        return " ".join(filter(None, parts)) 

    __table_args__ = (
        UniqueConstraint('firstname', 'surename', name='fullname_constraint'),
    )

    user = relationship('User')    


class Service(Base):
    __tablename__ = "service"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True)
    room = Column(Integer)
    image_url = Column(Text)
    description = Column(Text)
    avg_minute = Column(Text)
    from_time = Column(Time)
    to_time = Column(Time)
    available_days = Column(Text)
    disabled = Column(Boolean, default=False)


class Queue(Base):
    __tablename__ = "queue"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('user.id'))
    service_id = Column(Integer, ForeignKey('service.id'))
    number = Column(Integer)
    time = Column(Time, nullable=False)
    date = Column(Date, nullable=False)
    comment = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    step = Column(Integer, default=1)
    in_room = Column(Boolean, default=False)

    client = relationship('User', backref='queues', lazy="joined")
    service = relationship('Service', backref='queues', lazy="joined")