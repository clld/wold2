from __future__ import unicode_literals, division, absolute_import, print_function

from pyramid.config import Configurator

from clld.web.app import MapMarker
from clld.interfaces import ILanguage, IMapMarker, IValue, IValueSet
from clld.web.adapters.download import N3Dump
from clld.db.models.common import Parameter, Dataset

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
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.registry.registerUtility(WoldMapMarker(), IMapMarker),
    config.register_resource(
        'semanticfield', SemanticField, ISemanticField, with_index=True)
    #config.register_download(N3Dump(Parameter, 'wold2', description="Meanings as RDF"))
    return config.make_wsgi_app()
