from pydantic import BaseModel
from typing import Literal, Optional, List

FieldType = Literal["uuid","string","text","int","float","bool","date","datetime","enum"]
PageType  = Literal["dashboard","list","detail","form"]

class FieldDef(BaseModel):
    name: str
    type: FieldType
    required: bool = False
    primary: bool = False
    default: Optional[str] = None
    values: Optional[List[str]] = None

class RelationDef(BaseModel):
    type: Literal["hasMany","belongsTo","manyToMany"]
    target: str
    via: Optional[str] = None

class Entity(BaseModel):
    name: str
    fields: List[FieldDef]
    relations: List[RelationDef] = []

class Page(BaseModel):
    path: str
    type: PageType
    entity: Optional[str] = None
    actions: List[str] = []
    filters: List[str] = []
    tabs: List[str] = []

class AppSpec(BaseModel):
    app: dict
    entities: List[Entity]
    pages: List[Page]
    api_conventions: dict | None = None
