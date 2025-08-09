from typing import Optional
from sqlalchemy.orm import Session
from src.database.models.user import User


class UserRepository:
    """
    Repository class responsible for managing User entities in the database.
    """

    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        """
        Adds a new User to the database and commits the transaction.

        Args:
            user (User): The User instance to be added to the database.

        Returns:
            User: The newly created User object refreshed with the latest state from the database.
        """
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
        
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieves a User by its unique ID.

        Args:
            user_id (int): The unique identifier of the Post.

        Returns:
            Optional[User]: The matching User object if found, else None.
        """
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieves a User record by its username.

        Args:
            username (str): The username string to filter by.

        Returns:
            Optional[User]: The User object if found, otherwise None.
        """
        return self.session.query(User).filter(User.username == username).first()
    
    def get_by_linkedin_urn(self, linkedin_urn: str) -> Optional[User]:
        """
		Retrieves a User record by its LinkedIn URN.

		Args:
			linkedin_urn (str): The LinkedIn URN to filter by.

		Returns:
			Optional[User]: The User object if found, otherwise None.
		"""
        return self.session.query(User).filter(User.li_owner_urn == linkedin_urn).first()		
        

    def update(self, user: User) -> User:
        """
        Commits changes to an existing User record and refreshes the session state.

        Args:
            user (User): The User instance with updated information.

        Returns:
            User: The updated User object refreshed with the latest database state.
        """
        self.session.commit()
        self.session.refresh(user)
        return user   
