from typing import Optional, List

from src.database.models.user import User
from src.repositories.user_repo import UserRepository
from src.schemas.user_schemas import UserUpdate
from src.utilities.password_utils import get_password_hash, verify_password
from src.utilities import logger
from src.exceptions.user import UserException

logger = logger.setup_logger("UserService")


class UserService:
    """
    Service class responsible for business logic related to user management.

    This class handles creation, retrieval, authentication, updates of users,
    and retrieval of related user posts. It delegates persistence operations to UserRepository.

    Critical operations and error conditions are logged for traceability.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        logger.info("UserService initialized with UserRepository")

    def create_user(self, username: str, password: str) -> User:
        """
        Create a new user with a hashed password and persist it.

        Args:
            username (str): Username for the new user.
            password (str): Plain-text password to be hashed.

        Returns:
            User: The newly created User instance.

        Raises:
            Exception: If there is an error during creation, it will be logged and raised.
        """
        logger.info(f"Creating user with username: {username}")
        try:
            hashed_password = get_password_hash(password)
            user = User(username=username, hashed_password=hashed_password)
            created_user = self.user_repo.create(user)
            logger.info(f"User created successfully with id: {created_user.id}")
            return created_user

        except Exception as e:
            logger.error(f"Failed to create user '{username}': {e}", exc_info=True)
            raise UserException("Failed to create user") from e
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username.

        Args:
            username (str): Username to search for.

        Returns:
            Optional[User]: User object if found, else None.

        Raises:
            HTTPException: If the user does not exist, a 404 error is raised.
        """
        logger.info(f"Fetching user by username: {username}")
        try:
            user = self.user_repo.get_by_username(username)
            if user is None:
                logger.warning(f"User with username '{username}' not found")
            else:
                logger.info(f"User with username '{username}' retrieved successfully")
            return user

        except Exception as e:
            logger.error(f"Error retrieving user '{username}': {e}", exc_info=True)
            raise UserException("Failed to retrieve user by username") from e

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by verifying the provided password.

        Args:
            username (str): Username of the user to authenticate.
            password (str): Plain-text password to verify.

        Returns:
            Optional[User]: User if authentication is successful; otherwise None.

        Raises:
            HTTPException: If authentication fails, a 401 error is raised.
        """
        logger.info(f"Authenticating user: {username}")
        try:
            user = self.get_user_by_username(username)
            if not user:
                logger.warning(f"Authentication failed: user '{username}' not found")
                return None

            if not verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed: invalid password for user '{username}'")
                return None

            logger.info(f"User '{username}' authenticated successfully")
            return user

        except Exception as e:
            logger.error(f"Error during authentication for user '{username}': {e}", exc_info=True)
            raise UserException("Error during authentication") from e
    def update_user(self, user: User, updates: UserUpdate) -> User:
        """
        Update user fields such as username and/or password.

        Args:
            user (User): The User instance to update.
            updates (UserUpdate): Object containing fields to update.

        Returns:
            User: The updated User instance.

        Logs:
            Info on update attempt and success.
            Error with stack trace if update fails.
        """
        logger.info(f"Updating user with id: {user.id}")
        try:
            # Check if username update is requested
            if updates.username:
                logger.debug(f"Updating username to: {updates.username}")
                user.username = updates.username

            # Check if password update is requested
            if updates.password:
                logger.debug("Updating password")
                user.hashed_password = get_password_hash(updates.password)

            updated_user = self.user_repo.update(user)
            logger.info(f"User with id {user.id} updated successfully")
            return updated_user

        except Exception as e:
            logger.error(f"Failed to update user with id {user.id}: {e}", exc_info=True)
            raise UserException("Failed to update user") from e

    def get_user_posts(self, user: User) -> List:
        """
        Retrieve posts associated with the given user.

        Args:
            user (User): The user whose posts to retrieve.

        Returns:
            List: List of posts owned by the user.

        Raises:
            HTTPException: If an error occurs during retrieval, a 500 error is raised.
        """
        logger.info(f"Fetching posts for user id: {user.id}")
        try:
            posts = user.posts

            if not posts:
                logger.warning(f"No posts found for user id: {user.id}")
            else:
                logger.info(f"Found {len(posts)} posts for user id: {user.id}")

            return posts

        except Exception as e:
            logger.error(f"Error retrieving posts for user id {user.id}: {e}", exc_info=True)
            raise UserException("Failed to get user posts") from e
