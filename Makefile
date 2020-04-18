.PHONY : clean run
clean:
	rm -f *.csv *.png

run: deaths_per_day.png

deaths_per_day.png: my_experiment.py
	python my_experiment.py
	rm *.csv
