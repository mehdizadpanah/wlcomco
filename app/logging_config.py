import logging

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:  # جلوگیری از اضافه کردن چند هندلر تکراری
        handler = logging.FileHandler('/var/log/wlcomco/app.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
