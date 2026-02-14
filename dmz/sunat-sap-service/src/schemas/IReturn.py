from playwright.sync_api import FrameLocator
from typing import TypedDict, Optional


class IReturn(TypedDict):
    success: bool
    message: str
    error_system: bool
    frame: Optional[FrameLocator] = None
    file_path_sap: Optional[str] = None
    file_path_sunat: Optional[str] = None

