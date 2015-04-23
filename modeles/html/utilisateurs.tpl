%from deps import auth as a
%from etc import config as cfg
%import os
<div id="utilisateurs">

   <b>{{_("Ajout ou modification d'un utilisateur :")}}</b>
   <br>
   <br>
   <form method="post" action="/admin/utilisateurs">
      <input name="nom" placeholder="{{_("Nom")}}"></input>
      <br>
      <input name="mdp" type="password" placeholder="{{_("MdP")}}"></input>
      <br>
      <input name="mdp_v" type="password" placeholder="{{_("MdP (de nouveau)")}}"></input>
      <br><br>
      <button type="submit">Créer / modifier</button>
   </form>
   <br>

   <b>{{_("Utilisateurs :")}}</b>
   <table>
      %for utilisateur in sorted(a.utilisateurs()):
      <tr>
         <td>{{utilisateur}}&nbsp&nbsp&nbsp</td>
         <td><small>
            <a href=/admin/supprimerutilisateur/{{utilisateur}}>{{_("supprimer")}}</a>
            </small>
         </td>
      </tr>
      %end
   </table>

</div>

<br>

<div id="groupes">

   <script language="javascript" type="text/javascript"
           src="/static/js/edit_area/edit_area_full.js"></script>
   <script language="javascript" type="text/javascript">
      editAreaLoader.init({
          id : "fichier"
          , language: "{{cfg.LANGUE}}"
          , word_wrap:false
          , show_line_colors:false
          , start_highlight: false
      });
   </script>

   <b>Groupes :</b>
   <br>
   <br>
   <form method="post" action="/admin/groupes">
      %with open(os.path.join('etc', 'groupes'), 'r') as fichier:
      %groupes = fichier.read(-1)
      <textarea name="texte" id="fichier" cols="40" rows="10">{{groupes}}</textarea>
      %end
      <br>
      <button type="submit">{{_("Enregistrer")}}</button>
   </form>
</div>
