"""
Pydantic models for API responses.
"""
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, Dict, Any

class Event(BaseModel):
    id: int
    ts: int
    proto: str
    src: Optional[str]
    dst: Optional[str]
    mac: Optional[str]
    extra: Optional[Dict[str, Any]]

class Counts(BaseModel):
    counts: Dict[str, int]
