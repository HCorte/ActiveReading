from typing import Any
from app.db.database import Base
from sqlalchemy import Enum as SQLEnum, ForeignKey # ForeignKey, 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum

class BookCategory(str, Enum):
	SCIENCE_FICTION = "Science Fiction"
	FANTASY = "Fantasy"
	MYSTERY = "Mystery"
	ROMANCE = "Romance"
	NON_FICTION = "Non-Fiction"

class Library(Base):
	__tablename__ = 'library'

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)

    # Add relationships # One library → many books (FK lives on Book side)
	books: Mapped[list["Book"]] = relationship("Book", back_populates="library")

	def to_dict(self) -> dict[str, Any]:
		return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class Book(Base):
	__tablename__ = 'book'

	id: Mapped[int] = mapped_column(primary_key=True)
	title: Mapped[str] = mapped_column(index=True, unique=True)
	code: Mapped[str] = mapped_column(index=True, unique=True)
	author: Mapped[str]
	category: Mapped[BookCategory] = mapped_column(SQLEnum(BookCategory), nullable=False)
	publisher: Mapped[str]
	year: Mapped[int]
	library_id: Mapped[int] = mapped_column(ForeignKey("library.id"), nullable=True)  # FK here and optional because a book might not be in a library yet

	# Back to Library
	library: Mapped["Library"] = relationship("Library", back_populates="books")

	# One book → one borrow record (FK lives on Borrow side)
	borrowed: Mapped["Borrow"] = relationship("Borrow", back_populates="book") #, uselist=False
	history: Mapped[list["History"]] = relationship("History", back_populates="book")

	def to_dict(self) -> dict[str, Any]:
		return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
		}
	
class Borrow(Base):
	__tablename__ = 'borrow'

	id: Mapped[int] = mapped_column(primary_key=True)
	book_id: Mapped[int] = mapped_column(ForeignKey("book.id"))
	borrower_name: Mapped[str]
	borrow_date: Mapped[str]
	return_date: Mapped[str]

	book: Mapped["Book"] = relationship("Book", back_populates="borrowed")

	def to_dict(self) -> dict[str, Any]:
		data = {
			column.name: getattr(self, column.name)
			for column in self.__table__.columns
		}
		# Include the related book if loaded
		if self.book:
			data["book"] = self.book.to_dict()
		return data
	
class History(Base):
	__tablename__ = 'history'

	id: Mapped[int] = mapped_column(primary_key=True)
	book_id: Mapped[int] = mapped_column(ForeignKey("book.id"))
	borrower_name: Mapped[str]
	borrow_date: Mapped[str]
	return_date: Mapped[str]
	date_returned: Mapped[str]

	book: Mapped["Book"] = relationship("Book", back_populates="history")  # was "borrowed"

	def to_dict(self) -> dict[str, Any]:
		data = {
			column.name: getattr(self, column.name)
			for column in self.__table__.columns
		}
		# Include the related book if loaded
		if self.book:
			data["book"] = self.book.to_dict()
		return data