%from outils import msg
%from deps import auth as a

{{!msg.ac}}

<code>
{{!modifications}}
</code>

<br>

{{!msg.ad}}

<code>
{{!differences}}
</code>

<br>

%try:
%if a.authentifier(rq.auth[0], rq.auth[1]) and rq.auth[0] != 'anonyme':
<form method="post" action="/_retablir/{{emplacement}}">
    <button type="submit" name='commit' value='{{commit}}'>{{msg.ae}}</button>
</form>
%end
%except TypeError: pass
%end
