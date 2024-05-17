# choco 설치
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# vscode 최신 버전으로 업그레이드
choco upgrade vscode

python -m venv test

.\test\Scripts\activate

python -m pip install -r requirements.txt

python -m pip list --format=freeze > requirements.txt


error
1. https://www.inflearn.com/questions/949511/%EC%85%80%EB%A0%88%EB%8B%88%EC%9B%80-%EC%A0%95%EC%83%81-%EC%9E%91%EB%8F%99-%EB%90%98%EB%8B%A4%EA%B0%80-%EC%98%A4%EB%8A%98%EB%B6%80%EB%A1%9C-%EA%B0%91%EC%9E%90%EA%B8%B0-%EC%98%A4%EB%A5%98%EA%B0%80-%EB%B0%9C%EC%83%9D

2. https://chhan.tistory.com/44

3. https://38thzary.tistory.com/144

4. 엑셀 파일에 필터가 걸려 있으면 생기는 문제
https://stackoverflow.com/questions/75382340/python-pandas-read-excel-error-value-must-be-either-numerical-or-a-string-conta




pandas 텍스트 최대 너비 설정
import pandas as pd
pd.set_option('display.max_colwidth', None)