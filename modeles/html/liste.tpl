<ul class="listefichiers">
    %for element in liste:
    <li>{{!element}}</li>
    %end
</ul>

%try:
<br><br>
{{!readme}}
%except NameError: pass
%end
