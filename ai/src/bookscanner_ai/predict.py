import asyncio
import os
import cv2
import re
import numpy as np
import logging
from ultralytics import YOLO
from ultralytics.engine.results import Masks, Boxes
from PIL import Image, ImageEnhance
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler, MoondreamChatHandler
from typing import AsyncGenerator
from torch import Tensor
from .utils import scale_image, image_to_base64, remove_files

class BookPredictor:
    """
    A class to predict the title and author of books in an image.
    """
    yolo_model: YOLO
    llm: Llama
    chat_handler: Llava15ChatHandler
    prompt: str
    output_dir = os.path.abspath("output")
    yolo_initialized = False
    llm_initialized = False
    logger = logging.getLogger()

    def __init__(self) -> None:
        # Ensure the output directory exists
        os.makedirs(f"{self.output_dir}/segmentation", exist_ok=True)
        
        self.prompt = """Recognize the title and author of this book in the format 'Title by Author'. 
            If there is no author, just the title is fine. 
            If there's no book in the image, please type 'No book'."""

    async def predict(self, image_path: str) -> tuple[str | None, AsyncGenerator[str, None]]:
        """
        Asynchronously predict the title and author of the books in the image.
        Args:
            image_path (str): The path to the image file.
        Yields:
            tuple[str | None, AsyncGenerator[str, None]]: 
            A tuple containing the YOLO segmented image (as base64 string) and an async generator of results.
            If no books are detected, the YOLO segmented image will be None.
        """
        loop = asyncio.get_event_loop()

        # Run segmentation and get the YOLO output (segmented image in base64)
        segmentation_result = await loop.run_in_executor(None, self._segment_and_prepare_books, image_path)

        if segmentation_result is None:
            self.logger.info("No books detected.")
            return None, None
        
        yolo_output, cropped_books = segmentation_result

        # Define the async generator for the prediction results
        async def result_generator() -> AsyncGenerator[str, None]:
            for i, image_file in enumerate(cropped_books):
                try:
                    response = await loop.run_in_executor(None, self._recognize_book, image_file)
                    output = f"Book {i + 1}: {response}"
                    self.logger.info(output)
                    yield output
                except Exception as e:
                    self.logger.error(f"Error processing book {image_file}: {str(e)}")
                    yield f"Error processing book {image_file}: {str(e)}"

        return yolo_output, result_generator()
    
    def cleanup(self) -> None:
        """
        Remove all files in the output directory.
        """
        remove_files(self.output_dir)
        remove_files(f"{self.output_dir}/segmentation")
        self.logger.info("Output directory cleaned up.")
    
    def _init_yolo(self) -> None:
        """
        Try initialize the YOLO model for book segmentation.
        """
        if self.yolo_initialized:
            return

        self.yolo_model = YOLO("models/yolo11x-seg.pt", task="segment")
        self.yolo_initialized = True
        self.logger.info("YOLO model initialized.")

    def _init_llm(self) -> None:
        """
        Try initialize the Moondream model for OCR.
        """
        if self.llm_initialized:
            return
        
        self.chat_handler = MoondreamChatHandler.from_pretrained(
            repo_id="vikhyatk/moondream2",
            filename="moondream2-mmproj-f16.gguf",
            verbose=False,
        )
        self.llm = Llama.from_pretrained(
            repo_id="vikhyatk/moondream2",
            filename="moondream2-text-model-f16.gguf",
            chat_handler=self.chat_handler,
            n_ctx=2048,
        )
        self.llm_initialized = True
        self.logger.info("Moondream2 model initialized.")

    def _segment_and_prepare_books(self, image_path: str) -> tuple[str, list[str]] | None:
        """
        Segments the image using YOLO, processes each detected book, saves the segmented image,
        and returns it as a base64 string.
        Args:
            image_path (str): Path to the image file.
        Returns:
            tuple[str, list[str]] | None: 
            Base64 encoded segmented image and list of cropped books image paths if books are detected, else None.
        """
        original_image = Image.open(image_path)
        scaled_image: Image.Image

        # Scale the image if it's too large
        if original_image.size[0] > 2560 or original_image.size[1] > 2560:
            scaled_image = scale_image(original_image, (2560, 2560))
        else:
            scaled_image = original_image
            # Rotate if image in landscape
            if scaled_image.width > scaled_image.height:
                scaled_image = scaled_image.rotate(-90, expand=True)

        enhanced_image = self._enhance_image(scaled_image)
        enhanced_image = self._reduce_noise(enhanced_image)

        image_filename = os.path.basename(image_path)
        segmentation_mask_data = self._segment_books(enhanced_image, image_filename)

        if not segmentation_mask_data:
            # No books detected
            return None
        
        # Store paths of cropped books
        cropped_books: list[str] = []
        masks, boxes = segmentation_mask_data
        
        # Loop over each detected book and save the cropped image in the output directory
        for i, (mask, box) in enumerate(zip(masks.data, boxes)):
            mask: Tensor
            box: Boxes
            
            cropped_image = self._mask_and_crop(enhanced_image, mask, box)

            # Rotate the image if it's identified as a spine
            cropped_image = self._rotate_if_spine(cropped_image, box)
            cropped_image_path = os.path.abspath(f"{self.output_dir}/book_{i + 1}.png")

            # Save the cropped image and mask
            cropped_image.save(cropped_image_path)
            cropped_books.append(cropped_image_path)

        # Save the segmented image in the output/segmentation directory
        segmented_image_path = os.path.join(self.output_dir, "segmentation", image_filename)
        self.logger.info(f"Segmented image saved to {segmented_image_path}")
        segmented_image_encoded = image_to_base64(segmented_image_path)

        # Convert the segmented image to base64
        return segmented_image_encoded, cropped_books
    
    def _segment_books(self, image: Image.Image, image_filename: str) -> tuple[Masks, Boxes] | None:
        """
        Segment the books in the image using the YOLO model.
        Args:
            image (Image): The image to segment.
            image_filename (str): The filename of the image to save the results.
        Returns:
            tuple[Masks, Boxes]: The segmentation masks and bounding boxes. If no books are detected, returns None.
        """
        self._init_yolo()

        results = self.yolo_model.predict(
            image,
            imgsz=image.size[0],
            half=True,
            classes=[73],
            retina_masks=True,
            conf=0.25,
        )

        results = results[0]
        masks = results.masks
        boxes = results.boxes
        
        results.save(f"{self.output_dir}/segmentation/{image_filename}")

        if not masks or not boxes:
            return None

        return masks, boxes

    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """
        Enhance contrast and sharpness of the image for better OCR results.
        Args:
            image (Image): The image to enhance.
        Returns:
            Image: The enhanced PIL image.
        """
        image = ImageEnhance.Contrast(image).enhance(1.5)
        image = ImageEnhance.Brightness(image).enhance(1.1)
        #image = ImageEnhance.Sharpness(image).enhance(2)
        return image
    
    def _reduce_noise(self, image: Image.Image) -> Image.Image:
        """
        Apply noise reduction to the image. Uses OpenCV's fastNlMeansDenoisingColored function.
        Args:
            image (Image): The input image.
        Returns:
            Image: The denoised image.
        """
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        image_cv = cv2.fastNlMeansDenoisingColored(image_cv, None, 10, 10, 7, 21)
        return Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
    
    def _mask_and_crop(self, image: Image.Image, mask_data: Masks, box_data: Boxes) -> Image.Image:
        """
        Mask and crop the image using the mask and bounding box.
        Args:
            image (Image): The input image.
            mask_data (Masks): Segmentation mask data.
            box_data (Boxes): Segmentation bounding box.
        Returns:
            Image: The cropped and masked image.
        """
        # Convert mask to a PIL Image
        mask = Image.fromarray(mask_data.cpu().numpy().astype("uint8") * 255)

        # Create a new image for the masked book
        masked_image = Image.new("RGB", image.size)
        masked_image.paste(image, mask=mask)

        # Crop the image to the bounding box for efficiency
        x1, y1, x2, y2 = map(int, box_data.xyxy[0])
        cropped_image = masked_image.crop((x1, y1, x2, y2))
        return cropped_image
    
    def _recognize_book(self, image_path: str) -> str:
        """
        Recognize the title and author of the book in the image using the Moondream model.
        Args:
            image (str): The path to the image book image.
        Returns:
            str: The recognized title and author of the book.
        """
        self._init_llm()

        response = self.llm.create_chat_completion(messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": self.prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image_to_base64(image_path)}
                }
            ]
        }])

        message_content: str = response["choices"][0]["message"]["content"] # type: ignore
        return message_content.strip()
    
    def _rotate_if_spine(self, image: Image.Image, box_data: Boxes, threshold = 2.0) -> Image.Image:
        """
        Rotates the image if it is likely a book spine based on the aspect ratio.
        
        Args:
            image (Image): The cropped book image.
            box (Boxes): Bounding box data.
            threshold (float): Aspect ratio threshold to classify as spine.
        
        Returns:
            Image: The rotated or unrotated image.
        """
        x1, y1, x2, y2 = box_data.xyxy[0]
        width, height = x2 - x1, y2 - y1
        aspect_ratio = height / width

        if aspect_ratio > threshold:
            return image.rotate(90, expand=True)
        
        return image
