import logging
import re
from instapush import App


class WrongMessageCountException(Exception):
    pass


class ApiException(Exception):
    pass


def notify(title, message, event_name, appid, secret, trackers, retcode=None):
    """
    Required parameter:
        * ``event_name`` - Instapush event (the notification template)
        * ``appid`` - The appid found on the dashboard
        * ``secret`` - The secret found on the dashboard
        * ``trackers`` - List of the placeholders for the selected event
    """

    logger = logging.getLogger(__name__)

    msgs = [msg.replace("\\:", ":") for msg in re.split(r'(?<!\\):', message)]

    if len(msgs) != len(trackers):
        logger.error("Wrong number of messages! There are {} trackers so you "
                     "have to provide {} messages. Remember to separate each "
                     "message with ':' (example: send 'msg1:msg2'). You can "
                     "escape ':' with '\', so send 'message\: detail' would "
                     "be one message.".format(len(trackers), len(trackers)))
        raise WrongMessageCountException()

    to_send = dict(zip(trackers, msgs))
    app = App(appid=appid, secret=secret)
    res = app.notify(event_name=event_name, trackers=to_send)

    if res["status"] != 200:
        logger.error("{:d}: {}".format(res["status"], res["msg"]))
        raise ApiException()
