<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<%def name="th_property(name, placement='right')">
    <td>
        <strong>${u.property_label(name)}</strong>
    % if ctx.language and ctx.language.vocabulary:
        <% desc = ctx.language.vocabulary.jsondatadict.get('fd_' + u.property_name(name)) %>
        ${u.infobutton(desc, placement=placement)}
    % endif
    </td>
</%def>


<%def name="tr_property(name, value_filter=lambda x: x, with_body=False, placement='right')">
% if with_body:
    <tr>
      ${th_property(name, placement=placement)}
      <td>${caller.body()}</td>
    </tr>
% else:
    <% value = getattr(ctx, name, ctx.jsondatadict.get(name)) %>
    % if value_filter(value):
    <tr>
      ${th_property(name, placement=placement)}
      <td>${value}</td>
    </tr>
    % endif
% endif
</%def>


<%def name="sidebar()">
    <%util:well title="Loanword Information">
    % if ctx.counterparts:
<table class="table table-condensed table-nonfluid">
    <tbody>
        ${tr_property('borrowed', placement='left')}
        ${tr_property('comment_on_borrowed', placement='left')}
        % if ctx.source_word_assocs:
        <%self:tr_property name="source_words" with_body="${True}">
            ${u.source_words(request, ctx)}
        </%self:tr_property>
        % endif
        ${tr_property('effect', placement='left')}
        ${tr_property('salience', placement='left')}
        % if ctx.contact_situation:
        <%self:tr_property name="contact_situation" with_body="${True}" placement="left">
            ${ctx.contact_situation.unitdomainelement.name}
            ${u.infobutton(ctx.contact_situation.unitdomainelement.description, placement='left')}
        </%self:tr_property>
        % endif
    </tbody>
</table>
    % else:
        <p>Source for the following loanwords:</p>
        <ul class="unstyled">
            % for loan in ctx.target_word_assocs:
            <li>${h.link(request, loan.target_word)} (${h.link(request, loan.target_word.language.vocabulary)})</li>
            % endfor
        </ul>
    % endif
    </%util:well>
</%def>

<h2><i>${ctx.name}</i></h2>
% if ctx.counterparts:
<div class="well well-small" style="background-color: #${ctx.language.vocabulary.color};">
    a word from vocabulary ${h.link(request, ctx.language.vocabulary)}
    by ${h.linked_contributors(request, ctx.language.vocabulary)}
    &nbsp; ${h.cite_button(request, ctx.language.vocabulary)}
</div>
% endif

<table class="table table-nonfluid">
    <tbody>
        ${tr_property('name')}
        ${tr_property('original_script')}
        % if ctx.counterparts:
        <tr>
            <td><strong>LWT meaning(s)</strong></td>
            <td>
                <ul class="inline">
                % for c in ctx.counterparts:
                    <li>${h.link(request, c.valueset.parameter)}</li>
                % endfor
                </ul>
            </td>
        </tr>
        % elif ctx.language:
        <tr>
            <th>Language:</th>
            <td>${h.link(request, ctx.language)}</td>
        </tr>
        % endif
        ${tr_property('description', value_filter=lambda x: x and x != '?')}
        ${tr_property('paraphrase_in_dutch')}
        ${tr_property('paraphrase_in_german')}
        ${tr_property('czech_translation')}
        ${tr_property('hungarian_translation')}
        ${tr_property('grammatical_info')}
        ${tr_property('comment_on_word_form')}
        ${tr_property('word_source')}
        ${tr_property('analyzability')}
        ${tr_property('gloss')}
        % if ctx.age:
        <%self:tr_property name="age" with_body="${True}">
            ${u.infobutton(ctx.age.unitdomainelement.description)}
            ${ctx.age.unitdomainelement.name}
            % if ctx.age.unitdomainelement.jsondatadict.get('start_year'):
            (${ctx.age.unitdomainelement.jsondatadict['start_year']}&ndash;${ctx.age.unitdomainelement.jsondatadict.get('end_year', '')})
            % endif
        </%self:tr_property>
        % endif
        ${tr_property('lexical_stratum')}
        ${tr_property('year')}
        ${tr_property('comparison_with_mandarin')}
        ${tr_property('comparison_with_korean')}
        ${tr_property('colonial_word')}
        ${tr_property('early_romani_reconstruction')}
        ${tr_property('etymological_note')}
        ${tr_property('boretzky_and_igla_etymology')}
        ${tr_property('manuss_et_al_etymology')}
        ${tr_property('vekerdi_etymology')}
        ${tr_property('turner_etymology')}
        ${tr_property('other_etymologies')}
        ${tr_property('mayrhofer_etymology')}
        ${tr_property('register')}
        ${tr_property('numeric_frequency')}
        ${tr_property('relative_frequency')}
    </tbody>
</table>
<script>
$(document).ready(function() {
    $('.fieldinfo').clickover({'html': true});
});
</script>
