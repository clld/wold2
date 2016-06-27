${', '.join(c.name for c in list(ctx.primary_contributors))}${' (with ' + ', '.join(c.name for c in list(ctx.secondary_contributors)) + ')' if ctx.secondary_contributors else ''}. ${request.dataset.published.year if request.dataset.published else ctx.updated.year}. ${ctx.name} vocabulary.
In: ${request.dataset.formatted_editors()|n} (eds.)
${request.dataset.description}.
${request.dataset.publisher_place}: ${request.dataset.publisher_name}${', ' + str(entries) + 'entries' if entries else ''}.
(Available online at http://${request.dataset.domain}${request.resource_path(ctx)}, Accessed on ${h.datetime.date.today()}.)
