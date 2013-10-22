<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>


<h2>The World Loanword Database (WOLD)</h2>
<p>
      The World Loanword Database, edited by
      ${h.external_link("http://email.eva.mpg.de/~haspelmt/", label="Martin Haspelmath")} and
      ${h.external_link("http://lingweb.eva.mpg.de/jakarta/uri.php", label="Uri Tadmor")}, is a
      scientific publication by the
      ${h.external_link(request.dataset.publisher_url, label=request.dataset.publisher_name)},
      ${request.dataset.publisher_place} (2013).
</p>
<p>
      It provides
      <a href="http://wold.livingsources.org/terms#vocabulary" title="look up definition of vocabulary" class="Term">vocabularies</a>
      (mini-dictionaries of about 1000-2000 entries) of
      41
      languages
      from around the world, with comprehensive information about the loanword status of each word.
      It allows users to find
      <a href="http://wold.livingsources.org/terms#loanword" title="look up definition of loanword" class="Term">loanwords</a>
      ,
      <a href="http://wold.livingsources.org/terms#source_word" title="look up definition of source word" class="Term">source words</a>
      and
      <a href="http://wold.livingsources.org/terms#donor_language" title="look up definition of donor language" class="Term">donor languages</a>
      in each of the
      41
      languages, but also makes it easy to compare loanwords across languages.
</p>
<p>
      Each vocabulary was contributed by an expert on the language and its history. An accompanying
      book is being published by Mouton de Gruyter
      (${h.external_link("http://www.degruyter.de/cont/fb/sk/detail.cfm?id=IS-9783110218435-1", label="Loanwords in the World's Languages: A Comparative Handbook, edited by Martin Haspelmath &amp; Uri Tadmor")}).
</p>
<p>
      The World Loanword Database consists of vocabularies contributed
      by
      41
      different authors or author teams. When citing material from the database, please cite
      the corresponding vocabulary (or vocabularies).
</p>
<p>
    The database can be accessed by language, by meaning, by author, or by reference.
</p>
<p>
      The World Loanword Database is the result of a collaborative project coordinated by
      Uri Tadmor and Martin Haspelmath between 2004 and 2008, called the
      <a href="http://www.eva.mpg.de/lingua/files/lwt.html" title="Loanword Typology Project" class="ext-link">Loanword Typology Project</a>
      (LWT). Most of the contributors took part in workshops at which the procedures for selecting
      and annotating words were discussed extensively. The list of 1460 meanings on which the
      vocabularies are based is called the Loanword Typology meaning list, and it is in turn based
      on the list of the
      <a href="http://lingweb.eva.mpg.de/ids/" title="Intercontinental Dictionary Series" class="ext-link">Intercontinental Dictionary Series</a>
      .
</p>
