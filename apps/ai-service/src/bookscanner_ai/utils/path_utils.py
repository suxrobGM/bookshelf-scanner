import os

def get_image_path(image_file: str) -> str:
    """
    Get the full path of the image in the dataset/images directory.
    Args:
        image_file (str): The name of the image file including the extension.
    Returns:
        str: The full path of the image file.
    Raises:
        FileNotFoundError: If the image file is not found.
    """
    image_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "../../../dataset/images", image_file))

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_file}")
    
    return image_path

def get_model_path(model_file: str) -> str:
    """
    Get the full path of the model in the models directory.
    Args:
        model_file (str): The name of the model file including the extension.
    Returns:
        str: The full path of the model file.
    Raises:
        FileNotFoundError: If the model file is not found.
    """
    model_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "../../../models", model_file))

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_file}")
    
    return model_path

def remove_files(dir_path: str) -> None:
    """
    Remove all files in a directory.
    Args:
        dir_path (str): The path to the directory.
    """
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
