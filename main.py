 import os
import re
import yaml
import logging
from typing import Any, IO

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)

path_matcher = re.compile(r'\$\{([\w\d\_\-]+)\:?(\?)?([\w\d]+)?\}')
class Loader(yaml.FullLoader):
    """YAML Loader with `!include` constructor."""

    def __init__(self, stream: IO) -> None:
        """Initialise Loader."""
        self.path_matcher = re.compile(r'\$\{([\w\d\_\-]+)\:?(\?)?([\w\d]+)?\}')
        super().__init__(stream)

    def matcher(self):
        return self.path_matcher


def construct_env(loader: Loader, node: yaml.Node) -> Any:
    """ Extract the matched value, expand env variable, and replace the match """
    value = node.value
    match = loader.path_matcher.match(value)
    # 0 - all
    # 1 - VAR_NAME
    # 2 - ?
    # 3 - Value
    value = ""
    log.debug(f"Match: {match.group()} ")
    env_var = match.group(1)
    default_value = match.group(3)
    question = match.group(2)
    if question is not None:
        try:
            value = os.environ[env_var]
        except KeyError as ex:
            log.error(f"Can't find {env_var}:{default_value}")
            return default_value
    value = os.environ.get(env_var, default=default_value)
    return value


Loader.add_implicit_resolver('!env', path_matcher, None)
Loader.add_constructor('!env', construct_env)


data = """
env: ${VAR}/file.txt
env_def: ${VAR_DEF:some_value}/file.txt
env_?: ${VAR_DEF:?error_value}/file.txt
other: file.txt
"""


if __name__ == '__main__':
    _dt = yaml.load(data, Loader=Loader)
    os.environ["VAR"] = "works"

    log.info(_dt.get("env"))
    log.info(_dt.get("env_def"))
    log.info(_dt.get("env_?"))
