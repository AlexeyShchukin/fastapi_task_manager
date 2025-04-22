import logging


def setup_logger():
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)

    consol_handler = logging.StreamHandler()
    consol_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler("app.log", "w", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(datefmt="%Y-%m-%d %H:%M:%S",
        fmt="[%(asctime)s.%(msecs)03d] %(filename)18s:%(lineno)-3d %(levelname)-8s - %(message)s"
    )
    consol_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    log.addHandler(consol_handler)
    log.addHandler(file_handler)

    return log


logger = setup_logger()
