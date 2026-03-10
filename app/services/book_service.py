from sqlalchemy.orm import Session
from app.db.models import Book


def create_book(db: Session, book: Book) -> Book:
    # book = Book(**data)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_book_by_code(db: Session, code: str) -> Book | None:
    return db.query(Book).filter(Book.code == code).first()

def get_all_books(db: Session) -> list[Book]:
	return db.query(Book).all()

def update_book(db: Session, book_id: int, data: dict) -> Book | None:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return None

    for key, value in data.items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> bool:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return False

    db.delete(book)
    db.commit()
    return True

def delete_all_books(db: Session) -> None:
    db.query(Book).delete()
    db.commit()