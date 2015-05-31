<html>
<link rel="stylesheet" type="text/css" href="/static/js/jgabc/style/bootstrap.css" media="all" />
<link rel="stylesheet" type="text/css" href="/static/js/jgabc/style/style.css" />
<link rel="stylesheet" type="text/css" href="/static/js/jgabc/style/jquery-ui-1.10.3.custom.min.css" />
<script src="/static/js/jgabc/js/jquery.min.js" type="text/javascript"></script>
<script src="/static/js/jgabc/js/jquery-ui-1.10.3.custom.min.js" type="text/javascript"></script>
<script src="/static/js/jgabc/js/bootstrap.min.js"></script>
<script src="/static/js/jgabc/js/main.js"></script>
<script src="/static/js/jgabc/jgabc.js"></script>
<script src="/static/js/jgabc/psalmtone.js"></script>
<script src="/static/js/jgabc/sink.js"></script>
<script src="/static/js/jgabc/audiolet.js"></script>
<script src="/static/js/jgabc/transcriber.html.js"></script>
<script type="text/javascript">
    window.onbeforeunload = function(){
        return "Attention : si vous quittez cette page, vos modifications seront perdues.";
};
</script>
<style>
.btn-groups {
  width: 370px;
  height: auto;
  overflow-y: auto;
  float: left;
  margin-left: 5px;
  padding-left: 0px;
}
.print-hide {
  width:auto;
  margin-left: 385px;
}
textarea{
  padding:0px;
  float:right;
}
.dp{
  padding-right:16px;
}
.tap{
  padding-right:2px;
}
td{
  padding:0px;
}
#chant-parent2{
  width:auto;
  margin-left:385px;
  height:auto;
}
#chant-parent{
  border:1px solid #aaa;
  overflow-y:auto;
  height:auto;
}
#chant-pad{
  padding:0 0.1in;
}
#chant-preview{
  margin:0.1in auto auto;
}
input[type=checkbox]{
  margin-top:2px;
  margin-bottom:2px;
}
textarea{
  resize:none;
  float:right;
}
</style>


<div style="width:100%;margin-bottom:5px" class="titre">
  <div style="float:right">
    <a href='#' id='lnkPdfDirect'>{{_('Enregistrer')}}</a>
  </div>
</div>


<!-- Ceci est importé depuis Creat'Partition -->

<div id="groupes" class="btn-groups">
    <b>Caractères spéciaux </b> <br>
        <div style="float:left">
           <button class="btn" onclick="ecriretexte('á')">á</button>
           <button class="btn" onclick="ecriretexte('é')">é</button>
           <button class="btn" onclick="ecriretexte('í')">í</button>
           <br>
           <button class="btn" onclick="ecriretexte('ó')">ó</button>
           <button class="btn" onclick="ecriretexte('ú')">ú</button>
           <button class="btn" onclick="ecriretexte('ý')">ý</button>
        </div>
        <div style="float:right">
           <button class="btn" onclick="ecriretexte('℟')">℟</button>
           <button class="btn" onclick="ecriretexte('℣')">℣</button>
           <br>
           <button class="btn" onclick="ecriretexte('†')">†</button>
           <button class="btn" onclick="ecriretexte('✠')">✠</button>
        </div>
        <div style="text-align:center;">
           <button class="btn" onclick="ecriretexte('æ')">æ</button>
           <button class="btn" onclick="ecriretexte('ǽ')">ǽ</button>
           <br>
           <button class="btn" onclick="ecriretexte('œ')">œ</button>
           <button class="btn" onclick="ecriretexte('œ́')">œ́</button>
        </div>
    <b>Palette</b>
    <div id="groupe_1" class="btn-mini-group">
        <div style="float:right">
                <button class="btn" onclick="ecrirepartition(' ')">Syllabe<br>suivante</button>
        </div>
        <div style="float:left">
            <a>Hauteurs</a></br>
            <button class="btn-mini" onclick="ecrirepartition('a')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('b')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('c')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('d')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('e')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('f')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('g')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('h')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('i')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('j')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('k')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('l')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('m')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
        </div>
    </div>

    <br><br><br><br><br>
    <div id="groupe_2" class="btn-mini-group">
        <div style="float:left">
            <a >Altérations</a><br />
            <button class="btn-mini" onclick="ecrirepartition('x')" style="font-size:18px"><img src="/static/js/jgabc/img/bemol.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('y')" style="font-size:18px"><img src="/static/js/jgabc/img/becarre.png" class="img"></button>
            <button class="btn-mini" onclick="ecrirepartition('#')" style="font-size:18px"><img src="/static/js/jgabc/img/dieze.png" class="img"></button>
        </div>
        <div style="margin-left:100px">
            <a>Durées</a><br />
            <div>
                <button class="btn" onclick="ecrirepartition('.')">·</button>
                <button class="btn" onclick="ecrirepartition('_')">−</button>
                <button class="btn" onclick="ecrirepartition('\'')">'</button>
            </div>
        </div>
        <div style="margin-left:100px">
            <a>Coupures</a><br />
            <div>
                <button class="btn" onclick="ecrirepartition('!')">!</button>
                <button class="btn" onclick="ecrirepartition('/')">/</button>
                <button class="btn" onclick="ecrirepartition('//')">//</button>
                <button class="btn" onclick="ecrirepartition('\\ ')"> </button>
        </div>
    </div>

    <div id="groupe_3" class="btn-mini-group">
        <div style="float:left">
        <a >Neumes simples</a><br />
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume1.png" class="img"></button>
                <ul class="dropdown-menu">
                    <button class="btn-mini" onclick="ecrirepartition('a')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('b')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('c')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('d')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('e')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('f')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('g')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('h')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('i')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('j')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('k')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('l')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('m')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume2.png" class="img"></button>
                <ul class="dropdown-menu">
                    <button class="btn-mini" onclick="ecrirepartition('A')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('B')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('C')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('D')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('E')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('F')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('G')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('H')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('I')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('J')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('K')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('L')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('M')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume12.png" class="img"></button>
                <ul class="dropdown-menu">
                    <button class="btn-mini" onclick="ecrirepartition('av')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('bv')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('cv')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('dv')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('ev')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('fv')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('gv')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('hv')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('iv')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('jv')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('kv')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('lv')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('mv')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        </div>
    </div>
    <br><br><br>
    <div style="float:right">
        <a >Liquescences</a><br />
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume5.png" class="img"></button>
                <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('a~')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('b~')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('c~')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('d~')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('e~')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('f~')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('g~')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('h~')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('i~')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('j~')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('k~')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('l~')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('m~')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume7.png" class="img"></button>
                <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('a>')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('b>')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('c>')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('d>')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('e>')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('f>')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('g>')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('h>')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('i>')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('j>')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('k>')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('l>')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('m>')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume6.png" class="img"></button>
                <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('a<')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('b<')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('c<')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('d<')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('e<')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('f<')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('g<')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('h<')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('i<')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('j<')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('k<')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('l<')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('m<')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        <br>
        <div class="btn-group">
                <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume3.png" class="img"></button>
                    <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('A~')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('B~')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('C~')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('D~')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('E~')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('F~')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('G~')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('H~')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('I~')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('J~')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('K~')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('L~')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('M~')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                    </ul>
        </div>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume4.png" class="img"></button>
                <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('A>')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('B>')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('C>')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('D>')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('E>')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('F>')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('G>')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('H>')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('I>')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('J>')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('K>')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('L>')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                        <button class="btn-mini" onclick="ecrirepartition('M>')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
    </div>
    <div>
    <a >Neumes spéciaux</a><br>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume11.png" class="img"></button>
                <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('aw')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                                        <button class="btn-mini" onclick="ecrirepartition('bw')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('cw')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('dw')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ew')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('fw')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('gw')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('hw')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('iw')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('jw')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('kw')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('lw')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('mw')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume8.png" class="img"></button>
                <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('ao')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                                        <button class="btn-mini" onclick="ecrirepartition('bo')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('co')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('do')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('eo')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('fo')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('go')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ho')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('io')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('jo')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ko')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('lo')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                                        <button class="btn-mini" onclick="ecrirepartition('mo')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume9.png" class="img"></button>
                <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('ao~')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                                        <button class="btn-mini" onclick="ecrirepartition('bo~')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('co~')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('do~')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('eo~')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('fo~')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('go~')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ho~')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('io~')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('jo~')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ko~')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('lo~')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('mo~')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        <br>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume10.png" class="img"></button>
                <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('ao<')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                                        <button class="btn-mini" onclick="ecrirepartition('bo')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('co<')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('do<')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('eo<')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('fo<')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('go<')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ho<')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('io<')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('jo<')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ko<')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('lo<')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('mo<')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume13.png" class="img"></button>
                <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('as')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                                        <button class="btn-mini" onclick="ecrirepartition('bs')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('cs')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ds')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('es')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('fs')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('gs')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('hs')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('is')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('js')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ks')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ls')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ms')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
        <div class="btn-group">
            <button class="btn dropdown-toggle" data-toggle="dropdown"><img src="/static/js/jgabc/img/neume14.png" class="img"></button>
                <ul class="dropdown-menu">
                        <button class="btn-mini" onclick="ecrirepartition('as<')"><img src="/static/js/jgabc/img/note1.png" class="img"></button>
                                        <button class="btn-mini" onclick="ecrirepartition('bs<')"><img src="/static/js/jgabc/img/note2.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('cs<')"><img src="/static/js/jgabc/img/note3.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ds<')"><img src="/static/js/jgabc/img/note4.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('es<')"><img src="/static/js/jgabc/img/note5.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('fs<')"><img src="/static/js/jgabc/img/note6.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('gs<')"><img src="/static/js/jgabc/img/note7.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('hs<')"><img src="/static/js/jgabc/img/note8.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('is<')"><img src="/static/js/jgabc/img/note9.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('js<')"><img src="/static/js/jgabc/img/note10.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ks<')"><img src="/static/js/jgabc/img/note11.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ls<')"><img src="/static/js/jgabc/img/note12.png" class="img"></button>
                                    <button class="btn-mini" onclick="ecrirepartition('ms<')"><img src="/static/js/jgabc/img/note13.png" class="img"></button>
                </ul>
        </div>
    </div>
        <br>
        <div>
            <div id="groupe_4" class="btn-mini-group" style="float:left">
                <a >Cl&eacute;s</a><br />
                    <button class="btn-mini" onclick="ecrirepartition('c1 ')"><img src="/static/js/jgabc/img/cle1.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('c2 ')"><img src="/static/js/jgabc/img/cle2.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('c3 ')"><img src="/static/js/jgabc/img/cle3.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('c4 ')"><img src="/static/js/jgabc/img/cle4.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('f3 ')"><img src="/static/js/jgabc/img/cle5.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('f4 ')"><img src="/static/js/jgabc/img/cle6.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('cb3 ')"><img src="/static/js/jgabc/img/cle7.png" class="img"></button>
            </div>
            <div id="groupe_5" class="btn-mini-group" style="float:right">
                <a>Barres de s&eacute;paration</a></br>
                    <button class="btn-mini" onclick="ecrirepartition(',')"><img src="/static/js/jgabc/img/barre1.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('`')"><img src="/static/js/jgabc/img/barre2.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition(';')"><img src="/static/js/jgabc/img/barre3.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition(':')"><img src="/static/js/jgabc/img/barre4.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('::')"><img src="/static/js/jgabc/img/barre5.png" class="img"></button>
                    <button class="btn-mini" onclick="ecrirepartition('z0::')"><img src="/static/js/jgabc/img/custo.png" class="img"></button>
            </div>
        </div>
    </div>
</div>

<!-- Fin de Creat -->


<div class="print-hide">
<div style="width:100%;text-align:center;padding-bottom:4pt"><a href="#" id="lnkToggleMode">{{_('GABC simple')}}</a></div>
<div id="blankSpace" style="height:193px;">

<div id="twoBoxes" style="width:100%;overflow:hidden;float:right">
<div class="dp">
<div style="margin:auto;width:10.3in;max-width:100%"><div style="margin-left:4px;margin-right:-4px">
<table width="100%" style="margin-left:-2px;margin-top:-2px">
<tr><td width="50%">
  <label for="hymntext" title="This text box is for the text of the chant.  If the English checkbox is not checked it will be assumed to be Latin.">{{_('Texte')}}</label>&nbsp;&nbsp;
  <select style="float:right;margin:0;height:24px;max-width:30%;margin-right:20px" id="selLanguage" title="If you select English, the text will be run through the lyric hyphenator at juiciobrennan.com; it will only contact this site once every 5 seconds so you may have to wait a bit at times for the word syllabification to correct itself.  Unknown words are assumed to be a single syllable, and custom syllable breaks may be entered using = as in 'syl=la=ble'">
    <option value="la">Latin</option>
    <option value="en">English</option>
    <option value="pl">Polish</option>
  </select>
<br><div class="tap"><textarea id="hymntext" lang="la" style="height: 130pt; width: 100%; text-align:left;">{{paroles}}</textarea></div>
</td><td width="50%">
  <label for="hymngabc" title="This text box is for the GABC notation that would normally be in parentheses, as well as the GABC header.">GABC</label>
  <input type="checkbox" id="cbElisionHasNote"/><label for="cbElisionHasNote" title="You can signify an elision in the text by putting a vowel in parentheses.  If this box is checked, the elision will still have a punctum associated with it; if this is unchecked, that syllable will have no punctum.">{{_('Notes sur les élisions')}}</label>
  <br>
  <div class="tap">
    <textarea id="hymngabc" spellcheck="false" style="height: 130pt; width: 100%; text-align:left;">
{{entetes}}
{{'%%'}}
{{melodie}}
    </textarea>
  </div>
</td>
</table>
</div>
</div></div></div>
<div id="oneBox" style="display:none;width:100%;float:center;margin:auto">
<div class="dp">
<div style="width:100%;margin:auto">
<label for="editor" title="You can put GABC headers in this text box if you want them included in the GABC file download link below.  Any headers you type in will persist in local storage between sessions.">Integrated GABC</label>
<br><div class="tap"><textarea id="editor" spellcheck="false" style="height: 130pt; width: 100%;"></textarea></div>
</div>
</div></div>

</div>
<a href="#" id="lnkDownloadGabc" draggable target="_blank" style="display:block;margin-top:0.5em;margin-bottom:0.5em"></a>
</div>
<div id="chant-parent2">
  <div id="chant-parent">
    <div id="chant-pad">
      <div id="chant-preview"></div>
    </div>
  </div>
</div>

<form id="pdfFormDirect" method="post" action={{i18n_path('/' + emplacement)}}>
  <input type="hidden" id="pdff_gabc" name="gabc[]"/>
  <input type="hidden" name="action" value="enregistrer"/>
</form>
</html-->
