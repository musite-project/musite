%def creer_input(prop, val, proprietes):
    %if type(val[1]) is bool:
        <input name="{{prop}}" value="0" type="hidden">
        <input
            type="checkbox"
            name="{{prop}}"
            label="{{val[0]}} :"
            value="1"
            {{"checked" if proprietes[prop] else ""}}
        >
    %elif type(val[1]) in (int, float):
        %if len(val) == 2:
            <input
                class="nombre"
                name="{{prop}}"
                label="{{val[0]}} :"
                placeholder="{{val[0]}}"
                value="{{proprietes[prop]}}"
            >
        %elif len(val) == 3:
            <select
                class="nombre"
                name="{{prop}}"
                label="{{val[0]}} :"
                placeholder="{{val[0]}}"
            >
            <option selected>{{proprietes[prop]}}</option>
            {{!'\n'.join('<option>' + option for option in val[2])}}
            </select>
        %end
    %elif type(val[1]) is str:
        %if len(val) == 2:
            <input
                class="chaine"
                name="{{prop}}"
                label="{{val[0]}} :"
                placeholder="{{val[0]}}"
                value="{{proprietes[prop]}}"
            >
        %elif len(val) == 3:
            <select
                class="chaine"
                name="{{prop}}"
                label="{{val[0]}} :"
                placeholder="{{val[0]}}"
            >
            <option selected>{{proprietes[prop]}}</option>
            {{!'\n'.join('<option>' + option for option in val[2])}}
            </select>
        %end
    %elif type(val[1]) in (list, tuple):
        <input
            class="tuple"
            name="{{prop}}"
            label="{{val[0]}} :"
            placeholder="{{val[0]}}"
            value="{{','.join(str(v) for v in proprietes[prop])}}"
        >
    %elif type(val[1]) is dict:
        %creer_tableau(val[1], proprietes)
    %end
%end

%def creer_tableau(listeprops, proprietes):
    <table class="export">
    %for prop, val in sorted(listeprops.items()):
        <tr class="export">
            <td>{{val[0]}}&nbsp</td>
            <td>
            %creer_input(prop, val, proprietes)
            </td>
        </tr>
    %end
    </table>
%end

<div id="zonesaisie">
    <form method="post">
        %creer_tableau(listeproprietes, proprietes)
        <button type="submit" name="action" value="exporter">{{_("Exporter")}}</button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{_("Retour")}}</button>
    </form>
</div>
