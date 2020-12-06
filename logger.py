import logging

def get_logger(problem):

    fmt = f"[{problem}]" + " %(asctime)s - %(levelname)s : %(message)s"
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt=fmt,
            datefmt="%d/%m/%Y %I:%M:%S %p",
        )
    )
    logger.addHandler(handler)
    return logger
