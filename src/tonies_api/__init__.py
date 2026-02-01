from .client import TonieAPIClient
from .exceptions import TonieConnectionError, TonieAuthError
from .models import Toniebox, User, Household

__all__ = ["TonieAPIClient", "TonieConnectionError", "TonieAuthError", "Toniebox", "User", "Household"]

__version__ = "0.1.2"

import logging
import os
import sys

# Configure logging
if os.getenv("DEBUG") == "True":
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a handler to print to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    logging.getLogger(__name__).debug("DEBUG mode is enabled.")
else:
    # Optionally, you can configure a default logging level for non-debug mode
    logging.getLogger(__name__).addHandler(logging.NullHandler())
