
from datetime import datetime
from enum import Enum

class ConsultStatus(str, Enum):
    AGENDADA = "Agendada"
    REALIZADA = "Realizada"
    CANCELADA = "Cancelada"

class Consult():
    
    def __init__(
            self, name: str, 
            doctor_name: str, 
            date: datetime,
            status: ConsultStatus
        ):
        self.__name: str = name
        self.__doctor_name: str = doctor_name
        self.__date: datetime = date
        self.__status: ConsultStatus = status

        @property
        def get_name(self) -> str:
            return self.__name

        @property
        def get_doctor_name(self) -> str:
            return self.__doctor_name

        @property
        def get_date(self) -> datetime:
            return self.__date

        @property
        def get_status(self) -> ConsultStatus:
            return self.__status

        def set_name(self, name: str) -> None:
            self.__name = name

        def set_doctor_name(self, doctor_name: str) -> None:
            self.__doctor_name = doctor_name

        def set_date(self, date: datetime) -> None:
            self.__date = date

        def set_status(self, status: ConsultStatus) -> None:
            self.__status = status
