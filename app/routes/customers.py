from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.models.customer import Customer
from app.models.database import CustomerDB
from app.database import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=Customer)
def create_customer(customer: Customer, db: Session = Depends(get_db)):
    db_customer = CustomerDB(
        name=customer.name,
        email=customer.email,
        phone=customer.phone
    )
    try:
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")


@router.get("/", response_model=List[Customer])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = db.query(CustomerDB).offset(skip).limit(limit).all()
    return customers


@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(CustomerDB).filter(CustomerDB.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Client not found")
    return customer


@router.put("/{customer_id}", response_model=Customer)
def update_customer(customer_id: int, updated_customer: Customer, db: Session = Depends(get_db)):
    customer = db.query(CustomerDB).filter(CustomerDB.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Client not found")
    
    customer.name = updated_customer.name
    customer.email = updated_customer.email
    customer.phone = updated_customer.phone
    
    try:
        db.commit()
        db.refresh(customer)
        return customer
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(CustomerDB).filter(CustomerDB.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(customer)
    db.commit()
    return {"message": "The client has been deleted."}