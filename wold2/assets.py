from clld.web.assets import environment
from path import path

import wold2


environment.append_path(
    path(wold2.__file__).dirname().joinpath('static'), url='/wold2:static/')
environment.load_path = list(reversed(environment.load_path))
