from typing import Type, TypeVar, Generic, List, Optional, Mapping, Any
from sqlalchemy.orm import Session, DeclarativeMeta
from pydantic import BaseModel

Model = TypeVar("Model", bound=DeclarativeMeta)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)


class GenericRepo(Generic[Model, CreateSchema]):
    def __init__(
        self,
        session: Session,
        model: Type[Model],
        field_map: Optional[Mapping[str, str]] = None,
    ):
        """
        field_map: optional mapping from schema field names to model init kwarg names
                   e.g., {"some_schema_name": "different_model_attr"}
        """
        self.session = session
        self.model = model
        self.field_map = field_map or {}

    def _to_model_kwargs(self, obj_in: BaseModel, exclude_unset: bool = False) -> dict:
        data = obj_in.dict(exclude_unset=exclude_unset)
        mapped = {}
        for k, v in data.items():
            target_key = self.field_map.get(k, k)
            mapped[target_key] = v
        return mapped

    def get(self, id: int) -> Optional[Model]:
        return self.session.get(self.model, id)

    def list(self, **filters) -> List[Model]:
        return self.session.query(self.model).filter_by(**filters).all()

    def create(self, obj_in: CreateSchema) -> Model:
        try:
            with self.session.begin():
                kwargs = self._to_model_kwargs(obj_in, exclude_unset=False)
                obj = self.model(**kwargs)
                self.session.add(obj)
            self.session.refresh(obj)
            return obj
        except Exception:
            self.session.rollback()
            raise

    def update(self, obj: Model, obj_in: CreateSchema) -> Model:
        try:
            with self.session.begin():
                kwargs = self._to_model_kwargs(obj_in, exclude_unset=True)
                for k, v in kwargs.items():
                    setattr(obj, k, v)
            self.session.refresh(obj)
            return obj
        except Exception:
            self.session.rollback()
            raise

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if not obj:
            return False
        try:
            with self.session.begin():
                self.session.delete(obj)
            return True
        except Exception:
            self.session.rollback()
            raise