%def creer_input(prop, val):
    %if type(val[1]) is bool:
        <input name="{{prop}}" value="0" type="hidden">
        <input
            type="checkbox"
            name="{{prop}}"
            label="{{val[0]}} :"
            value="1"
            {{"checked" if val[1] else ""}}
        >
    %elif type(val[1]) in (int, float):
        <input
            class="nombre"
            name="{{prop}}"
            label="{{val[0]}} :"
            placeholder="{{val[0]}}"
            value="{{val[1]}}"
            required
        >
    %elif type(val[1]) is str:
        <input
            class="chaine"
            name="{{prop}}"
            label="{{val[0]}} :"
            placeholder="{{val[0]}}"
            value="{{val[1]}}"
            required
        >
    %elif type(val[1]) in (list, tuple):
        <input
            class="tuple"
            name="{{prop}}"
            label="{{val[0]}} :"
            placeholder="{{val[0]}}"
            value="{{','.join(str(v) for v in val[1])}}"
            required
        >
    %end
%end

<div id="zonesaisie">
    <form method="post">
        <table>
        %for prop, val in sorted(proprietes.items()):
            <tr>
                <td>{{val[0]}}</td>
                <td>
                %creer_input(prop, val)
                </td>
            </tr>
        %end
        </table>
        <button type="submit" name="action" value="exporter">{{_("Exporter")}}</button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
    </form>
</div>
