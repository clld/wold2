<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>

<%! from clld.interfaces import IDataTable %>
<%! from clld.db.models.common import Value %>

<h2>Language ${ctx.name}</h2>

% if ctx.vocabulary:
<ul class="nav nav-tabs">
    <li class="${'active' if request.params.get('t') != 'recipient' else ''}">
        <a href="${request.purl.query_param('t', 'donor')}">As donor language</a>
    </li>
    <li class="${'active' if request.params.get('t') == 'recipient' else ''}">
        <a href="${request.purl.query_param('t', 'recipient')}">As recipient Language</a>
    </li>
</ul>
% endif

<% rel_langs = list(wold.get_related_languages(ctx, request)) %>
<% request.map.layers[0]['data'] = wold.get_related_languages_geojson(ctx, request, rel_langs) %>
${request.map.render()}


##% for l in wold.get_related_languages(ctx, request):
##<div>${l.name}</div>
##% endfor

##
## render map and list of loanwords
##


##<dl>
##    <dt>Borrowed score</dt>
##    <dd>${ctx.borrowed_score}</dd>
##</dl>

##% if request.map:
##${request.map.render()}
##% endif


##<div>
##    <% dt = request.registry.getUtility(IDataTable, 'values'); dt = dt(request, Value, parameter=ctx) %>
##    ${dt.render()}
##</div>
