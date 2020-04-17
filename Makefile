.PHONY : clean build
clean:
	rm -f *.csv *.png

run: deaths_per_day.png

deaths_per_day.png:
	python my_experiment.py
	rm *.csv
