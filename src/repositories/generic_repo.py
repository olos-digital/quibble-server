from typing import Type, TypeVar, Generic, List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

Model = TypeVar("Model")
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)

from sqlalchemy.exc import SQLAlchemyError

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
        try:
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            return obj
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def update(self, obj: Model, obj_in: CreateSchema) -> Model:
        try:
            for k, v in obj_in.dict(exclude_unset=True).items():
                setattr(obj, k, v)
            self.session.commit()
            self.session.refresh(obj)
            return obj
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def delete(self, id: int) -> None:
        obj = self.get(id)
        if obj:
            try:
                self.session.delete(obj)
                self.session.commit()
            except SQLAlchemyError:
                self.session.rollback()
                raise