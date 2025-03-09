import logging
import random

logging.basicConfig(filename='python-neutralino.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)
FileOutputHandler = logging.FileHandler('python-neutralino.log')
logger.addHandler(FileOutputHandler)

logger.info("test")

def test(d):
    logger.info("test from frontend")
    logger.info(d)
    logger.info(random.randint(0, 100))