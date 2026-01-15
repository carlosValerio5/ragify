import logging
from logging import Formatter, StreamHandler
import sys

formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)

def setup_logging():
    logging.basicConfig(handlers=[handler])
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger