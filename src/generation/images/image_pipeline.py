from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
import psutil
import os
import torch

def initialize_pipeline():
    """
    Initializes and configures the Stable Diffusion pipeline (free model).
    
    Loads the model with optimizations (e.g., fp16, attention slicing for low RAM).
    Returns the pipeline ready for image generation.
    
    Returns:
        StableDiffusionPipeline: Configured pipeline instance.
    """
    device_arg = os.getenv("DEVICE", None)
    if device_arg:
        device = torch.device(device_arg)
    else:
        if torch.cuda.is_available():
            device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")

    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    
    model_name = "runwayml/stable-diffusion-v1-5"  # Free, non-gated model.
    
    pipeline = StableDiffusionPipeline.from_pretrained(
        model_name,
        torch_dtype=torch.float16,  # Reduces VRAM usage with minimal quality loss.
        use_safetensors=True,       # Ensures safe model loading.
        scheduler=EulerDiscreteScheduler()  # Compatible scheduler for Stable Diffusion.
    ).to(device)
    
    # Enable attention slicing for low-RAM environments to prevent OOM errors.
    total_memory = psutil.virtual_memory().total
    total_memory_gb = total_memory / (1024 ** 3)
    if (device in ['cpu', 'mps']) and total_memory_gb < 64:
        print("Enabling attention slicing")
        pipeline.enable_attention_slicing()
    
    return pipeline

# Global pipeline: Load once at import time (or app startup) for efficiency.
pipeline = initialize_pipeline()
