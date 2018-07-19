## How to generate the tutorial

The tutorial is written in markdown, so you can convert it into a pdf file via pandoc/latex or markdown-pdf. The former is to convert markdown files into latex first and compile to the produce file while the latter converts html file first and then use Phantomjs render the pages into a pdf file.

So you can either install [pandoc](https://pandoc.org/) and texlive and then 
```
make pandoc
```

or directly use [docker](https://docs.docker.com/install/) image via
```
make docker
docker run -v `pwd`:/source jagregory/pandoc -f markdown -t html5 myfile.md -o myfile.html
```
Make sure you have installed docker and add your username into docker group.

or install markdown-pdf via `npm install -g markdown-pdf` and then 
```
make nodejs
```
Make sure you have installed [nodejs](https://nodejs.org/). 

## Contribution
Welcome to fork and commit pull request.
