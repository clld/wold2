from clld.web.assets import environment
from clldutils.path import Path

import wold2


environment.append_path(
    Path(wold2.__file__).parent.joinpath('static').as_posix(), url='/wold2:static/')
environment.load_path = list(reversed(environment.load_path))
