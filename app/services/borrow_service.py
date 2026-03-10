from sqlalchemy.orm import Session
from app.db.models import Borrow


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