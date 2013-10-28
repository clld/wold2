<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>

<%! from wold2.maps import RecipientMap, DonorMap %>
<% qr, qd = map(list, u.get_related_languages(ctx, request)) %>

<div style="margin-top: 5px;">
${util.codes()}
</div>

<h2>Language ${ctx.name}</h2>
% if qr and qd:
<ul class="nav nav-pills">
    <li><a href="#recipient">as recipient</a></li>
    <li><a href="#donor">as donor</a></li>
</ul>
% endif

% if qr:
<h3 id="recipient">As recipient Language</h3>
<div class="well well-small" style="background-color: #${ctx.vocabulary.color};">
    ${h.link(request, ctx.vocabulary)} vocabulary contributed by ${h.linked_contributors(request, ctx.vocabulary)}
</div>
${RecipientMap(ctx, request, qr).render()}
${request.get_datatable('units', h.models.Unit, language=ctx, type_='recipient').render()}
<div style="margin-top: 30px;">&nbsp;</div>
% endif
% if qd:
<h3 id="donor">As donor Language</h3>
${DonorMap(ctx, request, qd).render()}
${request.get_datatable('units', h.models.Unit, language=ctx, type_='donor').render()}
% endif
