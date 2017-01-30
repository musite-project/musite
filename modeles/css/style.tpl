@import url("/static/css/libertine.css");

html,body {
    width:100%;
    margin: 0px;
    padding: 0px;
    font-family: LinLibertineO;
    font-size:14pt;
}

#logo {
    position:absolute;
    top:0px;
    left:0px;
    margin: 0px;
    padding: 0px;
    font-size: 108%;
    width: 100px;
    height:100px;
    float:left;
}

#logo-img {
    width:150px;
}

#entete {
    border: 0px solid #ccc;
    background-color: #fff;
    margin: 0px;
    padding: 1px;
    font-size: 108%;
    margin-left:100px;
    padding-left:20px;
    height:40px;
}

#chemin {
    position:absolute;
    top:60px;
    left:150px;
    white-space:nowrap;
    max-width:100%;
    overflow:auto;
}

#langues {
    position:absolute;
    top:10px;
    right:0px;
    padding-right:20px;
}

#btn-menu {
    position:absolute;
    visibility:hidden;
    top:0px;
    left:0px;
    right:0px;
    width:40px;
    height:45px;
    line-height:0px;
    margin:0px;
    padding:0px;
    text-align:center;
    font-size:24pt;
}

#btn-midi {
    width:50px;
    height:50px;
    text-align:center;
    margin:0px;
    padding:0px;
    font-size:24pt;
}

#menu {
    position:absolute;
    top:170px;
    bottom:0px;
    left:0px;
    right:0px;
    background-color: white;
    margin: 0px;
    margin-left: 10px;
    font-size: 93%;
    width: 130px;
    padding: 0px;
    float:left;
    overflow:auto;
    text-align:left;
}

#acces {
    position:relative;
    top:auto;
    bottom:0px;
    left:0px;
    right:0px;
}

#titre {
    text-align:left;
    font-size:180%;
}

#corps {
    border: 1px solid #ccc;
    box-sizing:border-box;
    -moz-box-sizing:border-box; /* Firefox */
    -webkit-box-sizing:border-box; /* Safari */
    position:absolute;
    top:80px;
    bottom:0px;
    left:0;
    right:10px;
    min-height:400px;
    height: auto;
    overflow:auto;
    padding: 4px;
    font-size: 108%;
    margin-left:140px;
    margin-right:auto;
}

#utilisateurs {
    position:absolute;
    top:0px;
    bottom:0px;
    left:0px;
    right:51%;
}

A:link { text-decoration: none; color: #303030 }
A:visited { text-decoration: none; color: #303030 }
A:active { text-decoration: none; color: black }
A:hover { text-decoration: underline; color: gray; }

sub { vertical-align: sub; }
sup { vertical-align: super; }
sub, sup { line-height: 0.3em; font-size: 60%; }

*
{
    text-align:justify;
}

h1
{
    text-align: left;
    font-size: 140%;
    padding-left: 10px;
}

h2
{
    text-align: left;
    font-size: 120%;
}

body{
    counter-reset: h1 h2 h3;
    font-size: 90%;
}

ul.listefichiers {
    list-style: none;
}

a.dossier {
    font-weight: bold;
}

#menu ul {
    list-style: none;
    margin-top: 0px;
    margin-left: 1ex;
    padding-left: 0;
}

#groupes {
    position:absolute;
    top:0px;
    bottom:0px;
    right:0px;
    left:51%;
}

table {
    font-size: 100%;
}

table.export {
    border: 1px solid black;
}

table.export table.export {
    border-top: 1px solid black;
    border-bottom: 1px solid black;
    width:100%;
}

tr.export {
    border: none;
}

code {
    text-align: left;
    font-size: 90%;
    word-wrap: break-word;
    overflow-wrap: break-word;
    word-break: break-all;
    white-space: pre-wrap;
    overflow: auto;
}

textarea {
    width: 80%;
    height: 80%;
}

strong.add {
    color: green;
}

em.suppr {
    color: red;
}

#saisie {
    position: absolute;
    top:0px;
    bottom: 50px;
    left:0px;
    right:10px;
}

#boutons_editeur {
    position: absolute;
    top:auto;
    bottom:10px;
}

#expr {
    width: 120px;
}

.important A {
    color: red;
    font-weight: bold;
    font-style: italic;
}

@media screen and (max-device-width: 840px) {
    html,body {
        font-size:16pt;
    }
    #entete h1{
        line-height:.4ex;
        font-size:120%;
    }
    #entete {
        margin-left:50px;
    }
    #chemin {
        top:50px;
        left:20px;
    }
    #corps {
        margin-left:0px;
        right:0px;
    }
    #logo-img {
        width:100px;
    }
    #btn-menu {
        visibility:visible;
    }
    #menu {
        display:none;
        top:0px;
        left:30px;
        width: 200px;
        border: 1px solid #ccc;
    }
    #btn-menu:hover + #menu {
        display:inline-block;
    }
    #menu:hover {
        display:inline-block;
    }
}

{{ext}}
