from typing import TypedDict, Optional
from enum import Enum


class EmitEvent(str, Enum):
    SAP = 'sap:bot'
    SUNAT = 'sunat:bot'


class IDataEmit(TypedDict):
    message: str
    date: str
