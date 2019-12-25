"""
A wrapper around an API.
"""
import dataclasses
import datetime
import typing
import os


import dotenv


@dataclasses.dataclass()
class BaseConfig:
    """
    The finance configuration.
    """
    #: The working directory
    workdir: str = dataclasses.field(default_factory=lambda: os.getcwd())
    #: The path to the personal capital environment files
    environ: str = dataclasses.field(init=False, default='.env')
    #: The time at configuration creation
    dt: datetime.datetime = dataclasses.field(
        init=False, default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc))

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


class BaseHandler:
    """
    Handler to create a REST session.
    """
    def __init__(self, config: typing.Union[None, BaseConfig]):
        self._obj_config: BaseConfig = config

    @property
    def config(self):
        """
        Object configuration.
        """
        return self._obj_config

    @property
    def client(self):
        """
        API client session instance.
        """
        raise NotImplementedError
