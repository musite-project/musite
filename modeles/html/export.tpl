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
        >
    %elif type(val[1]) is str:
        <input
            class="chaine"
            name="{{prop}}"
            label="{{val[0]}} :"
            placeholder="{{val[0]}}"
            value="{{val[1]}}"
        >
    %elif type(val[1]) in (list, tuple):
        <input
            class="tuple"
            name="{{prop}}"
            label="{{val[0]}} :"
            placeholder="{{val[0]}}"
            value="{{','.join(str(v) for v in val[1])}}"
        >
    %elif type(val[1]) is dict:
        %creer_tableau(val[1])
    %end
%end

%def creer_tableau(props):
    <table class="export">
    %for prop, val in sorted(props.items()):
        <tr class="export">
            <td>{{val[0]}}&nbsp</td>
            <td>
            %creer_input(prop, val)
            </td>
        </tr>
    %end
    </table>
%end

<div id="zonesaisie">
    <form method="post">
        %creer_tableau(proprietes)
        <button type="submit" name="action" value="exporter">{{_("Exporter")}}</button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{_("Retour")}}</button>
    </form>
</div>
