install:
	python3 -m venv venv
	source venv/bin/activate
	python install -r requirements.txt


test-scp:
	python -m pytest tests/test_scp_connect.py

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf venv

run:
	source venv/bin/activate && python cp2toto.py
