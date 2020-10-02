import logging
from nixnetconfig.parser import get_parser
from nixnetconfig import utilities
import sys


logger = logging.getLogger('nixnetconfig')


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    configure_logger(args)

    try:
        args.command(**get_command_arguments(args))

        if args.enumerate:
            utilities.enumerate_xnet_devices()

    except utilities.XnetConfigError as err:
        logger.error(err.message, exc_info=(logger.getEffectiveLevel() == logging.DEBUG))
        sys.exit(1)

    except Exception:
        logger.error('Operation failed', exc_info=(logger.getEffectiveLevel() == logging.DEBUG))
        sys.exit(1)


def get_command_arguments(args):
    arguments = vars(args).copy()
    for ignore_argument in ('verbose', 'command', 'enumerate'):
        arguments.pop(ignore_argument, None)
    return arguments


def configure_logger(args):
    class InfoFilter(logging.Filter):
        def filter(self, rec):
            return rec.levelno in (logging.DEBUG, logging.INFO)

    formatter = logging.Formatter('%(levelname)s: %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(InfoFilter())
    stdout_handler.setFormatter(formatter)

    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)

    logger.setLevel(
        {0: logging.ERROR,
         1: logging.INFO,
         2: logging.DEBUG,
         }.get(args.verbose, 0))
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)


def parse_args(argv=sys.argv[1:]):
    parser = get_parser()

    return parser.parse_args(argv)


if __name__ == "__main__":  # pragma: no cover
    main()
