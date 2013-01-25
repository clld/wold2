from pyramid.config import Configurator
from pyramid.events import BeforeRender
from sqlalchemy import engine_from_config

from clld.db.meta import (
    DBSession,
    Base,
)
from clld import interfaces

from wold2 import util
from wold2.datatables import Counterparts, WoldLanguages
from wold2.maps import MeaningMap, LanguagesMap, LanguageMap
from wold2.adapters import WoldGeoJsonLanguages


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)

    def add_util(event):
        event['wold'] = util

    config.add_subscriber(add_util, BeforeRender)

    config.include('clld.web.app')
    config.register_datatable('values', Counterparts)
    config.register_datatable('languages', WoldLanguages)
    config.register_map('parameter', MeaningMap)
    config.register_map('languages', LanguagesMap)
    config.register_map('language', LanguageMap)

    config.registry.registerAdapter(
        WoldGeoJsonLanguages,
        (interfaces.ILanguage,),
        interfaces.IIndex,
        name=WoldGeoJsonLanguages.mimetype)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    return config.make_wsgi_app()
