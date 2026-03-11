from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.db.models import Book, Borrow
from typing import TypedDict
from app.services.history_service import *

class BorrowsResult(TypedDict):
    borrowed_list: list[Borrow]
    borrowed_counter: int

def create_borrow(db: Session, borrow: Borrow) -> Borrow:
    # borrow = Borrow(**data)
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow

def return_book(db: Session, borrow: Borrow) -> None:
    # for history purposes to track how many times a book as been borrow as well books that have been borrow at least once (can create some reports from that data....)
    history = create_history(db, borrow)
    print("History Record:\n", history.to_dict())
    # deletes from borrow since it haves been return the book to the library
    delete_borrow(db, borrow_id=borrow.id)


def get_borrow(db: Session, borrow_id: int) -> Borrow | None:
    return db.query(Borrow).filter(Borrow.id == borrow_id).first()

def get_all_borrows(db: Session) -> BorrowsResult:
    borrowed = db.query(Borrow).all()
    return {
        "borrowed_list": borrowed,
        "borrowed_counter": len(borrowed),
    }

def get_all_borrows_by_requester(db: Session, requester: str, init_date: datetime | None = None, final_date: datetime| None = None) -> list[Borrow]:
    
    query = (
        db.query(Borrow)
        .join(Book, Borrow.book_id == Book.id)
        .options(joinedload(Borrow.book))  # eagerly loads the book relation
    )
    
    if requester:
        query = query.filter(Borrow.borrower_name == requester)

    if init_date:
        print(f"\ninit_date: {init_date.strftime('%d/%m/%Y')}\n")
        query = query.filter(Borrow.borrow_date >= init_date.strftime("%d/%m/%Y"))

    if final_date:
        print(f"\final_date: {final_date.strftime('%d/%m/%Y')}\n")
        query = query.filter(Borrow.borrow_date < final_date.strftime("%d/%m/%Y"))

    return query.all()

def get_requester_list(db: Session) -> list[str]:
    requesters = [row[0] for row in db.query(Borrow.borrower_name).distinct().all()]
    print("requesters list:\n", requesters)
    return requesters

def update_borrow(db: Session, borrow_id: int, data: dict) -> Borrow | None:
    borrow = db.query(Borrow).filter(Borrow.id == borrow_id).first()
    if not borrow:
        return None

    for key, value in data.items():
        setattr(borrow, key, value)

    db.commit()
    db.refresh(borrow)
    return borrow


def delete_borrow(db: Session, borrow_id: int) -> bool:
    borrow = db.query(Borrow).filter(Borrow.id == borrow_id).first()
    if not borrow:
        return False

    db.delete(borrow)
    db.commit()
    return True

def delete_all_borrows(db: Session) -> None:
    db.query(Borrow).delete()
    db.commit()