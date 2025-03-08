from loguru import logger
from dotenv import load_dotenv
from os import getenv
from sys import stdout

logger.remove(0)
logger.add(stdout, level=getenv('LOGLEVEL', 'info').upper(), format='<magenta>[{time:HH:mm:ss}]</magenta> <orange>')