<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>


<h2>Meaning ${ctx.id}: ${ctx.name}</h2>

<div class="row-fluid">
<div class="span8">
${util.dl_table(*list(u.get_meaning_properties(request, ctx)))}
</div>
</div>

<ul class="nav nav-pills pull-right">
    <li><a href="#map-container">Map</a></li>
    <li><a href="#list-container">List</a></li>
</ul>
<h3>Counterpart words in the World Loanword Database</h3>
${request.map.render()}
<div id="list-container">
${request.get_datatable('values', h.models.Value, parameter=ctx).render()}
</div>
<script>
$(document).ready(function() {
    $('.fieldinfo').clickover({'html': true});
});
</script>
