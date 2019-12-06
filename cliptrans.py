import time
import threading
import pyperclip
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import tkinter.font as font
from googletrans import Translator


class ClipboardWatcher(threading.Thread):
    def __init__(self, predicate, callback, pause=5.):
        super(ClipboardWatcher, self).__init__()
        self._predicate = predicate
        self._callback = callback
        self._pause = pause
        self._stopping = False

    def run(self):
        recent_value = ""
        while not self._stopping:
            try:
                tmp_value = pyperclip.paste()
            except:
                pass
            if tmp_value != recent_value:
                recent_value = tmp_value
                if self._predicate(recent_value):
                    self._callback(recent_value)
            time.sleep(self._pause)

    def stop(self):
        self._stopping = True

class ClipTrans(object):
    def __init__(self):
        # UI初期化
        self.root = tk.Tk()
        self.root.title('cliptrans')

        text_font = font.Font(self.root, family="Meiryo", size=12)

        self.locked = tk.BooleanVar()
        self.lock_chk = tk.Checkbutton(self.root, text='Lock', variable=self.locked)
        self.lock_chk.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.sentence_text = scrolledtext.ScrolledText(self.root, fg='#333', padx=12, pady=12, width=50, height=8)
        self.sentence_text.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.trans_text = scrolledtext.ScrolledText(self.root, fg='#333', font=text_font, padx=12, pady=12, width=50, height=8)
        self.trans_text.grid(column=0, row=2, sticky=(tk.N, tk.S, tk.E, tk.W))


        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=2)

        # 常に最前面
        self.root.attributes("-topmost", True)

        # クリップボード監視クラス生成
        self.watcher = ClipboardWatcher( lambda x:True, self.clip_translate, 1.)

        # ウインドウを閉じるときの動作
        on_closing = lambda : self.watcher.stop() or self.root.destroy()
        self.root.protocol("WM_DELETE_WINDOW", on_closing)

    def clip_translate(self, clipboard_content):
        # Lock中は翻訳しない
        if self.locked.get():
            return

        # 翻訳
        s = clipboard_content
        s = s.replace('\r\n', ' ')
        s = s.replace('\r', ' ')
        s = s.replace('\n', ' ')
        s = s.replace('. ', '.\n')
        trans_sentence = Translator().translate(s, src = "en", dest = "ja").text

        # 表示
        self.sentence_text.delete('1.0', 'end')
        self.trans_text.delete('1.0', 'end')
        self.sentence_text.insert('1.0', s)
        self.trans_text.insert('1.0', trans_sentence)

        # debug log
        #print('translate!')

    def start(self):
        self.watcher.start()
        self.root.mainloop()

def main():
    ClipTrans().start()

if __name__ == "__main__":
    main()
