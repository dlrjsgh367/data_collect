# choco 설치
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# vscode 최신 버전으로 업그레이드
choco upgrade vscode

python -m venv test

.\test\Scripts\activate

python -m pip install -r requirements.txt

python -m pip list --format=freeze > requirements.txt