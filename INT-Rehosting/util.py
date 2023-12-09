
import logging
import avatar2

VECTOR_TABLE_OFFSET_REG = 0xe000ed08

class CustomFormatter(logging.Formatter):

    green = "\x1b[32;20m"
    grey = "\x1b[37;20m"
    yellow = "\x1b[33;20m"
    blue = "\x1b[34;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_time = "%(asctime)s"
    format_level = "%(levelname)s"
    format_source = "%(name)s"
    format_message = "%(message)s"
    format = f"{format_time} | {format_source} | {format_level} | {format_message}"

    FORMATS = {
        logging.NOTSET: grey + format + reset,
        logging.DEBUG: f"{grey}{format_time} | {format_source}{green} | {format_level} | {grey}{format_message}{reset}",
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS[record.levelno]
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def pretty_logging_setup(logger: logging.Logger, level):
    # Create handler which will catch every message
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(CustomFormatter())
    # Assign this handler to the logger
    logger.addHandler(ch)

    return logger


def setup_loggers(avatar=True, script=True, emulated_logger=False):
    res = []
    if avatar:
        logger = logging.getLogger('avatar')
        logger.setLevel(logging.INFO)
        pretty_logging_setup(logger, logging.INFO)
        res.append(logger)

    if script:
        logger = logging.getLogger('script')
        logger.setLevel(logging.DEBUG)
        logger = pretty_logging_setup(logger, logging.DEBUG)
        logger.root.handlers.clear()
        res.append(logger)

    if emulated_logger:
        logger = logging.getLogger('emulated')
        logger.setLevel(logging.DEBUG)
        logger = pretty_logging_setup(logger, logging.DEBUG)
        logger.root.handlers.clear()
        res.append(logger)

    return res

def getVTOR(device: avatar2.Target):
    return device.read_memory(VECTOR_TABLE_OFFSET_REG, 4)


def printVT(device: avatar2.Target, irq_map):
    vt_offset = getVTOR(device)
    print(f"Vector table is at address 0x{vt_offset:x}")

    # The last 4 bytes contain the end of RAM address
    vector_table = device.read_memory(
        vt_offset, size=4, num_words=48)  # 48 = 16 cpu internal + 32 user interrupts
    print(f"Vector table:")
    print(f"  Address      [irq--num] --  target      --  label")
    for i, entry in enumerate(vector_table):
        if entry - 1 in irq_map:
            label = "\x1b[32m" + irq_map[entry - 1] + "\x1b[0m"
        else:
            label = "\x1b[33;1munknown\x1b[0m"
        print(
            f"    0x{vt_offset + i * 4:8x} [{i:2d} / {(i - 16):3d}] --  0x{entry:8x}  --  {label}")
