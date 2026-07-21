<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<h2>${_('Contribution')} ${ctx.name}</h2>
<div class="well well-small" style="background-color: #${ctx.color};">
    by ${h.linked_contributors(request, ctx)} &nbsp; ${h.cite_button(request, ctx)}
</div>
<p>
    The vocabulary contains ${ctx.count_core_list_counterparts} meaning-word pairs ("entries")
    corresponding to core ${u.term_link(request, 'lwt_meaning', 'LWT meanings')} from the recipient language
    ${h.link(request, ctx.language)}. The corresponding text chapter was published in the
    book Loanwords in the World's Languages. The language page ${h.link(request, ctx.language)}
    contains a list of all ${u.term_link(request, 'loanword', 'loanwords')} arranged by
    ${u.term_link(request, 'donor languoid')}.
</p>
<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#tab1" data-toggle="tab">Meaning-word pairs</a></li>
        <li><a href="#tab2" data-toggle="tab">Description</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="tab1" class="tab-pane active">
            ${request.get_datatable('values', h.models.Value, contribution=ctx).render()}
        </div>
        <div id="tab2" class="tab-pane">
            <h3>Field descriptions</h3>
            ${ctx.description|n}
        </div>
    </div>
</div>
