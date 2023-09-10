import logging
import json

# Colourful Formatting for the terminal
class VerboseColourfulFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = "%(asctime)s::%(name)s::%(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: green + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset
    }

    def format(self, record : logging.LogRecord):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Black and White Formatting for Files
class VerboseBWFormatter(logging.Formatter):
    fmt = '%(asctime)s::%(name)s::%(levelname)s| %(message)s (%(filename)s:%(lineno)d)'
    def format(self, record : logging.LogRecord):
        formatter = logging.Formatter(self.fmt)
        return formatter.format(record)

class SimpleBWFormatter(logging.Formatter):
    fmt = '%(message)s'
    def format(self, record : logging.LogRecord):
        formatter = logging.Formatter(self.fmt)
        formatted = formatter.format(record)
        return formatted

# Frontend Display Filter
class FrontendFormatter(logging.Formatter):
    fmt = '%(message)s'
    def format(self, record : logging.LogRecord):
        formatter   = logging.Formatter(self.fmt)
        load        = formatter.format(record)
        try:
            json.loads(load)
        except json.JSONDecodeError:
            typ = 'warn'
            load= json.dumps({
                'type' : typ, 'msg' : load
            })
        return load