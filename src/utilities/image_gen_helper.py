import os
import time

from src.utilities.logger import setup_logger

logger = setup_logger("image_saving_logger")

def save_image_bytes(image_bytes, directory="artifacts/generated_images"):
    """
    Saves image bytes to a file in the specified directory.

    Args:
        image_bytes (bytes): The image data to be saved.
        directory (str, optional): The directory where the image will be saved.
            Defaults to "artifacts/generated_images".

    Returns:
        str: The file path of the saved image.

    Side Effects:
        Creates the target directory if it does not exist.
    """
    os.makedirs(directory, exist_ok=True)
    filename = f"generated_image_{int(time.time())}.png"
    filepath = os.path.join(directory, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    logger.info(f"Image saved to {filepath}")
    return filepath
