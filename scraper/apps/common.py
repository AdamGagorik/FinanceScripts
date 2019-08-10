"""
A script to save a accounts CSV for the current date.
"""
import logging
import typing


import scraper.config


def run(main: typing.Callable, args: typing.Callable):
    """
    A helper method to execute the main function of a script.

    Parameters:
         main: The main script function.
         args: The command line arguments method.
    """
    # noinspection PyBroadException
    try:
        scraper.config.logging()
        scraper.config.pandas()
        main(**args().__dict__)
    except Exception:
        logging.exception('caught unhandled exception!')
        exit(-1)
    exit(0)
