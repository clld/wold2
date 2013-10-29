<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Languages')}</%block>

<h2>${_('Languages')}</h2>

<p>
    The World Loanword Database contains information on
    ${u.term_link(request, 'loanword', label='loanwords')},
    ${u.term_link(request, 'source_word', label='source words')} and
    and other words in 395 languages.
</p>
<p>
    Of these, 41 are called recipient languages, because we are interested in the loanwords
    that they have received from other languages. For each recipient language, there is a
    <a href="${request.route_url('contributions')}" title="see vocabularies">vocabulary</a>.
</p>
<p>
    The loanwords in these languages come from 369 different donor languages. These are
    the languages from which the recipient languages have taken the loanwords. 15 languages
    are both recipient languages and donor languages.
</p>

${request.map.render()}

${ctx.render()}
