import logging
log = logging.getLogger('django')


def log_django(data, error=False):
    data = str(data)
    if error is False:
        log.warning(data)
    else:
        log.error(data)