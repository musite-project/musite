FICHIER="00-Document"
CPU_CORES=`cat /proc/cpuinfo | grep -m1 "cpu cores" | sed s/".*: "//`
LILY_CMD = lilypond -ddelete-intermediate-files \
                    -dno-point-and-click -djob-count=$(CPU_CORES)
LATEX_CMD = lualatex -interaction=batchmode --shell-escape

individuel:
	TEXINPUTS="lib:" $(LATEX_CMD) $(FICHIER)

document:
	./dependances.sh
	TEXINPUTS="lib:" lilypond-book -P "$(LILY_CMD)" -f latex --pdf --latex-program=lualatex --output=Fait/ $(FICHIER).tex
	(export TEXINPUTS="lib:" ; cd Fait ; $(LATEX_CMD) $(FICHIER) ; makeindex -s lib/manuel.ist 00-Document.idx ; $(LATEX_CMD) $(FICHIER))
	cp Fait/$(FICHIER).pdf .

rapide:
	TEXINPUTS="lib:" lualatex --shell-escape -synctex=1 00-Document.tex ; makeindex -s lib/manuel.ist 00-Document.idx ; TEXINPUTS="lib:" lualatex --shell-escape -synctex=1 00-Document.tex

schola:
	./dependances.sh
	TEXINPUTS="lib:" lilypond-book -P "$(LILY_CMD)" -f latex --pdf --latex-program=lualatex --output=Fait/ $(FICHIER).tex
	(export TEXINPUTS="lib:" ; cd Fait ; $(LATEX_CMD) '\def\dest{schola}\input{$(FICHIER)}' ; $(LATEX_CMD) '\def\dest{schola}\input{$(FICHIER)}')
	cp Fait/$(FICHIER).pdf .
	
debug:
	./dependances.sh
	TEXINPUTS="lib:" lilypond-book -P "$(LILY_CMD)" -f latex --pdf --latex-program=lualatex --output=Fait/ $(FICHIER).tex
	(export TEXINPUTS="lib:" ; cd Fait ; lualatex --shell-escape $(FICHIER) ; lualatex --shell-escape $(FICHIER))
	cp Fait/$(FICHIER).pdf .

tmp:
	./dependances.sh
	TEXINPUTS="lib:" lilypond-book -P "$(LILY_CMD)" -f latex --pdf --latex-program=lualatex --output=Fait/ tmp.tex
	(cd Fait ; rm tmp.toc ; TEXINPUTS="lib:" lualatex -interaction=nonstopmode --shell-escape tmp.tex)
