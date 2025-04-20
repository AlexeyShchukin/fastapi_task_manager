import logging


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    consol_handler = logging.StreamHandler()
    consol_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("app.log", "w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="""#%(levelname)-8s [%(asctime)s] - %(filename)s:
        %(lineno)d - %(name)s:%(funcName)s - %(message)s"""
    )
    consol_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(consol_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
