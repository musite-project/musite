%from deps import auth as a

Les <em class='suppr'><del>suppressions</del></em> sont en italique,
les <strong class='add'>additions</strong> en gras.
<br>

<h2>Changements apportés par la modification {{commit}} :</h2>

<code>
{{!modifications}}
</code>

<br>

<h2>Changements effectués depuis cette modification :</h2>

<code>
{{!differences}}
</code>

<br>

%try:
%if a.authentifier(rq.auth[0], rq.auth[1]) and rq.auth[0] != 'anonyme':
<form method="post" action="/_retablir/{{emplacement}}">
    <button type="submit" name='commit' value='{{commit}}'>Revenir à cette version</button>
</form>
%end
%except TypeError: pass
%end
