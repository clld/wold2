<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<h2>${_('Contribution')} ${ctx.name}</h2>
<div class="well well-small" style="background-color: #${ctx.color};">
    by ${h.linked_contributors(request, ctx)} &nbsp; ${h.cite_button(request, ctx)}
</div>
<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#tab1" data-toggle="tab">Words</a></li>
        <li><a href="#tab2" data-toggle="tab">Description</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="tab1" class="tab-pane active">
            ${request.get_datatable('values', h.models.Value, contribution=ctx).render()}
        </div>
        <div id="tab2" class="tab-pane">
            ${util.dl_table(**ctx.jsondatadict)}
        </div>
    </div>
</div>
