import asyncio
import logging
import os
from typing import AsyncGenerator, Generator

import cv2
import httpx
import numpy as np
from dotenv import load_dotenv
from PIL import Image, ImageEnhance
from torch import Tensor
from ultralytics import YOLO
from ultralytics.engine.results import Boxes, Masks

from .utils import image_to_base64, remove_files, scale_image

load_dotenv()

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))
YOLO_MODEL = os.path.join(MODELS_DIR, "yolo26x-seg.pt")

LLAMA_SERVER_URL = os.environ.get("LLAMA_SERVER_URL", "http://localhost:4000")

BOOK_RECOGNITION_PROMPT = (
    "Read the text on this book spine or cover. "
    "Return only the title and author in the format 'Title by Author'. "
    "If you can't identify the author, return just the title. "
    "If there is no book, respond with 'No book'."
)


class BookPredictor:
    """Predicts the title and author of books in an image."""

    output_dir = os.path.abspath("output")
    yolo_initialized = False
    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        os.makedirs(f"{self.output_dir}/segmentation", exist_ok=True)
        self.http_client = httpx.Client(base_url=LLAMA_SERVER_URL, timeout=120.0)

    def load_models(self) -> None:
        """Initialize YOLO and verify llama-server is reachable."""
        self._init_yolo()
        self._check_llama_server()

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

    def _check_llama_server(self) -> None:
        """Verify that llama-server is running and reachable."""
        try:
            resp = self.http_client.get("/health")
            resp.raise_for_status()
            self.logger.info(f"llama-server connected at {LLAMA_SERVER_URL}")
        except httpx.ConnectError:
            self.logger.warning(
                f"llama-server not reachable at {LLAMA_SERVER_URL}. "
                "Start it with: pdm run llama-server"
            )

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
        """Recognize the title and author of a book via llama-server."""
        image_data_url = image_to_base64(image_path)

        resp = self.http_client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_data_url}},
                            {"type": "text", "text": BOOK_RECOGNITION_PROMPT},
                        ],
                    }
                ],
                "max_tokens": 64,
                "temperature": 0.1,
            },
        )
        resp.raise_for_status()

        return resp.json()["choices"][0]["message"]["content"].strip()

    def _rotate_if_spine(
        self, image: Image.Image, box_data: Boxes, threshold: float = 2.0
    ) -> Image.Image:
        """Rotate the image if it's likely a book spine based on aspect ratio."""
        x1, y1, x2, y2 = box_data.xyxy[0]
        width, height = x2 - x1, y2 - y1
        aspect_ratio = height / width

        if aspect_ratio > threshold:
            return image.rotate(90, expand=True)

        return image
