from os import environ

__all__ = [
    "OTON_LOG_LEVEL",
    "OTON_LOG_FORMAT",
]

OTON_LOG_LEVEL = environ.get("OTON_LOG_LEVEL", "INFO")
OTON_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s:%(funcName)s: %(lineno)s: %(message)s'
