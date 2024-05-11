python -m venv test

.\test\Scripts\activate

python -m pip install -r requirements.txt

python -m pip list --format=freeze > requirements.txt