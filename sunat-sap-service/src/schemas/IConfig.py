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

class ISunat(BaseConfig):
    cred: CredSunat
    date: DateSunat

class IArgs(TypedDict):
    sap: ISap
    sunat: ISunat
    socket_url: Optional[str] = None
