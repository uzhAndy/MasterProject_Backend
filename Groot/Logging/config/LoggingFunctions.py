import logging

file_logger = logging.getLogger('log_file')
console_logger = logging.getLogger('console')

def log_info(message):
    file_logger.info(message)

def log_warning(message):
    file_logger.warning(message)

def log_error(message):
    file_logger.error(message)


def print_info(message):
    log_info(message)
    console_logger.info(message)

def print_error(message):
    console_logger.error(message)