from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from app.db.models import History, Borrow

def create_history(db: Session, borrow: Borrow) -> History:
    print("create borrow dict to convert to history....")
    borrow_dict = {
        column.name: getattr(borrow, column.name)
        for column in borrow.__table__.columns        
    }
    # borrow_dict.pop("id")  # let DB generate a new id for history  # also works, returns the removed value
    del borrow_dict["id"]        # also works, just deletes it
    # borrow_dict.pop("book") # don't need this since it already ignore in  borrow.__table__.columns since this is not a column but a relationship...
    print("borrow_dict:\n", borrow_dict)
    history = History(**borrow_dict, date_returned=datetime.now(tz=ZoneInfo("UTC")).strftime("%d/%m/%Y-%H:%M:%S"))
    print("\n\nhistory:\n", history.to_dict(),"\n\n")
    db.add(history)
    db.commit()
    db.refresh(history)
    return history

# could be added some filters like in borrow to return a list filtered by some fields but for simplicity return everything 
def get_all_historys(db: Session) -> list[History]:
    return db.query(History).all()
