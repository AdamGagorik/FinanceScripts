"""
The scraper configuration.
"""
import dataclasses
import datetime
import dotenv
import os


def nowtime() -> datetime.datetime:
    """
    Get the current time.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)


@dataclasses.dataclass()
class BaseConfig:
    """
    The scraper configuration.
    """
    #: The working directory
    workdir: str = dataclasses.field(default_factory=lambda: os.getcwd())
    #: The path to the personal capital environment files
    environ: str = dataclasses.field(init=False, default='.env')
    #: The time at configuration creation
    dt: datetime.datetime = dataclasses.field(init=False, default_factory=nowtime)

    def getpath(self, *args, **kwargs) -> str:
        """
        Create an output path string.
        """
        path: str = os.path.abspath(os.path.join(*args).format(self=self, dt=self.dt, **kwargs))

        # create root directory
        root: str = os.path.dirname(path)
        if not os.path.exists(root):
            os.makedirs(root, exist_ok=True)

        return path

    def __post_init__(self):
        self.environ = os.path.join(self.workdir, self.environ)
        dotenv.load_dotenv(verbose=True, dotenv_path=self.environ)


@dataclasses.dataclass()
class PCConfig(BaseConfig):
    """
    The scraper configuration for Personal Capital.
    """
    #: The path to the personal capital session cookie
    cookies: str = dataclasses.field(init=False, default='session.json')

    @property
    def username(self) -> str:
        """
        Get the personal capital account username.
        """
        return os.environ.get('PC_USERNAME', '')

    @property
    def password(self) -> str:
        """
        Get the personal capital account password.
        """
        return os.environ.get('PC_PASSWORD', '')

    def __post_init__(self):
        super().__post_init__()
        self.cookies = os.path.join(self.workdir, self.cookies)


def pandas():
    """
    Set up the pandas module.
    """
    import pandas as _pandas
    _pandas.set_option('display.max_colwidth', 1024)
    _pandas.set_option('display.max_columns', 1024)
    _pandas.set_option('display.max_rows', 1024)
    _pandas.set_option('display.width', 4096)


def logging():
    """
    Set up the logging module.
    """
    import logging as _logging
    _logging.basicConfig(level=_logging.DEBUG, format='%(message)s')
