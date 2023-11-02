from pydantic import BaseModel, HttpUrl

from typing import Sequence, Optional


class GetFile(BaseModel):
    file: str
    
