DOCBASE=report
GRAPHICS=

all: $(GRAPHICS) $(DOCBASE).pdf clean

graphics/%-plot.ps: graphics/%-gnuplot.txt
	gnuplot $<

graphics/%.pdf: graphics/%.dot
	dot $< -Tps2 -o $@.ps
	ps2pdf $@.ps $@
	rm $@.ps

graphics/%.pdf: graphics/%.dia
	dia -t eps -e $@.eps $<
	epstopdf --outfile=$@ $@.eps
	rm $@.eps

graphics/%.pdf: graphics/%.ps
	ps2pdf $< $@

graphics/%-crop.pdf: graphics/%.pdf
	pdfcrop $<

$(DOCBASE).pdf: $(DOCBASE).tex
	pdflatex $(DOCBASE).tex
	pdflatex $(DOCBASE).tex

clean:
	@rm -f $(DOCBASE).aux $(DOCBASE).log *~

kill:
	rm -f *.pdf *.ps $(GRAPHICS)
