import base64
import logging
import os
import tempfile
from typing import Iterator

import grpc

from .bookscanner_ai import BookPredictor
from .generated.bookscanner.v1 import prediction_pb2, prediction_pb2_grpc

logger = logging.getLogger(__name__)


class PredictionServicer(prediction_pb2_grpc.PredictionServiceServicer):
    def __init__(self) -> None:
        self.predictor = BookPredictor()
        self.predictor.load_models()
        logger.info("PredictionServicer initialized with models loaded.")

    def Predict(
        self,
        request: prediction_pb2.PredictRequest,
        context: grpc.ServicerContext,
    ) -> Iterator[prediction_pb2.PredictResponse]:
        """Handle a prediction request by streaming back segmentation + book results."""
        temp_path = None

        try:
            # Save uploaded image bytes to a temp file
            suffix = os.path.splitext(request.filename)[1] or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(request.image_data)
                temp_path = tmp.name

            logger.info(f"Processing image: {request.filename} ({len(request.image_data)} bytes)")

            # Run prediction (synchronous — runs on gRPC thread pool)
            result = self.predictor.predict(temp_path)

            if result is None:
                yield prediction_pb2.PredictResponse(
                    error=prediction_pb2.ErrorResult(message="No books detected in the image.")
                )
                return

            segmented_base64, book_generator = result

            # Extract raw PNG bytes from the base64 data URL
            # Format: "data:image/png;base64,<data>"
            if "," in segmented_base64:
                image_bytes = base64.b64decode(segmented_base64.split(",", 1)[1])
            else:
                image_bytes = base64.b64decode(segmented_base64)

            # First message: segmented image
            yield prediction_pb2.PredictResponse(
                segmentation=prediction_pb2.SegmentationResult(
                    segmented_image=image_bytes,
                    book_count=0,  # count is not known upfront
                )
            )

            # Subsequent messages: one per book
            for book_text in book_generator:
                if context.is_active():
                    yield prediction_pb2.PredictResponse(
                        book=prediction_pb2.BookResult(
                            book_number=_extract_book_number(book_text),
                            raw_text=book_text,
                        )
                    )
                else:
                    logger.info("Client disconnected, stopping prediction stream.")
                    break

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            yield prediction_pb2.PredictResponse(error=prediction_pb2.ErrorResult(message=str(e)))
        finally:
            self.predictor.cleanup()
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)


def _extract_book_number(text: str) -> int:
    """Extract book number from text like 'Book 1: Title by Author'."""
    try:
        if text.startswith("Book "):
            num_str = text.split(":")[0].replace("Book ", "")
            return int(num_str)
    except (ValueError, IndexError):
        pass
    return 0
