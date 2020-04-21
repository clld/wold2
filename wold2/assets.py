import pathlib

from clld.web.assets import environment

import wold2


environment.append_path(
    str(pathlib.Path(wold2.__file__).parent.joinpath('static')), url='/wold2:static/')
environment.load_path = list(reversed(environment.load_path))
