<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="sidebar()">
    <%util:well>
        <h3>New domain for <i>WOLD</i></h3>
        <p>
            For reasons beyond our control we have to serve <i>WOLD</i> under a new domain.
            Starting June 3, 2014 <i>WOLD</i> should be accessed using the domain
            <a href="http://wold.clld.org">wold.clld.org</a>
            instead of the old domain <i>wold.livingsources.org</i>.
        </p>
        <p>
            Until the end of 2014 the old domain will be redirected to the new one, but
            make sure you update bookmarks or links accordingly. From January 2015
            <i>wold.livingsources.org</i> is no longer under our control.
        </p>
        <p>
            We regret that we could not find a better solution and apologize for
            the inconvenience.
        </p>
    </%util:well>
</%def>

<h2>The World Loanword Database (WOLD)</h2>
<p>
    The World Loanword Database, edited by
    ${h.external_link("http://email.eva.mpg.de/~haspelmt/", label="Martin Haspelmath")} and
    ${h.external_link("http://lingweb.eva.mpg.de/jakarta/uri.php", label="Uri Tadmor")}, is a
    scientific publication by the
    ${h.external_link(request.dataset.publisher_url, label=request.dataset.publisher_name)},
    ${request.dataset.publisher_place} (2009). ${h.cite_button(request, ctx)}
</p>
<p>
    It provides
    <a href="${request.route_url('contributions')}">vocabularies</a>
    (mini-dictionaries of about 1000-2000 entries) of 41 languages
    from around the world, with comprehensive information about the loanword status of each word.
    It allows users to find
    ${u.term_link(request, 'loanword', label='loanwords')},
    ${u.term_link(request, 'source_word', label='source words')} and
    ${u.term_link(request, 'donor_language', label='donor languages')}
    in each of the 41
    languages, but also makes it easy to compare loanwords across languages.
</p>
<p>
    Each vocabulary was contributed by an expert on the language and its history. An accompanying
    book has been published by De Gruyter Mouton
    (${h.external_link("http://www.degruyter.com/view/product/41172?rskey=XDsyHr&result=5", label="Loanwords in the World's Languages: A Comparative Handbook, edited by Martin Haspelmath & Uri Tadmor")}).
</p>
<p>
    The World Loanword Database consists of vocabularies contributed by 41
    different authors or author teams. When citing material from the database, please cite
    the corresponding vocabulary (or vocabularies).
</p>
<p>
    The database can be accessed by language, by meaning or by author.
</p>
<p>
    The World Loanword Database is the result of a collaborative project coordinated by
    Uri Tadmor and Martin Haspelmath between 2004 and 2008, called the
    <em>Loanword Typology Project</em>
    (LWT). Most of the contributors took part in workshops at which the procedures for selecting
    and annotating words were discussed extensively. The list of 1460 meanings on which the
    vocabularies are based is called the Loanword Typology meaning list, and it is in turn based
    on the list of the
    ${h.external_link("http://lingweb.eva.mpg.de/ids/", label="Intercontinental Dictionary Series")}.
</p>
