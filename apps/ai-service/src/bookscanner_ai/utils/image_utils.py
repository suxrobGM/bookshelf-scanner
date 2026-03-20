import base64
from PIL.Image import Image, Resampling
from PIL import ImageOps

def scale_image(image: Image, max_size: tuple[int, int]) -> Image:
    """
    Resize an image to fit within the specified maximum width and height.
    Args:
        image (Image): The input image.
        max_size (tuple[int, int]): The maximum width and height.
    Returns:
        Image: The resized image.
    """
    copied_image = image.copy()
    ImageOps.exif_transpose(copied_image, in_place=True)
    copied_image.thumbnail(max_size, Resampling.LANCZOS)
    return copied_image

def image_to_base64(file_path: str) -> str:
    """
    Convert an image file to a base64 string.
    Args:
        file_path (str): The path to the image file.
    Returns:
        str: The base64 encoded image string.
    """
    with open(file_path, "rb") as img_file:
        base64_data = base64.b64encode(img_file.read()).decode("utf-8")
        return f"data:image/png;base64,{base64_data}"
