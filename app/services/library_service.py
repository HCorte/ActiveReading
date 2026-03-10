from sqlalchemy.orm import Session
from app.db.models import Library


def create_library(db: Session, library: Library) -> Library:
    # library = Library(**data)
    db.add(library)
    db.commit()
    db.refresh(library)
    return library


def get_library(db: Session, library_id: int) -> Library | None:
    return db.query(Library).filter(Library.id == library_id).first()

def get_all_librarys(db: Session) -> list[Library]:
    return db.query(Library).all()


def update_library(db: Session, library_id: int, data: dict) -> Library | None:
    library = db.query(Library).filter(Library.id == library_id).first()
    if not library:
        return None

    for key, value in data.items():
        setattr(library, key, value)

    db.commit()
    db.refresh(library)
    return library


def delete_library(db: Session, library_id: int) -> bool:
    library = db.query(Library).filter(Library.id == library_id).first()
    if not library:
        return False

    db.delete(library)
    db.commit()
    return True

def delete_all_libraries(db: Session) -> None:
    db.query(Library).delete()
    db.commit()