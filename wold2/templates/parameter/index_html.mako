<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">Meanings</%block>
<%! from wold2.models import SemanticField %>

<h2>${title()}</h2>
<div id="list-container">
    <div class="tabbable">
        <ul class="nav nav-tabs">
            <li class="active"><a href="#tab1" data-toggle="tab">Semantic fields</a></li>
            <li><a href="#tab2" data-toggle="tab">All meanings</a></li>
        </ul>
        <div class="tab-content" style="overflow: visible;">
            <div id="tab1" class="tab-pane active">
                ${request.get_datatable('semanticfields', SemanticField).render()}
            </div>
            <div id="tab2" class="tab-pane">
                ${request.get_datatable('parameters', h.models.Parameter).render()}
            </div>
        </div>
    </div>
</div>
