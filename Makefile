install:
	python3 -m venv venv
	source venv/bin/activate
	python install -r requirements.txt

test:
	python -m pytest tests

test-scp:
	python -m pytest tests/test_scp_connect.py

