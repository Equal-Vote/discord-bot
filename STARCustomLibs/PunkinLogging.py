import logging
import os
from dotenv import load_dotenv
from datetime import datetime

#small class for making logging easier and consistent

class logWrapper():
    def __init__(self):
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename = os.getenv("BOT_LOG_PATH"), encoding = "utf-8", level = logging.DEBUG)
    
    #Is there a lead (such as ballot ID), whats the main focus of your logging event, and what type (info, warn, etc)
    def log(self, log: str = "", type: str = "info", lead: str = ""):
        content = f"[{datetime.now()}]{lead}:{log}"
        print(content)
        if type == "info":
            self.logger.info(content)
        elif type == "debug":
            self.logger.debug(content)
        elif type == "warning":
            self.logger.warning(content)
        elif type == "error":
            self.logger.error(content)
