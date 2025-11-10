🌵 DeepL 핫키 번역기 (Text Processor Service)

선택한 텍스트를 즉시 DeepL로 번역하고, 결과를 작은 팝업창으로 화면에 띄워주는 경량화된 시스템 트레이 상주 프로그램입니다.

✨ 주요 기능

즉시 번역: 핫키(Ctrl + \ 또는 Ctrl + F10 등 사용자가 설정한 키)를 누르면, 마우스로 선택된 텍스트를 클립보드로 복사하여 즉시 번역합니다.

팝업 결과: 번역 결과를 작은 투명 팝업창으로 화면 오른쪽 하단에 표시합니다.

자동 언어 감지: 텍스트가 한국어이면 영어(EN-US)로, 영어/기타 언어이면 한국어(KO)로 자동 번역합니다.

긴 줄 정리: PDF 등에서 발생하는 하이픈(-)과 줄 바꿈(-\n)을 자동으로 정리하여 정확하게 번역합니다.

🛠️ 1단계: 준비물 (환경 설정)

프로그램을 실행하거나 .exe 파일을 직접 만들기 위해 필요한 준비물입니다.

1. Python 설치

프로그램은 Python으로 작성되었으므로, Python 공식 웹사이트에서 최신 버전을 다운로드하여 설치해야 합니다. (설치 시 **"Add Python to PATH"**를 반드시 체크해 주세요.)

2. DeepL API Key 발급

이 프로그램은 DeepL의 API를 사용합니다. 유료 DeepL Pro 계정이나 DeepL API Free 계정에서 API 키를 발급받아야 합니다.

💻 2단계: 프로그램 설치 및 실행 (소스 코드)
1. 코드 다운로드

터미널(명령 프롬프트 또는 PowerShell)을 열고 Git을 이용해 코드를 다운로드합니다.

code
Bash
download
content_copy
expand_less
# 원하는 폴더로 이동합니다.
cd [원하는 폴더 경로]

# GitHub에서 파일을 다운로드합니다.
git clone https://github.com/sk-crevis/text-cleaner-translator.git

# 다운로드한 폴더로 이동합니다.
cd text-cleaner-translator
2. 필수 라이브러리 설치

프로그램이 작동하는 데 필요한 모든 라이브러리를 한 번에 설치합니다.

code
Bash
download
content_copy
expand_less
pip install -r requirements.txt
3. 프로그램 실행

이제 코드를 직접 실행해 볼 수 있습니다.

code
Bash
download
content_copy
expand_less
python text_processor.py

API 키 입력: 실행 후, DeepL API 키를 입력하라는 팝업창이 뜨면, 2단계에서 발급받은 키를 입력하고 확인을 누릅니다. (이 키는 사용자 컴퓨터의 숨겨진 폴더에 저장됩니다.)

핫키 사용: 프로그램이 시스템 트레이(시계 옆 작은 아이콘 공간)에 🌵 선인장 아이콘으로 실행됩니다. Ctrl + \ (틸드/물결표 ~ 키 옆의 백틱 ` 키)를 누른 후 텍스트를 선택하고 다시 핫키를 누르면 번역 결과가 팝업으로 나타납니다.

🔨 3단계: 실행 파일(.exe) 만들기 (선택 사항)

다른 컴퓨터에서 Python 설치 없이 바로 실행하거나, 더 편리하게 사용하고 싶을 때 이 과정을 따르세요.

1. PyInstaller 설치

.exe 파일을 만들어주는 도구인 PyInstaller를 설치합니다.

code
Bash
download
content_copy
expand_less
pip install pyinstaller
2. PyInstaller 명령어 실행 (매우 중요!)

ttkbootstrap 테마 파일과 pystray 아이콘 파일을 .exe에 제대로 포함시키기 위해 아래 명령어를 정확하게 실행해야 합니다.

🚨 주의: 아래 명령의 [파이썬 경로] 부분은 사용자의 컴퓨터 환경에 따라 직접 수정해야 합니다.

파이썬 경로 찾기: 터미널에서 아래 명령을 입력하여 파이썬 라이브러리가 설치된 경로를 확인합니다.

code
Bash
download
content_copy
expand_less
pip show ttkbootstrap

결과 중 Location: C:\Users\...\venv\Lib\site-packages와 같은 경로를 확인하고, 이 경로의 ...site-packages까지만 복사합니다.

.exe 파일 만들기: 복사한 경로를 아래 명령어의 [여기에 복사한 경로를 붙여넣기] 부분에 붙여넣어 명령어를 완성합니다.

code
Bash
download
content_copy
expand_less
pyinstaller --onefile --noconsole ^
--name "DeepLTranslator" ^
--hidden-import "PIL._tkinter_finder" ^
--add-data "[여기에 복사한 site-packages 경로]\ttkbootstrap\themes;ttkbootstrap/themes" ^
text_processor.py

^ 기호는 줄 바꿈을 의미하며, 한 줄로 길게 입력해도 됩니다.

3. .exe 파일 확인

명령어 실행이 끝나면, 프로젝트 폴더 안에 **dist**라는 폴더가 새로 생깁니다. 이 폴더 안에 있는 DeepLTranslator.exe 파일을 실행하면 됩니다. 이 파일 하나만 다른 사람에게 배포할 수 있습니다.
