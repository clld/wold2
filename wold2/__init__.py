from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from clld.db.meta import (
    DBSession,
    Base,
)

from wold2.datatables import Counterparts
from wold2.maps import MeaningMap


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)

    config.include('clld.web.app')
    config.register_datatable('values', Counterparts)
    config.register_map('parameter', MeaningMap)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    return config.make_wsgi_app()
