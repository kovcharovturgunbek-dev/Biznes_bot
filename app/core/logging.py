import logging
import sys


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


def setup_logging() -> None:
    """
    Bozorchi uchun markaziy log tizimini sozlaydi.

    Loglar standart chiqish oqimiga (stdout) yoziladi.
    Bu Render va boshqa serverlarda loglarni kuzatish imkonini beradi.
    """

    root_logger = logging.getLogger()

    # Log darajasi
    root_logger.setLevel(logging.INFO)

    # Takroriy handler qo'shilishining oldini olish
    handler_exists = any(
        getattr(handler, "_bozorchi_handler", False)
        for handler in root_logger.handlers
    )

    if not handler_exists:
        console_handler = logging.StreamHandler(sys.stdout)

        console_handler.setLevel(logging.INFO)

        console_handler.setFormatter(
            logging.Formatter(
                fmt=LOG_FORMAT,
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        # Ushbu handler Bozorchi uchun yaratilganini belgilash
        console_handler._bozorchi_handler = True

        root_logger.addHandler(console_handler)

    # Python ogohlantirishlarini ham log tizimiga yo'naltirish
    logging.captureWarnings(True)

    # Keraksiz texnik loglarni cheklash
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    root_logger.info("Bozorchi log tizimi ishga tushdi.")
