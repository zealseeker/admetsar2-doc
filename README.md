## How to generate the tutorial

The tutorial is written in markdown, so you can convert it into a pdf file via pandoc/latex or markdown-pdf. The former is to convert markdown files into latex first and compile to the produce file while the latter converts html file first and then use Phantomjs render the pages into a pdf file.

We prefer to use markdown-py and weasyprint to convert. Install them by `pip install -r requirement.txt` or see their references if you have dependency problems.

If you have already installed these two python packages, you can compile the document by:

```
make
```

or you can also use [pandoc](https://pandoc.org/) and texlive and then 
```
make pandoc
```


## Contribution
Welcome to fork and commit pull request.
