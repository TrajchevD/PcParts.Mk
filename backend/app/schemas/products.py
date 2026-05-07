from typing import Any, Optional

from pydantic import BaseModel


class CompareRequest(BaseModel):
    category: str
    ids: list[Any]
