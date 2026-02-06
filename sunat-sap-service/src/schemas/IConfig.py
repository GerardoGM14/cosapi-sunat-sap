from typing import TypedDict, Optional


class BaseConfig(TypedDict):
    folder: str

class CredSap(TypedDict):
    email: str
    password: str

class CredSunat(TypedDict):
    ruc: str
    user: str
    clave: str

class DateSap(TypedDict):
    date: str

class DateSunat(TypedDict):
    month: int
    year: int

class ISap(BaseConfig):
    code_sociedad: str
    cred: CredSap
    date: DateSap
    time: Optional[str]
    days: Optional[str]

class ISunat(BaseConfig):
    cred: CredSunat
    date: DateSunat
    time: Optional[str]
    days: Optional[str]

class IArgs(TypedDict):
    sap: ISap
    sunat: ISunat
    socket_url: Optional[str] = None
