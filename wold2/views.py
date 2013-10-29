from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='terms', renderer='terms.mako')
def terms(req):
    return {}
