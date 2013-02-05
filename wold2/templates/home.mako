<%inherit file="wold2.mako"/>

<%def name="sidebar()">
  <div id="wold_news" class="well well-small">
  </div>
  <script>
$(document).ready(function() {
    CLLD.Feed.init(${h.dumps(dict(eid="wold_news", url="http://blog.wold.livingsources.org/category/news/feed/", title="WOLD News"))|n});
});
  </script>
</%def>


<h2>Welcome to the World Loanword Database (WOLD)</h2>

<p class="lead">
The World Loanword Database, edited by Martin Haspelmath and Uri Tadmor, is a scientific
publication by the Max Planck Digital Library, Munich (2009).
</p>
<p>
It provides vocabularies (mini-dictionaries of about 1000-2000 entries) of 41 languages
from around the world, with comprehensive information about the loanword status of each
word. It allows users to find loanwords, source words and donor languages in each of the
41 languages, but also makes it easy to compare loanwords across languages.
</p>
