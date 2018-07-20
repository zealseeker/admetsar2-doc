
py: 
	markdown_py -x fenced_code -x toc tutorial/guide.md | weasyprint --base-url=tutorial/ -s tutorial/css.css - guide.pdf

pandoc:
	pandoc -f markdown -t pdf tutorial/guide.md -o guide.pdf

.PHONY : pandoc clean

clean:
	rm *.pdf
