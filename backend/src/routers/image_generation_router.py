# routers/image_generation_router.py
# (Recommended file name and path for a FastAPI project; groups image generation
# endpoints to promote modularity and clear API documentation.)

from fastapi import APIRouter, HTTPException

from io import BytesIO

import base64

from typing import List

from diffusers import FlowMatchEulerDiscreteScheduler, FluxPipeline  # Assumed imports for the pipeline.

import torch

from schemas.image_generation_request import GenerateRequest  
from generation.images.image_pipeline import pipeline

class ImageGenerationRouter:
    """
    Router class for image generation endpoints in FastAPI.
    
    This class defines a route for generating images using a diffusion model (e.g., FluxPipeline),
    handling validation, generation, and base64 encoding. It follows FastAPI best practices for
    async operations, error handling, and response serialization, with the pipeline assumed
    to be pre-initialized (e.g., globally or via dependency injection).
    """
    
    def __init__(self) -> None:
        # Initialize router: Sets tags for OpenAPI grouping; prefix can be added when including in app.
        self.router = APIRouter(prefix="/ai", tags=["Image Generation"])
        self._setup_routes()  

    def _setup_routes(self) -> None:
        # Defines the endpoint handler; kept private for encapsulation.
        
        @self.router.post("/image-generation")
        async def generate_image(request: GenerateRequest) -> dict:
            """
            Generates images based on the provided request parameters.
            
            This async endpoint validates dimensions, generates images using a diffusion pipeline,
            and returns them as base64-encoded strings. It ensures deterministic seeding and
            handles batch generation efficiently, suitable for AI-powered FastAPI apps.
            
            Args:
                request (GenerateRequest): Pydantic model with prompt, dimensions, seed, etc.
            
            Returns:
                dict: {"images": list[str]} - Base64-encoded PNG images.
            
            Raises:
                HTTPException: 400 if dimensions are invalid.
            """
            # Validate dimensions: Required by FLUX model to ensure compatibility.
            if request.height % 8 != 0 or request.width % 8 != 0:
                raise HTTPException(status_code=400, detail="Height and width must both be multiples of 8")
            
            # Seed calculation: Uses CPU for deterministic RNG; generates sequential seeds for batch.
            generator = [torch.Generator(device="cpu").manual_seed(i) for i in range(request.seed, request.seed + request.batch_size)]
            
            # Image generation: Calls the pipeline with provided params; assumes 'pipeline' is pre-initialized.
            images = pipeline(
                height=request.height,
                width=request.width,
                prompt=request.prompt,
                generator=generator,
                num_inference_steps=request.steps,
                guidance_scale=request.cfg,
                num_images_per_prompt=request.batch_size
            ).images
            
            # Base64 conversion: Encodes images for easy transmission; note for prod: prefer S3 URLs.
            base64_images: List[str] = []
            for image in images:
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                base64_images.append(img_str)
            
            return {
                "images": base64_images,
            }


# image_generation_router = ImageGenerationRouter().router
