import logging

import grpc
from concurrent import futures

from .logger import setup_logging
from .generated.bookscanner.v1 import prediction_pb2_grpc
from .servicer import PredictionServicer

_PORT = 4001
_MAX_MESSAGE_SIZE = 20 * 1024 * 1024  # 20MB

setup_logging()
logger = logging.getLogger(__name__)


def serve() -> None:
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=4),
        options=[
            ("grpc.max_send_message_length", _MAX_MESSAGE_SIZE),
            ("grpc.max_receive_message_length", _MAX_MESSAGE_SIZE),
        ],
    )

    servicer = PredictionServicer()
    prediction_pb2_grpc.add_PredictionServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{_PORT}")
    server.start()
    logger.info(f"AI gRPC service listening on port {_PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
