from pyramid.config import Configurator
from pyramid.events import BeforeRender
from sqlalchemy import engine_from_config

from clld import interfaces

from wold2 import util
from wold2.datatables import Counterparts, WoldLanguages, WoldContributors
from wold2.maps import MeaningMap, LanguagesMap, LanguageMap
from wold2.adapters import WoldGeoJsonLanguages
from wold2 import views


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['mako.directories'] = ['wold2:templates', 'clld:web/templates']
    settings['clld.app_template'] = "wold2.mako"

    config = Configurator(settings=settings)

    def add_util(event):
        event['wold'] = util

    config.add_subscriber(add_util, BeforeRender)

    config.include('clld.web.app')

    config.register_datatable('values', Counterparts)
    config.register_datatable('languages', WoldLanguages)
    config.register_datatable('contributors', WoldContributors)
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
    config.scan(views)
    return config.make_wsgi_app()
