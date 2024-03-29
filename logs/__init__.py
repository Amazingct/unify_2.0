import bugsnag
import json
import logging
from bugsnag.handlers import BugsnagHandler
import os
#dir = "/home/ubuntu/Desktop/unify_2/configurations/"
dir ="/home/amazing/Desktop/PROJECTS_AND_CODES/unify_2/configurations/"



LOG_FORMAT = "/%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename=dir+"logs.log", level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger()


bugsnag.configure(api_key="22177300d77526c97f63abd8dab93752", project_root=dir)
logger = logging.getLogger("unify_2.logger")
handler = BugsnagHandler()
handler.setLevel(logging.ERROR)
logger.addHandler(handler)

email = ""
id = ""


def log_cinfig():
    with open(dir+"user.json", "r") as kiosk:
        k = kiosk.read()
        k = json.loads(k)

    global email, id
    email = k["email"]
    id= k["localId"]


def log(message):
    bugsnag.notify(message, user={"id": id, "email": email})
    logger.info(message)
