from .homebase import HomeBase
from .config import config

if __name__ == "__main__":
    import logging

    logger = logging.getLogger('homebase')
    logger.setLevel(config['loglevel'])
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    hb = HomeBase(config)
    hb.run()
