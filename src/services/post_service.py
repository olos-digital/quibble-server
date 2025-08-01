from typing import Optional, List

from src.database.models.post import Post
from src.database.models.user import User
from src.repositories.post_repo import PostRepository


class PostService:
    """
    Service class for post operations in FastAPI.

    Coordinates higher-level logic; uses PostRepository for DB operations.
    """

    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def create_post(self, user: User, title: str, content: str) -> Post:
        post = Post(title=title, content=content, owner_id=user.id)
        return self.post_repo.create(post)

    def get_post(self, post_id: int) -> Optional[Post]:
        return self.post_repo.get_by_id(post_id)

    def get_posts(
        self,
        category: Optional[str] = None,
        sort_by: str = "likes"
    ) -> List[Post]:
        return self.post_repo.list(category=category, sort_by=sort_by)

    def delete_post(self, user: User, post_id: int) -> bool:
        post = self.post_repo.get_by_id(post_id)
        if post and post.owner_id == user.id:
            self.post_repo.delete(post)
            return True
        return False

    def update_post_image(self, user: User, post_id: int, image_url: str) -> Optional[Post]:
        post = self.post_repo.get_by_id_and_owner(post_id, user.id)
        if not post:
            return None
        post.image_url = image_url
        return self.post_repo.update(post)
