from clld.web.app import get_configurator, MapMarker
from clld.interfaces import ILanguage, IIndex, IParameter, IMapMarker, IValue, IValueSet
from clld.web.adapters.base import Index, adapter_factory
from clld.web.adapters.download import N3Dump
from clld.db.models.common import Parameter

from wold2.maps import LanguagesMap, LanguageMap, MeaningMap
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
_('Terms')


class WoldMapMarker(MapMarker):
    def __call__(self, ctx, req):
        asset_spec = None
        if IValueSet.providedBy(ctx):
            asset_spec = 'wold2:static/%s.png' % ctx.contribution.color
        elif IValue.providedBy(ctx):
            asset_spec = 'wold2:static/%s.png' % ctx.valueset.contribution.color
        elif ILanguage.providedBy(ctx):
            asset_spec = 'clld:web/static/icons/%s.png' % (
                'ddd0000' if ctx.vocabulary else 'c4d6cee',)
        return req.static_url(asset_spec) if asset_spec else \
            super(WoldMapMarker, self).__call__(ctx, req)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['route_patterns'] = {
        'languages': '/language',
        'language': '/language/{id:[^/\.]+}',
        'unit': '/word/{id:[^/\.]+}',
        'parameters': '/meaning',
        'parameter': '/meaning/{id:[^/\.]+}',
        'contributions': '/vocabulary',
        'contribution': '/vocabulary/{id:[^/\.]+}',
        'contributors': '/contributor',
        'contributor': '/contributor/{id:[^/\.]+}',
        'semanticfields': '/semanticfield',
        'semanticfield': '/semanticfield/{id:[^/\.]+}',
        'legal': '/about/legal',
    }
    ##settings['sitemaps'] = 'contribution parameter source sentence valueset'.split()
    settings['mako.directories'] = ['wold2:templates', 'clld:web/templates']
    settings['clld.app_template'] = "wold2.mako"

    config = get_configurator('wold2', (WoldMapMarker(), IMapMarker), settings=settings)
    config.include('clldmpg')
    config.include('wold2.datatables')
    config.register_map('languages', LanguagesMap)
    config.register_map('language', LanguageMap)
    config.register_map('parameter', MeaningMap)
    config.register_resource('semanticfield', SemanticField, ISemanticField, with_index=True)
    config.register_adapter(adapter_factory('semanticfield/detail_html.mako'), ISemanticField)
    config.register_adapter(adapter_factory('semanticfield/index_html.mako', base=Index), ISemanticField)

    config.register_adapter(GeoJsonMeaning, IParameter)
    config.register_adapter(
        WoldGeoJsonLanguages,
        ILanguage,
        IIndex,
        WoldGeoJsonLanguages.mimetype)
    config.register_download(N3Dump(Parameter, 'wold2', description="Meanings as RDF"))
    return config.make_wsgi_app()
