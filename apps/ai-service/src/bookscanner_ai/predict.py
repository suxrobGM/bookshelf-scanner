import os
import cv2
import numpy as np
import logging
import asyncio
import torch
from ultralytics import YOLO
from ultralytics.engine.results import Masks, Boxes
from PIL import Image, ImageEnhance
from transformers import AutoModelForCausalLM
from typing import Generator, AsyncGenerator
from torch import Tensor
from .utils import scale_image, image_to_base64, remove_files

YOLO_MODEL = "yolo26x-seg.pt"
MOONDREAM_MODEL_ID = "moondream/moondream3-preview"

BOOK_RECOGNITION_PROMPT = (
    "Recognize the title and author of this book in the format 'Title by Author'. "
    "If there is no author, just the title is fine. "
    "If there's no book in the image, please type 'No book'."
)


class BookPredictor:
    """Predicts the title and author of books in an image."""

    output_dir = os.path.abspath("output")
    yolo_initialized = False
    llm_initialized = False
    logger = logging.getLogger()

    def __init__(self) -> None:
        os.makedirs(f"{self.output_dir}/segmentation", exist_ok=True)

    def load_models(self) -> None:
        """Initialize and load the YOLO and Moondream models."""
        self._init_yolo()
        self._init_llm()

    def predict(self, image_path: str) -> tuple[str, Generator[str, None, None]] | None:
        """Run segmentation + book recognition on an image."""
        segmentation_result = self._segment_and_prepare_books(image_path)

        if segmentation_result is None:
            self.logger.info("No books detected.")
            return None

        yolo_output, cropped_books = segmentation_result

        def result_generator() -> Generator[str, None, None]:
            for i, image_file in enumerate(cropped_books):
                try:
                    response = self._recognize_book(image_file)
                    output = f"Book {i + 1}: {response}"
                    self.logger.info(output)
                    yield output
                except Exception as e:
                    self.logger.error(f"Error processing book {image_file}: {str(e)}")
                    yield f"Error processing book {image_file}: {str(e)}"

        return yolo_output, result_generator()

    async def predict_async(self, image_path: str) -> tuple[str, AsyncGenerator[str, None]] | None:
        """Async version of predict using asyncio.to_thread."""
        self.logger.info(f"Async Processing image: {image_path}")
        segmentation_result = await asyncio.to_thread(self._segment_and_prepare_books, image_path)

        if segmentation_result is None:
            self.logger.info("No books detected.")
            return None

        yolo_output, cropped_books = segmentation_result

        async def result_generator() -> AsyncGenerator[str, None]:
            for i, image_file in enumerate(cropped_books):
                try:
                    response = await asyncio.to_thread(self._recognize_book, image_file)
                    output = f"Book {i + 1}: {response}"
                    self.logger.info(output)
                    yield output
                except Exception as e:
                    error_message = f"Error processing book {image_file}: {str(e)}"
                    self.logger.error(error_message)
                    yield error_message

        return yolo_output, result_generator()

    def cleanup(self) -> None:
        """Remove all files in the output directory."""
        remove_files(self.output_dir)
        remove_files(f"{self.output_dir}/segmentation")
        self.logger.info("Output directory cleaned up.")

    def _init_yolo(self) -> None:
        """Initialize the YOLO model for book segmentation."""
        if self.yolo_initialized:
            return

        self.yolo_model = YOLO(YOLO_MODEL, task="segment")
        self.yolo_initialized = True
        self.logger.info("YOLO model initialized.")

    def _init_llm(self) -> None:
        """Initialize the Moondream v3 model for book recognition."""
        if self.llm_initialized:
            return

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if device == "cuda" else torch.float32

        self.logger.info(f"Loading Moondream v3 from HuggingFace ({device}, {dtype})...")
        self.moondream = AutoModelForCausalLM.from_pretrained(
            MOONDREAM_MODEL_ID,
            trust_remote_code=True,
            dtype=dtype,
            device_map={"": device},
        )

        if device == "cuda":
            self.moondream.compile()

        self.llm_initialized = True
        self.logger.info("Moondream v3 model initialized.")

    def _segment_and_prepare_books(self, image_path: str) -> tuple[str, list[str]] | None:
        """Segment books with YOLO and return base64 annotated image + cropped book paths."""
        original_image = Image.open(image_path)
        scaled_image: Image.Image

        if original_image.size[0] > 2560 or original_image.size[1] > 2560:
            scaled_image = scale_image(original_image, (2560, 2560))
        else:
            scaled_image = original_image
            if scaled_image.width > scaled_image.height:
                scaled_image = scaled_image.rotate(-90, expand=True)

        enhanced_image = self._enhance_image(scaled_image)
        enhanced_image = self._reduce_noise(enhanced_image)

        image_filename = os.path.basename(image_path)
        segmentation_mask_data = self._segment_books(enhanced_image, image_filename)

        if not segmentation_mask_data:
            return None

        cropped_books: list[str] = []
        masks, boxes = segmentation_mask_data

        for i, (mask, box) in enumerate(zip(masks.data, boxes)):  # type: ignore
            mask: Tensor
            box: Boxes

            cropped_image = self._mask_and_crop(enhanced_image, mask, box)
            cropped_image = self._rotate_if_spine(cropped_image, box)
            cropped_image_path = os.path.abspath(f"{self.output_dir}/book_{i + 1}.png")

            cropped_image.save(cropped_image_path)
            cropped_books.append(cropped_image_path)

        segmented_image_path = os.path.join(self.output_dir, "segmentation", image_filename)
        self.logger.info(f"Segmented image saved to {segmented_image_path}")
        segmented_image_encoded = image_to_base64(segmented_image_path)

        return segmented_image_encoded, cropped_books

    def _segment_books(self, image: Image.Image, image_filename: str) -> tuple[Masks, Boxes] | None:
        """Segment books using the YOLO model."""
        if not self.yolo_initialized:
            raise ValueError("YOLO model is not initialized, please call load_models() first.")

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
        """Enhance contrast and brightness for better recognition."""
        image = ImageEnhance.Contrast(image).enhance(1.5)
        image = ImageEnhance.Brightness(image).enhance(1.1)
        return image

    def _reduce_noise(self, image: Image.Image) -> Image.Image:
        """Apply noise reduction using OpenCV's fastNlMeansDenoisingColored."""
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        image_cv = cv2.fastNlMeansDenoisingColored(image_cv, None, 10, 10, 7, 21)
        return Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

    def _mask_and_crop(self, image: Image.Image, mask_data: Tensor, box_data: Boxes) -> Image.Image:
        """Apply segmentation mask and crop to bounding box."""
        mask = Image.fromarray(mask_data.cpu().numpy().astype("uint8") * 255)

        masked_image = Image.new("RGB", image.size)
        masked_image.paste(image, mask=mask)

        x1, y1, x2, y2 = map(int, box_data.xyxy[0])
        cropped_image = masked_image.crop((x1, y1, x2, y2))
        return cropped_image

    def _recognize_book(self, image_path: str) -> str:
        """Recognize the title and author of a book using Moondream v3."""
        if not self.llm_initialized:
            raise ValueError("Moondream model is not initialized, please call load_models() first.")

        image = Image.open(image_path)
        result = self.moondream.query(image=image, question=BOOK_RECOGNITION_PROMPT, reasoning=False)
        return result["answer"].strip()

    def _rotate_if_spine(self, image: Image.Image, box_data: Boxes, threshold: float = 2.0) -> Image.Image:
        """Rotate the image if it's likely a book spine based on aspect ratio."""
        x1, y1, x2, y2 = box_data.xyxy[0]
        width, height = x2 - x1, y2 - y1
        aspect_ratio = height / width

        if aspect_ratio > threshold:
            return image.rotate(90, expand=True)

        return image
