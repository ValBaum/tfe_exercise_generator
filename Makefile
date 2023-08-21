run :
	python main.py
pdf :
	latexmk -pdf -silent exercises/*.tex -outdir=exercises
	rm exercises/*.log exercises/*.aux exercises/*.fdb_latexmk exercises/*.fls
clean :
	rm -f exercises/* 
	rm -f solutions/* 
	rm -f feedbacks/* 
pakage:
	pip install matplotlib
	pip install pandas
c:
	gcc -o t test.c
	./t
