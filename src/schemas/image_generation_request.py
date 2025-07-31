from pydantic import BaseModel, Field, conint, confloat

class GenerateRequest(BaseModel):
      prompt: str
      seed: conint(ge=0) = Field(..., description="Seed for random number generation")
      height: conint(gt=0) = Field(..., description="Height of the generated image, must be a positive integer and a multiple of 8")
      width: conint(gt=0) = Field(..., description="Width of the generated image, must be a positive integer and a multiple of 8")
      cfg: confloat(gt=0) = Field(..., description="CFG (classifier-free guidance scale), must be a positive integer or 0")
      steps: conint(ge=0) = Field(..., description="Number of steps")
      batch_size: conint(gt=0) = Field(..., description="Number of images to generate in a batch")
