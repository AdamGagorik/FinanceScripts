"""
A script to save a accounts CSV for the current date.
"""
import datetime
import logging
import typing


import finance.config


def yyyy_mm_dd(v: str) -> datetime.datetime:
    """
    Convert argparse string to datetime.
    """
    return datetime.datetime.strptime(v, '%Y-%m-%d')


def run(main: typing.Callable, args: typing.Callable, exiting: bool = True) -> int:
    """
    A helper method to execute the main function of a script.

    Parameters:
         main: The main script function.
         args: The command line arguments method.
         exiting: This method will run sys.exit?

    Returns:
        The exitcode, which is >= 0 if the program succeeded.
    """
    exitcode: int = 0

    # noinspection PyBroadException
    try:
        finance.config.logging()
        finance.config.pandas()
        main(**args().__dict__)
    except Exception:
        logging.exception('caught unhandled exception!')
        exitcode = -1

    if exiting:
        exit(exitcode)
    else:
        return exitcode
