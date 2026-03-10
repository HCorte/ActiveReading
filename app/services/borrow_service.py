from sqlalchemy.orm import Session, joinedload
from app.db.models import Book, Borrow


def create_borrow(db: Session, borrow: Borrow) -> Borrow:
    # borrow = Borrow(**data)
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow


def get_borrow(db: Session, borrow_id: int) -> Borrow | None:
    return db.query(Borrow).filter(Borrow.id == borrow_id).first()

def get_all_borrows(db: Session) -> list[Borrow]:
    return db.query(Borrow).all()

def get_all_borrows_by_requester(db: Session, requester: str) -> list[Borrow]:
    return (
        db.query(Borrow)
        .join(Book, Borrow.book_id == Book.id)
        .filter(Borrow.borrower_name == requester)
        .options(joinedload(Borrow.book))  # eagerly loads the book relation
        .all()
    )

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