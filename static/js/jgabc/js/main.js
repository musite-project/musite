
function recuprythmeenote(){
		document.getElementById("prependedInput").value = chiffre_lettrine.firstChild.nodeValue;
}

function ecrirenoteryhtme(){
	chiffre_lettrine.firstChild.nodeValue=document.getElementById("prependedInput").value;
}

function ecrireediteur(e){
        var startPos = document.getElementById("editor").selectionStart;
        var endPos = document.getElementById("editor").selectionEnd;
        document.getElementById("editor").value = document.getElementById("editor").value.substring(0, startPos)
            + e
            + document.getElementById("editor").value.substring(endPos, document.getElementById("editor").value.length);
		$('#editor').keyup();
        document.getElementById('editor').focus();
        var place = startPos + e.length;
        document.getElementById('editor').setSelectionRange(place, place);
}

function ecrirepartition(e){
    if($("#twoBoxes").is(':hidden')){
        ecrireediteur(e);
    } else {
        var startPos = document.getElementById("hymngabc").selectionStart;
        var endPos = document.getElementById("hymngabc").selectionEnd;
        document.getElementById("hymngabc").value = document.getElementById("hymngabc").value.substring(0, startPos)
            + e
            + document.getElementById("hymngabc").value.substring(endPos, document.getElementById("hymngabc").value.length);
		$('#hymngabc').keyup();
        document.getElementById('hymngabc').focus();
        var place = startPos + e.length;
        document.getElementById('hymngabc').setSelectionRange(place, place);
    }
}

function ecriretexte(e){
    if($("#twoBoxes").is(':hidden')){
        ecrireediteur(e);
    } else{
        var startPos = document.getElementById("hymntext").selectionStart;
        var endPos = document.getElementById("hymntext").selectionEnd;
        document.getElementById("hymntext").value = document.getElementById("hymntext").value.substring(0, startPos)
            + e
            + document.getElementById("hymntext").value.substring(endPos, document.getElementById("hymntext").value.length);
		$('#hymntext').keyup();
        document.getElementById('hymntext').focus();
        var place = startPos + e.length;
        document.getElementById('hymntext').setSelectionRange(place, place);
    }
}

function visible(){
	$('#twoBoxes').css('overflow','visible');
}

function recuppolice(){
	document.getElementById("policeInput").value = $('.goudy').css('fontFamily');
}

function ecrirepolice(){
	$('.goudy').css('fontFamily',document.getElementById("policeInput").value);
	$('#alert_popup').css('visibility','visible');
	$('#alert_popup').css('height','38px');
	
}

function recuptaillepolice(){
	document.getElementById("tailleInput").value = $('.goudy').css('fontSize');
}

function recuptaillepolicepart(){
	document.getElementById("tailleInputPartition").value = $('#chant-parent').css('width');
}


function ecriretaillepolice(){
	$('.goudy').css('fontSize',document.getElementById("tailleInput").value );
}


function ecriretaillepartition(){
	$('#chant-parent').css('width',document.getElementById("tailleInputPartition").value );
}

function donwloadPDF(){
	window.print();
}
