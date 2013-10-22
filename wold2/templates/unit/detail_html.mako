<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>


<%def name="sidebar()">
    <%util:well title="Loanword Information">
        ${util.dl_table(('Borrowed status', ctx.borrowed))}
    </%util:well>
</%def>

<h2><i>${ctx.name}</i></h2>
<div class="well well-small" style="background-color: #${ctx.language.vocabulary.color};">
    a word from vocabulary ${h.link(request, ctx.language.vocabulary)}
    by ${h.linked_contributors(request, ctx.language.vocabulary)}
    &nbsp; ${h.cite_button(request, ctx.language.vocabulary)}
</div>
