from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel

Model = TypeVar("Model")
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)

class GenericRepo(Generic[Model, CreateSchema]):
    def __init__(self, session: Session, model: Type[Model]):
        self.session = session
        self.model = model

    def get(self, id: int) -> Optional[Model]:
        return self.session.query(self.model).get(id)

    def list(self, **filters) -> List[Model]:
        return self.session.query(self.model).filter_by(**filters).all()

    def create(self, obj_in: CreateSchema) -> Model:
        obj = self.model(**obj_in.dict())
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: Model, obj_in: CreateSchema) -> Model:
        for k, v in obj_in.dict(exclude_unset=True).items():
            setattr(obj, k, v)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, id: int) -> None:
        obj = self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()