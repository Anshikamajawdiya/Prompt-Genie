# import logging
# from app import create_app
# from config import Config

# logging.basicConfig(
#     level   = logging.INFO,
#     format  = "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
#     datefmt = "%Y-%m-%d %H:%M:%S"
# )

# app = create_app()

# if __name__ == "__main__":
#     app.run(
#         host  = "0.0.0.0",    # accessible from Android emulator + real device
#         port  = Config.PORT,
#         debug = Config.DEBUG
#     )


import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from app import create_app
from config import Config

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S"
)

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", Config.PORT))
    app.run(
        host  = "0.0.0.0",
        port  = port,
        debug = Config.DEBUG
    )