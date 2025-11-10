# ======================================================================
# Text Processor Service v7.9 (Stable) - StartUp Enabled
# ======================================================================

import tkinter as tk
import ttkbootstrap as ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox, simpledialog

import pyperclip
import re
import deepl
import os
import time
from threading import Thread
from queue import Queue, Empty

import keyboard
from PIL import Image, ImageDraw, ImageFont
import pystray

# ⬇️ 시작 프로그램 등록을 위한 라이브러리 추가
import sys
import winreg


# ======================================================================
# 1. 팝업창 UI 정의
# ======================================================================
class PopupWindow(ttk.Toplevel):
    def __init__(self, translated_text, master=None):
        super().__init__(master=master)
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        self.attributes('-alpha', 0.95)

        # 위치 및 크기
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 400
        window_height = 200
        x = screen_width - window_width - 20
        y = screen_height - window_height - 60
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # 상단 제목바
        self.grip = ttk.Frame(self, bootstyle="primary")
        self.grip.pack(fill='x', pady=(1, 0), padx=(1, 1))

        # inverse 스타일 제거
        title = ttk.Label(self.grip, text="  번역 결과 (DeepL)", bootstyle="primary")
        title.pack(side='left', padx=10)

        close_btn = ttk.Button(self.grip, text='✕', bootstyle="primary", command=self.destroy)
        close_btn.pack(side='right', padx=5)

        self.grip.bind("<ButtonPress-1>", self.start_move)
        self.grip.bind("<B1-Motion>", self.do_move)
        title.bind("<ButtonPress-1>", self.start_move)
        title.bind("<B1-Motion>", self.do_move)

        # 본문 영역
        text_frame = ttk.Frame(self, bootstyle="secondary")
        text_frame.pack(expand=True, fill='both', padx=(1, 1), pady=(0, 1))

        text_area = ScrolledText(text_frame, wrap='word', font=("Malgun Gothic", 10))
        text_area.pack(expand=True, fill='both')
        text_area.insert('1.0', translated_text)
        text_area.configure(state='disabled')

        self.bind_all("<Control-w>", lambda e: self.destroy())
        self.bind_all("<Escape>", lambda e: self.destroy())
        self.focus_force()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")


# ======================================================================
# 2. 메인 애플리케이션 클래스
# ======================================================================
class App:
    def __init__(self, api_key):
        self.api_key = api_key
        self.translator = self.initialize_translator()

        if not self.translator:
            messagebox.showerror("인증 오류", "API 키가 유효하지 않아 번역기를 초기화할 수 없습니다.")
            self.is_ready = False
            return

        self.root = self.create_dummy_root()
        self.result_queue = Queue()
        self.processing = False
        self.icon = None
        self.is_ready = True
        
        # ⬇️ 시작 프로그램 등록 로직 호출 추가
        if self.is_ready:
            self.register_as_startup()

    def create_dummy_root(self):
        root = ttk.Window()
        root.withdraw()
        return root

    # 시스템 트레이 아이콘
    def create_emoji_icon(self, emoji: str) -> Image:
        width, height = (64, 64)
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        font_path = "C:/Windows/Fonts/seguiemj.ttf"
        try:
            font = ImageFont.truetype(font_path, size=int(width * 0.7))
        except IOError:
            font = ImageFont.load_default()
        text_bbox = draw.textbbox((0, 0), emoji, font=font)
        x = (width - (text_bbox[2] - text_bbox[0])) / 2
        y = (height - (text_bbox[3] - text_bbox[1])) / 2
        draw.text((x, y), emoji, font=font, embedded_color=True)
        return image

    # 메인 실행 루프
    def run(self):
        self.check_queue()

        Thread(target=self.setup_hotkey, daemon=True).start()

        image = self.create_emoji_icon("☯️")
        menu = (pystray.MenuItem('종료', self.quit_app),)
        self.icon = pystray.Icon("TextProcessor", image, "Text Processor", menu)

        # pystray를 별도 스레드에서 실행
        Thread(target=self.icon.run, daemon=True).start()
        self.root.mainloop()

    def check_queue(self):
        try:
            result = self.result_queue.get(block=False)
            if result:
                PopupWindow(result, master=self.root)
        except Empty:
            pass
        finally:
            self.root.after(100, self.check_queue)

    def setup_hotkey(self):
        try:
            keyboard.add_hotkey('ctrl+`', self.on_hotkey_pressed)
            # 불필요한 keyboard.wait() 제거됨
        except Exception as e:
            print(f"[핫키 오류] {e}")

    def on_hotkey_pressed(self):
        if self.processing:
            return
        self.processing = True
        Thread(target=self.process_text_task, daemon=True).start()

    def process_text_task(self):
        try:
            original_clipboard = pyperclip.paste()

            # 복사 명령 및 안정 대기
            keyboard.send('ctrl+c')

            selected_text = ""
            for _ in range(10):
                new_clip = pyperclip.paste()
                if new_clip and new_clip != original_clipboard:
                    selected_text = new_clip
                    break
                time.sleep(0.1)

            pyperclip.copy(original_clipboard)

            if not selected_text:
                print("[INFO] 선택된 텍스트 없음")
                return

            cleaned_text = self.clean_text(selected_text)
            translated_text = self.translate_text(cleaned_text)

            if translated_text:
                self.result_queue.put(translated_text)

        except Exception as e:
            print(f"[처리 오류] {e}")
        finally:
            self.processing = False

    def clean_text(self, text):
        cleaned = text.replace('-\n', '')
        cleaned = re.sub(r'(\S)\n(\S)', r'\1 \2', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()

    def translate_text(self, text):
        if not self.translator:
            return "DeepL 번역기 초기화 실패"
        try:
            is_korean = re.search("[\uac00-\ud7a3]", text)
            target_lang = "EN-US" if is_korean else "KO"
            result = self.translator.translate_text(text, target_lang=target_lang)
            print(f"[DeepL 번역 성공] {text[:50]}... → {result.text[:50]}...")
            return result.text
        except deepl.DeepLException as e:
            return f"DeepL API 오류:\n{e}"
        except Exception as e:
            return f"알 수 없는 오류:\n{e}"

    def initialize_translator(self):
        try:
            return deepl.Translator(self.api_key)
        except Exception as e:
            print(f"[DeepL 초기화 실패] {e}")
            return None

    def quit_app(self):
        try:
            if self.icon:
                self.icon.stop()
        except Exception:
            pass
        self.root.quit()
        os._exit(0)
        
    # ⬇️ 새로운 메서드: 시작 프로그램 등록
    def register_as_startup(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            # .exe 파일 경로를 얻는 더 안정적인 방법
            if getattr(sys, 'frozen', False):
                # .exe (PyInstaller)로 실행됨
                program_path = sys.executable
            else:
                # .py 파일로 실행됨
                program_path = os.path.abspath(__file__)
            
            winreg.SetValueEx(
                key,
                "TextProcessorService",  # 시작 프로그램에 표시될 이름
                0,
                winreg.REG_SZ,
                f'"{program_path}"'
            )
            winreg.CloseKey(key)
        except Exception:
            # 등록 권한이 없을 경우를 대비해 조용히 넘어갑니다.
            pass


# ======================================================================
# 3. 설정 관리
# ======================================================================
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.text_processor')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.ini')


def load_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return f.read().strip()
    return None


def save_api_key(key):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            f.write(key)
    except Exception as e:
        messagebox.showerror("저장 오류", f"API 키 저장에 실패했습니다: {e}")


def get_api_key_from_user():
    root = tk.Tk()
    root.withdraw()
    key = simpledialog.askstring(
        "DeepL API Key 필요",
        "DeepL API 인증 키를 입력해주세요.\n(계정 페이지에서 복사할 수 있습니다)",
        parent=root,
        show='*'
    )
    root.destroy()
    return key


# ======================================================================
# 4. 프로그램 시작점
# ======================================================================
if __name__ == "__main__":
    api_key = load_api_key()
    if not api_key:
        api_key = get_api_key_from_user()
        if api_key:
            save_api_key(api_key)

    if api_key:
        app = App(api_key)
        if app.is_ready:
            app.run()
