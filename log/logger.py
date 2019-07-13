"""Logger setup configuration module"""
import os
import yaml
from copy import deepcopy
from utils.utils import get_root


def setup_logger() -> dict:
    """Logger setup configuration. Returns logger configuration"""
    # Get log directory path
    log_root = get_root()

    # Load logger configuration
    with open(os.path.join(log_root, 'log', 'logging.yaml'), 'rt') as log_conf:
        log_config = yaml.load(log_conf.read())

    # Get handlers and loggers from configuration
    handlers = log_config.pop('handlers', {})
    loggers = log_config.get('loggers', {})

    new_handlers = {}

    # Setup files location and handler for each logger defined
    for logger_name, logger_config in loggers.items():
        new_handler_names = []
        for handler in logger_config.pop('handlers'):
            log_conf = deepcopy(handlers[handler])
            log_dir = log_conf.pop('log_dir', None)

            log_dir = log_dir if log_dir else 'applog'
            log_dir = os.path.join(log_root, log_dir, logger_name)
            log_file = log_conf.get('filename')

            if log_file:
                log_file = os.path.join(log_dir, log_file)
                # Create log directory if not exists
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                log_conf['filename'] = log_file

            new_name = '{}_{}'.format(handler, logger_name)
            new_handler_names.append(new_name)
            new_handlers[new_name] = log_conf

        logger_config['handlers'] = new_handler_names

    log_config['handlers'] = new_handlers

    # Return logger configuration
    return log_config
