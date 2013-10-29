<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>


<h2>Glossary</h2>

<%util:section title="Affiliation" prefix="">
    Affiliation refers to the larger genealogical group
    (${u.term_link(request, 'genus')}, ${u.term_link(request, 'language_family', 'family')}) that a
    language belongs to.
</%util:section>

<%util:section title="Age" prefix="">
    For most words, ${u.home_link(request, )} gives the time at which it was first attested or reconstructed
    in the language. For ${u.term_link(request, 'loanword', 'loanwords')}, we give the time when the word was borrowed. For
    non-loanwords, we give the time of earliest attestation or reconstruction. The age
    is indicated by year numbers or by language-particular age names (e.g. "Early Modern
    Japanese", "Sranan Stratum"). In languages with no earlier attestation, age names
    are often reconstructed proto-languages (e.g. "Proto-Tara-Cahitan",
    "Proto-Tibeto-Burman").
</%util:section>

<%util:section title="Age score" id="age_score">
    <p>
      For individual ${u.term_link(request, 'meaning', 'meanings')} and
      ${u.term_link(request, 'semantic_field', 'semantic fields')}, we give an average age score, averaging
      over all the words corresponding to the meaning (or to the semantic field).
    </p>
    <p>
      The following age scores are assigned to words depending on their (estimated) age:
    </p>
    <table class="table table-condensed table-nonfluid">
      <tbody>
        <tr>
          <td>1. first attested or reconstructed earlier than 1000</td>
          <td>1.00</td>
        </tr>
        <tr>
          <td>2. earlier than 1500</td>
          <td>0.90</td>
        </tr>
        <tr>
          <td>3. earlier than 1800</td>
          <td>0.80</td>
        </tr>
        <tr>
          <td>4. earlier than 1900</td>
          <td>0.70</td>
        </tr>
        <tr>
          <td>5. earlier than 1950</td>
          <td>0.60</td>
        </tr>
        <tr>
          <td>6. earlier than 2007</td>
          <td>0.50</td>
        </tr>
      </tbody>
    </table>
    <p>
      Thus, the higher the average age score of a meaning, the older the corresponding
      words tend to be.
    </p>
    <p>
      In all average scores, words that correspond to multiple
      ${u.term_link(request, 'lwt_meaning', 'LWT meanings')} do not
      count fully. Thus, if a word corresponds to both the meanings 'air' and 'wind',
      it counts 50% for the average score of 'air' and 50% for the average score of 'wind'.
    </p>
</%util:section>

<%util:section title="Analyzability" prefix="">
    <p>
      Here we indicate for each ${u.term_link(request, 'word')} whether it is
    </p>
    <ol style="list-style: none;">
      <li>(1) unanalyzable (if the form cannot be analyzed into two or more constituents);</li>
      <li>(2) semi-analyzable (if one can identify a constituent structure, but not all constituents have meanings, such as cran in cranberry);</li>
      <li>(3) analyzable derived;</li>
      <li>(4) analyzable compound;</li>
      <li>(5) analyzable phrasal.</li>
    </ol>
</%util:section>

<%util:section title="Author" prefix="">
    ${u.home_link(request, 'The World Loanword Database')} is an edited work, consisting of 41 individual
    vocabularies with individual authors. When citing ${u.home_link(request, )} only for one language or a
    few languages, you need to cite the individual vocabulary and thus give credit to
    the individual author or author team.
</%util:section>

<%util:section title="Borrowed score" id="borrowed_score">
    <p>
      For individual ${u.term_link(request, 'lwt_meaning', 'meanings')} and
      ${u.term_link(request, 'semantic_field', 'semantic fields')}, we give an average borrowed score,
      averaging over all the words corresponding to the meaning (or to the semantic field).
    </p>
    <p>
      The following borrowed scores are assigned to words depending on their borrowed status:
    </p>
    <table class="table table-condensed table-nonfluid">
      <tbody>
        <tr>
          <td>1. clearly borrowed</td>
          <td>1.00</td>
        </tr>
        <tr>
          <td>2. probably borrowed</td>
          <td>0.75</td>
        </tr>
        <tr>
          <td>3. perhaps borrowed</td>
          <td>0.50</td>
        </tr>
        <tr>
          <td>4. very little evidence for borrowing</td>
          <td>0.25</td>
        </tr>
        <tr>
          <td>5. no evidence for borrowing</td>
          <td>0.00</td>
        </tr>
      </tbody>
    </table>
    <p>
      Thus, the higher the average borrowed score of a meaning, the greater its borrowability.
    </p>
    <p>
      In all average scores, words that correspond to multiple
      ${u.term_link(request, 'lwt_meaning', 'LWT meanings')} do not count
      fully. Thus, if a word corresponds to both the meanings 'air' and 'wind', it counts
      50% for the average score of 'air' and 50% for the average score of 'wind'.
    </p>
</%util:section>

<%util:section title="Borrowed status" id="borrowed_status">
      <p>
        There are five borrowed statuses, reflecting decreasing likelihood that the ${u.term_link(request, 'word')}
        is a ${u.term_link(request, 'loanword')}:
      </p>
      <ol>
        <li>clearly borrowed</li>
        <li>probably borrowed</li>
        <li>perhaps borrowed</li>
        <li>very little evidence for borrowing</li>
        <li>no evidence for borrowing</li>
      </ol>
      <p>
        This field does not allow values like "Clearly not borrowed" or "Clearly inherited"
        because any word could have been borrowed at some prehistoric time, so we can never
        be sure that a word is not an old loanword. And even loanwords can be inherited,
        e.g. a word borrowed into Proto-Uralic can be inherited by Hungarian.
      </p>
      <p>
        We are dealing basically with lexemes which are transferred or copied from one lect
        into another. Words from a substrate language are considered to be loanwords, even
        though some linguists do not use the term "borrowing" for transfer from substrates.
      </p>
      <p>
        Excluded from the class of loanwords are neologisms (= productively created lexemes),
        even those which consist partly or entirely of foreign material, because they are
        created in the recipient language, not in the ${u.term_link(request, 'donor_language')}.
      </p>
</%util:section>

<%util:section title="Citation" id="citation">
        ${u.home_link(request, 'The World Loanword Database')} is an edited work, consisting of 41 individual vocabularies
        with individual authors. When citing ${u.home_link(request, )} only for one language or a few languages, you need
        to cite the individual vocabulary and thus give credit to the individual author or author team.
</%util:section>

<%util:section title="Contact situation" id="contact_situation">
        This field contains the name of the contact situation in which the word was borrowed.
        Normally there are at least as many contact situations as there are different
        ${u.term_link(request, 'donor_language', 'donor languages')}.
        But languages can borrow words from the same language in completely
        different situations. For instance, English dish was borrowed from Latin discus in
        pre-Old English times, whereas discus was borrowed from the same Latin word in the
        17th century. So we distinguish a contact situation "Latin to Germanic" from a
        contact situation "(Learned) Latin contact". On the other hand, for the borrowing
        of boomerang and kangaroo, we can assume basically the same contact situation
        ("Australian Aboriginal contact"), even if the two terms are from two different
        donor languages.
</%util:section>

<%util:section title="Description" id="description">
        Under "description", we list various comments that the individual authors have
        provided concerning the individual fields of their vocabularies. Here you also find
        the list of works that are referred to.
</%util:section>

<%util:section title="Donor language, donor languoid" id="donor_language">
        The donor language for a ${u.term_link(request, 'loanword')} is the language from which
        the word was borrowed.
        Sometimes the language is not known, only the family (e.g. when it is clear that
        the word was borrowed from a Bantu language, but it is not clear which Bantu language).
        In such cases we can talk about a "donor family", even though strictly speaking the
        word must of course have been borrowed from a single language. The term
        "donor languoid" is a cover term for "donor language" and "donor family".
</%util:section>

<%util:section title="Earlier donor language (or donor languoid)" id="earlier_donor_language">
        For many ${u.term_link(request, 'loanword', 'loanwords')}, we know not only the
        ${u.term_link(request, 'immediate_donor_language')}  from which the
        word was borrowed, but also an earlier donor language, if the word was itself a
        loanword from some other language. And there are also quite a few loanwords for
        which we can identify an earlier donor, but not the immediate donor language. For
        example, for many Indonesian words it is clear that they must have come from Arabic,
        but probably not directly, so there must have been intermediate languages. In such
        cases, we only give the earlier donor language, not the immediate donor language.
</%util:section>

<%util:section title="Effect" id="effect">
      <p>
        This field contains information on
      </p>
      <ol style="list-style: none;">
        <li>whether the word replaced an earlier word (1: replacement),</li>
        <li>whether it was simply added where no earlier word existed with the same meaning (2: insertion),</li>
        <li>whether it coexists with an earlier word of roughly the same meaning (3: coexistence),</li>
        <li>or whether there is no information about its effect (0: no information).</li>
      </ol>
</%util:section>

<%util:section title="Field number" id="field_number">
        The number in this column is the semantic field number. It is the first part of the
        Loanword Typology Code of the words in the corresponding field.
</%util:section>

<%util:section title="Genus" id="genus">
        A genus is a relatively shallow kind genealogical group. The "genus" level is used
        in the classification of the
        ${h.external_link('http://wals.info/', label='World Atlas of Language Structures Online')}
        in addition to the
        "family" level. Families with considerable time depth consist of different genera.
</%util:section>

<%util:section title="Grammatical information" id="grammatical_info">
        The field "Grammatical info" contains grammatical information such as word class,
        gender, inflection class.
</%util:section>

<%util:section title="ID" id="language_id">
        For the recipient languages, the language ID number corresponds to the ordering
        of the chapters in the book "Loanwords in the World's Languages". Languages are
        listed in rough geographical order from west to east, from Africa via Europe to
        Asia and the Americas, so that geographically adjacent languages are next to
        each other. For the other languages, the ID number has no particular significance.
</%util:section>

<%util:section title="IDS list" id="ids_list">
        The IDS list is the list of lexical meanings used by the
        ${h.external_link("http://lingweb.eva.mpg.de/ids/", label="Intercontinental Dictionary Series website")}.
</%util:section>

<%util:section title="Immediate donor language (or donor languoid)" id="immediate_donor_language">
        The immediate donor language for a ${u.term_link(request, 'loanword')} is the language from which the word was
        borrowed directly, as opposed to "indirect borrowing" from an ${u.term_link(request, 'earlier_donor_language')}.
</%util:section>

<%util:section title="ISO 639-3 code" id="iso_code">
        This is the unique three-letter language code used by the
        ${h.external_link("http://www.sil.org/iso639-3/", label='standard 639-3')}
        of the
        ${h.external_link("http://www.iso.org/", label='International Standards Organization')}.
</%util:section>

<%util:section title="Language family" id="language_family">
        In this field, we the give the name of the highest family that is generally
        accepted to which the language belongs.
</%util:section>

<%util:section title="Language name" id="language_name">
        In this field, we the give the name of the language (or family, in the case of
        donor languages) that was adopted in the ${u.home_link(request, 'World Loanword Database')}.
        Alternative names can be found on the individual language pages.
</%util:section>

<%util:section title="Languoid" id="languoid">
    "Languoid" is a (relatively new) cover term for "language" and "language family".
</%util:section>

<%util:section title="Loanword" id="loanword">
    A loanword is a word that was copied from another language, either by adoption
    or by retention, at some point in the history of the language. Even if a loanword
    is fully integrated, it is still a loanword, and a loanword never ceases to be a
    loanword.
</%util:section>

<%util:section title="LWT" id="lwt">
    LWT is an abbreviation for "<strong>L</strong>oan<strong>w</strong>ord <strong>T</strong>ypology", the name of the Loanword Typology Project (2004-2009)
    that resulted in the ${u.home_link(request, 'World Loanword Database')}.
</%util:section>

<%util:section title="LWT Code" id="lwt_code">
    The Loanword Typology code (LWT code) is the identifier of the ${u.term_link(request, 'lwt_meaning', 'Loanword Typology meaning')}.
</%util:section>

<%util:section title="LWT meaning" id="lwt_meaning">
    An LWT meaning is a lexical meaning from the ${u.term_link(request, 'lwt_meaning_list', 'LWT meaning list')}.
</%util:section>

<%util:section title="LWT meaning list" id="lwt_meaning_list">
    The LWT meaning list is the list of 1460 core lexical meanings that served as the
    basis for the vocabularies of the ${u.home_link(request, 'World Loanword Database')}.
    It is based on the ${u.term_link(request, 'ids_list', 'IDS list')} created by
    Mary Ritchie Key, which in turn is based on the list in Carl Darling Buck's
    "Dictionary of Selected Synonyms in the Principal Indo-European Languages" (1949).
</%util:section>

<%util:section title="Meaning" id="meaning">
        By "meaning", we mean lexical meanings, i.e. meanings of lexical items. For each
        word, there is a corresponding ${u.term_link(request, 'lwt_meaning', 'LWT meaning')}, and often there are several
        corresponding LWT meanings. For many words, there is additional language-particular
        information in the field "Word meaning".
</%util:section>

<%util:section title="Original script" id="original_script">
        This gives the usual written form for languages that do not use the Latin script.
</%util:section>

<%util:section title="Recipient language" id="recipient_language">
        The recipient language for a loanword is the language into which the word was
        borrowed, i.e. the language whose lexicon the word is part of.
</%util:section>

<%util:section title="Reference" id="reference">
        This field often contains bibliographic information about works that were used
        as a source by the authors.
</%util:section>

<%util:section title="Representation" id="representation">
        This column shows how many counterparts for this meaning there are in the 41
        languages. The number can be higher than 41 because a language may have several
        counterparts for one meaning ("synonyms"), and it may be lower than 41, because
        not all languages may have a counterpart for a meaning.
</%util:section>

<%util:section title="Salience" id="salience">
      <p>
        This field gives information about the degree to which a word's meaning is
        relevant to the speakers. "Environment" refers both to the natural and to the
        cultural environment. The three values are:
      </p>
      <ol>
        <li>Present in pre-contact environment</li>
        <li>Present only since contact</li>
        <li>Not present</li>
      </ol>
      <p>
        By ‘contact’, we mean the first contact between speakers of the project language
        and the donor language. This contact could have been with speakers of the donor
        language, but it could also have been with written sources in the donor language.
      </p>
</%util:section>

<%util:section title="Semantic category" id="semantic_category">
        Meanings were assigned to semantic categories with word-class-like labels:
        nouns, verbs, adjectives, adverbs, function words. No claim is made about the
        grammatical behavior of words corresponding to these meanings. The categories
        are intended to be purely semantic.
</%util:section>

<%util:section title="Semantic field" id="semantic_field">
        The 1460 meanings of the LWT list are divided into 24 semantic fields, following
        Carl Darling Buck's original classification.
</%util:section>

<%util:section title="Simplicity score" id="simplicity_score">
      <p>
        For individual meanings and semantic fields, we give an average simplicity score,
        averaging over all the words corresponding to the meaning (or to the semantic field).
        The following simplicity scores are assigned to words depending on their analyzability:
      </p>
      <table class="table table-condensed table-nonfluid">
        <tbody>
          <tr>
            <td>1. unanalyzable (= simple)</td>
            <td>1.00</td>
          </tr>
          <tr>
            <td>2. semi-analyzable</td>
            <td>0.75</td>
          </tr>
          <tr>
            <td>3. analyzable</td>
            <td>0.50</td>
          </tr>
        </tbody>
      </table>
      <p>
        Thus, the higher the average borrowed score of a meaning, the fewer complex
        words correspond to it.
      </p>
      <p>
        In all average scores, words that correspond to multiple <a href="#lwt_meaning">LWT meanings</a> do not
        count fully. Thus, if a word corresponds to both the meanings 'air' and 'wind',
        it counts 50% for the average score of 'air' and 50% for the average score of 'wind'.
      </p>
</%util:section>

<%util:section title="Source word" id="source_word">
    The source word of a ${u.term_link(request, 'loanword')} is the word that served as the model during the
    borrowing process, i.e. from which the loanword was copied.
</%util:section>

<%util:section title="Text chapter" id="text_chapter">
    Each ${u.term_link(request, 'vocabulary')} has a corresponding text chapter in the book
    "Loanwords in the World's Languages".
</%util:section>

<%util:section title="Vocabulary" id="vocabulary">
    Each vocabulary of ${u.home_link(request, )} is a separate electronic publication with a separate
    ${u.term_link(request, 'author', 'author or team of authors')}.
    Each vocabulary has a characteristic colour in ${u.home_link(request, )}.
</%util:section>

<%util:section title="WALS Code" id="wals_code">
    This refers to the unique three-letter abbreviation of the language in the
    ${h.external_link('http://wals.info/', label='World Atlas of Language Structures Online')}.
</%util:section>

<%util:section title="Word" id="word">
    The word is given in the usual orthography or transcription, and in the usual citation form.
</%util:section>

<%util:section title="Word meaning" id="word_meaning">
    For many ${u.term_link(request, 'word', 'words')}, we have information in this field, giving the translation of the
    word into English. This field was by no means obligatory, however, because the
    meaning of a word is very often sufficiently described by giving the corresponding
    ${u.term_link(request, 'lwt_meaning', 'LWT meaning(s)')}.
</%util:section>
