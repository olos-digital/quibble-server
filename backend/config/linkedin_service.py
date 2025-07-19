from services.upload_image_and_post import publish_post_to_linkedin

class LinkedInService:
    def publish_post(self, text: str, image_path: str) -> None:
        publish_post_to_linkedin(text=text, image_path=image_path)