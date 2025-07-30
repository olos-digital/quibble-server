from pydantic import BaseModel


class TweetResponse(BaseModel):
    """
    Pydantic model for tweet creation responses.
    
    This model structures the output of tweet posting endpoints, ensuring
    consistent API responses in FastAPI. 
    
    Attributes:
        message (str): Success message (e.g., "Tweet posted!").
        tweet_id (str | int): Unique identifier of the created tweet.
    """
    message: str
    tweet_id: str | int
