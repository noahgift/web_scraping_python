setup:
	#You may want to create an alias to automatically source this:
	# alias wstop="cd ~/src/web_scraping_python && source ~/.web_scraping_python/bin/activate"
	python3 -m venv ~/.web_scraping_python/

install:
	pip3 install -r requirements.txt

deploy-chalice-scrape-yahoo:
	cd chalice_apps/scrape-yahoo && chalice deploy

test:
	#PYTHONPATH=. && pytest -vv --cov=wslib tests/*.py
	PYTHONPATH=. && py.test --nbval-lax notebooks/*.ipynb

lint:
	pylint --disable=R,C wscli chalice_apps/scrape-yahoo/*.py

