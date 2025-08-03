from typing import Type, TypeVar, Generic, List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

Model = TypeVar("Model")
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)

from sqlalchemy.exc import SQLAlchemyError


class GenericRepo(Generic[Model, CreateSchema]):
	"""
	Generic repository for CRUD operations.
	"""

	def __init__(self, session: Session, model: Type[Model]):
		self.session = session
		self.model = model

	def get(self, id: int) -> Optional[Model]:
		"""
				Retrieve a single record by its primary key.
				Args:
					id (int): Primary key of the record.
				Returns:
					Optional[Model]: The model instance if found, else None.
				"""
		return self.session.query(self.model).get(id)

	def list(self, **filters) -> List[Model]:
		"""
		List all records matching the given filters.
		Args:
			**filters: Keyword arguments to filter the query.
		Returns:
			List[Model]: List of model instances.
		"""
		return self.session.query(self.model).filter_by(**filters).all()

	def create(self, obj_in: CreateSchema) -> Model:
		"""
				Create a new record in the database.
				Args:
					obj_in (CreateSchema): Pydantic schema with creation data.
				Returns:
					Model: The created model instance.
				"""
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
		"""
				Update an existing record with new data.
				Args:
					obj (Model): The existing model instance.
					obj_in (CreateSchema): Pydantic schema with update data.
				Returns:
					Model: The updated model instance.
				"""
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
		"""
				Delete a record by its primary key.
				Args:
					id (int): Primary key of the record to delete.
				"""
		obj = self.get(id)
		if obj:
			try:
				self.session.delete(obj)
				self.session.commit()
			except SQLAlchemyError:
				self.session.rollback()
				raise
