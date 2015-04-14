<table border='1'>
    <tr>
        %for cellule in tableau[0]:
        <th>{{cellule}}</th>
        %end
    %for ligne in tableau[1:]:
    <tr>
        %for cellule in ligne:
        <td>{{!cellule}}</td>
        %end
    </tr>
    %end
</table>
