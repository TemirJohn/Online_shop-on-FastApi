from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.models.order import Order, OrderItem
from app.models.database import OrderDB, OrderItemDB, ProductDB, CustomerDB
from app.database import get_db

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=Order)
def create_order(order: Order, db: Session = Depends(get_db)):
    customer = db.query(CustomerDB).filter(CustomerDB.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Client not found")
    
    total = 0
    order_items_list = []
    
    for item in order.items:
        product = db.query(ProductDB).filter(ProductDB.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404, 
                detail=f"Product with ID {item.product_id} not found"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough goods'{product.name}' in stock"
            )
        
        item_price = product.price * item.quantity
        total += item_price
        
        product.stock -= item.quantity
        
        order_items_list.append({
            'product_id': item.product_id,
            'quantity': item.quantity,
            'price': item_price
        })
    
    db_order = OrderDB(
        customer_id=order.customer_id,
        total_price=total,
        status=order.status,
        created_at=datetime.utcnow()
    )
    db.add(db_order)
    db.flush()
    
    for item_data in order_items_list:
        order_item = OrderItemDB(
            order_id=db_order.id,
            **item_data
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(db_order)
    
    response_items = [
        OrderItem(product_id=item['product_id'], quantity=item['quantity'])
        for item in order_items_list
    ]
    
    return Order(
        id=db_order.id,
        customer_id=db_order.customer_id,
        items=response_items,
        total_price=db_order.total_price,
        status=db_order.status,
        created_at=db_order.created_at
    )


@router.get("/", response_model=List[Order])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = db.query(OrderDB).offset(skip).limit(limit).all()
    
    result = []
    for order in orders:
        order_items = db.query(OrderItemDB).filter(OrderItemDB.order_id == order.id).all()
        items = [
            OrderItem(product_id=item.product_id, quantity=item.quantity)
            for item in order_items
        ]
        result.append(Order(
            id=order.id,
            customer_id=order.customer_id,
            items=items,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at
        ))
    
    return result


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_items = db.query(OrderItemDB).filter(OrderItemDB.order_id == order.id).all()
    items = [
        OrderItem(product_id=item.product_id, quantity=item.quantity)
        for item in order_items
    ]
    
    return Order(
        id=order.id,
        customer_id=order.customer_id,
        items=items,
        total_price=order.total_price,
        status=order.status,
        created_at=order.created_at
    )


@router.patch("/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    return {"message": f"Order status updated to'{status}'"}