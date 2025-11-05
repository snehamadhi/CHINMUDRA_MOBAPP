from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
from models import Batch
from datetime import datetime


app = FastAPI()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root route
@app.get("/")
def read_root():
    return {"message": "Hello, Chinmudra!"}

# Pydantic schema for creating a batch
class BatchCreate(BaseModel):
    name: str

# POST route to create a batch
@app.post("/batches")
def create_batch(batch: BatchCreate, db: Session = Depends(get_db)):
    existing = db.query(Batch).filter(Batch.name == batch.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Batch already exists")
    new_batch = Batch(name=batch.name)
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch

# GET all batches
@app.get("/batches")
def read_batches(db: Session = Depends(get_db)):
    return db.query(Batch).all()

from models import Student

# Pydantic schema for creating a student
class StudentCreate(BaseModel):
    name: str
    batch_id: int

# POST route to create a student
@app.post("/students")
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == student.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    new_student = Student(
        name=student.name,
        batch_id=student.batch_id,
        payment_status="unpaid",
        amount=0
    )
    db.add(new_student)
    # Update total_students in batch
    batch.total_students += 1
    db.commit()
    db.refresh(new_student)
    return new_student

from models import Payment

# Pydantic schema for Payment creation
class PaymentCreate(BaseModel):
    student_id: int
    amount: int
    transaction_id: str = None

# POST route to create a payment
@app.post("/payments")
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == payment.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    new_payment = Payment(
        student_id=payment.student_id,
        amount=payment.amount,
        transaction_id=payment.transaction_id
    )
    db.add(new_payment)
    
    # Update student payment info
    student.amount = payment.amount
    student.payment_status = "paid"
    student.last_payment_date = datetime.utcnow().isoformat()
    
    db.commit()
    db.refresh(new_payment)
    return new_payment

# GET all payments for a student
@app.get("/students/{student_id}/payments")
def get_payments(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student.payments

# GET all students in a specific batch
@app.get("/batches/{batch_id}/students")
def get_students_in_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Return all students in this batch
    return batch.students
