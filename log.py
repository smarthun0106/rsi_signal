import logging

def setup_custom_logger(name, log_level=logging.INFO):
    logger = logging.getLogger(name)
    log_format = (
        '%(asctime)s - %(levelname)s - '
        # '[%(filename)s:%(lineno)s - %(funcName)15s() ] - '
        '%(message)s'
    )
    # log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt=log_format)
    # logging.basicConfig(filename='dummy.log', level=logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.setLevel(log_level) # set log level
    logger.addHandler(handler)

    return logger
