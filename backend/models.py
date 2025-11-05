from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    total_students = Column(Integer, default=0)

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    payment_status = Column(String, default="unpaid")
    last_payment_date = Column(String, nullable=True)
    amount = Column(Integer, default=0)
    
    # Relationship to batch
    batch = relationship("Batch", back_populates="students")

# Add this line to Batch class to complete the relationship
Batch.students = relationship("Student", back_populates="batch", cascade="all, delete-orphan")

from sqlalchemy import DateTime
from datetime import datetime

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Integer, nullable=False)
    transaction_id = Column(String, nullable=True)
    
    # Relationship to student
    student = relationship("Student", back_populates="payments")

# Add this line to Student class to complete the relationship
Student.payments = relationship("Payment", back_populates="student", cascade="all, delete-orphan")
