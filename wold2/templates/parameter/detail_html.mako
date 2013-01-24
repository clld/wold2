<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>

<%! from clld.interfaces import IDataTable %>
<%! from clld.db.models.common import Value %>

<h2>Meaning ${ctx.name}</h2>

<dl>
    <dt>Borrowed score</dt>
    <dd>${ctx.borrowed_score}</dd>
</dl>

% if request.map:
${request.map.render()}
% endif


<div>
    <% dt = request.registry.getUtility(IDataTable, 'values'); dt = dt(request, Value, parameter=ctx) %>
    ${dt.render()}
</div>
