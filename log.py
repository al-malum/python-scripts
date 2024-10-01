import logging

FILENAME = 'test.log'


logger = logging.getLogger('handler')
logger.setLevel(logging.WARNING)
logger_handler = logging.FileHandler(f'{FILENAME}')
logger_handler.setLevel(logging.WARNING)
logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)

