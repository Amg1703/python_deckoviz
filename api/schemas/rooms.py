from pydantic import BaseModel 
from typing import List, Optional

class Collection(BaseModel):
    id: str
    # Size of collection in MB, renamed to match payload
    space_mb: float
    images: List[str]

class BatchRequest(BaseModel):
    # Available space in MB on TV, renamed to match payload
    available_space_mb: float
    collection: Collection
