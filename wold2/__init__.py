from clld.web.app import get_configurator
from clld.interfaces import ILanguage, IIndex, IParameter
from clld.web.adapters.base import Index, adapter_factory

from wold2.datatables import Counterparts, WoldLanguages, Authors, Vocabularies, Meanings
from wold2.maps import MeaningMap, LanguagesMap, LanguageMap
from wold2.adapters import WoldGeoJsonLanguages, GeoJsonMeaning
from wold2.models import SemanticField
from wold2.interfaces import ISemanticField


_ = lambda s: s
_('Contribution')
_('Contributions')
_('Contributor')
_('Contributors')
_('Parameter')
_('Parameters')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['route_patterns'] = {
        'languages': '/language',
        'language': '/language/{id:[^/\.]+}',
        'parameters': '/meaning',
        'parameter': '/meaning/{id:[^/\.]+}',
        'contributions': '/vocabulary',
        'contribution': '/vocabulary/{id:[^/\.]+}',
        'contributors': '/contributor',
        'contributor': '/contributor/{id:[^/\.]+}',
        'legal': '/about/legal',
    }
    ##settings['sitemaps'] = 'contribution parameter source sentence valueset'.split()
    settings['mako.directories'] = ['wold2:templates', 'clld:web/templates']
    settings['clld.app_template'] = "wold2.mako"

    config = get_configurator('wold2', settings=settings)

    config.register_datatable('values', Counterparts)
    config.register_datatable('languages', WoldLanguages)
    config.register_datatable('contributors', Authors)
    config.register_datatable('contributions', Vocabularies)
    config.register_datatable('parameters', Meanings)
    config.register_map('parameter', MeaningMap)
    config.register_map('languages', LanguagesMap)
    config.register_map('language', LanguageMap)

    config.register_resource('semanticfield', SemanticField, ISemanticField, with_index=True)
    config.register_adapter(adapter_factory('semanticfield/detail_html.mako'), ISemanticField)
    config.register_adapter(adapter_factory('semanticfield/index_html.mako', base=Index), ISemanticField)

    config.register_adapter(GeoJsonMeaning, IParameter)
    config.register_adapter(
        WoldGeoJsonLanguages,
        ILanguage,
        IIndex,
        WoldGeoJsonLanguages.mimetype)

    return config.make_wsgi_app()
