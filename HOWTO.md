
How To
======


- Dump a vocabulary as csv file:

    (clld)robert@astroman:~/venvs/clld$ sql2csv --db "postgresql://robert@/wold2" --query "select p.id, p.name, p.description, string_agg(u.name, ', ') from parameter as p, valueset as vs, value as v, counterpart as cp, unit as u where vs.language_pk = 19 and vs.parameter_pk = p.pk and v.valueset_pk = vs.pk and v.pk = cp.pk and cp.word_pk = u.pk group by p.name, p.pk, p.id, p.description order by p.pk;" > lwt_sakha.csv

