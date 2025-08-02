from typing import Optional, List
from sqlalchemy.orm import Session
from src.database.models.post import Post


class PostRepository:
    """
    Repository class responsible for handling all database operations related to the Post entity.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, post: Post) -> Post:
        """
        Adds a new Post record to the database and commits the transaction.

        Args:
            post (Post): The Post instance to add.

        Returns:
            Post: The created Post instance refreshed with database state (e.g., assigned ID).
        """
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_by_id(self, post_id: int) -> Optional[Post]:
        """
        Retrieves a Post by its unique ID.

        Args:
            post_id (int): The unique identifier of the Post.

        Returns:
            Optional[Post]: The matching Post object if found, else None.
        """
        return self.db.query(Post).filter(Post.id == post_id).first()

    def list(
        self,
        category: Optional[str] = None,
        sort_by: str = "likes"
    ) -> List[Post]:
        """
        Retrieves a list of Posts, optionally filtered by category and sorted by specified criteria.

        Args:
            category (Optional[str]): If provided, filters Posts by this category.
            sort_by (str): Field to sort by, either 'likes' (default) or 'newest'.

        Returns:
            List[Post]: A list of Post instances matching the filters and sort order.
        """
        query = self.db.query(Post)
        if category:
            query = query.filter(Post.category == category)

        if sort_by == "likes":
            query = query.order_by(Post.likes.desc())
        elif sort_by == "newest":
            query = query.order_by(Post.created_at.desc())

        return query.all()

    def delete(self, post: Post) -> None:
        """
        Deletes the given Post record from the database and commits the transaction.

        Args:
            post (Post): The Post instance to delete.
        """
        self.db.delete(post)
        self.db.commit()

    def get_by_id_and_owner(
        self,
        post_id: int,
        owner_id: int
    ) -> Optional[Post]:
        """
        Retrieves a Post by ID and owner ID, ensuring ownership match.

        Args:
            post_id (int): The unique identifier of the Post.
            owner_id (int): The unique identifier of the owner/user.

        Returns:
            Optional[Post]: The matching Post object if found and owned by the owner, else None.
        """
        return (
            self.db.query(Post)
            .filter(Post.id == post_id, Post.owner_id == owner_id)
            .first()
        )

    def update(self, post: Post) -> Post:
        """
        Commits any changes made to the Post instance to the database and refreshes its state.

        Args:
            post (Post): The Post instance with updated data.

        Returns:
            Post: The updated Post instance refreshed with the latest database state.
        """
        self.db.commit()
        self.db.refresh(post)
        return post
