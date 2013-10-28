<%inherit file="app.mako"/>

##
## define app-level blocks:
##
<%block name="header">
    <div id="banner">
        <a href="${request.route_url('dataset')}">
            <img src="${request.static_url('wold2:static/header.gif')}"/>
        </a>
    </div>
</%block>

${next.body()}
