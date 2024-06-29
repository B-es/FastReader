import flet as ft

class StartStopButton(ft.ElevatedButton):
    def __init__(self, start_text, stop_text, start_action, stop_action, long_action):
        super().__init__(text=start_text, disabled=True)
        
        self.state = False
        self.icon = ft.icons.PLAY_ARROW_ROUNDED
        
        def change_btn(state):
            if(state):
                self.text = stop_text
                self.icon = ft.icons.STOP_ROUNDED
            else:
                self.text = start_text
                self.icon = ft.icons.PLAY_ARROW_ROUNDED
            self.update()
            
        def change(state):
            change_btn(state)
            self.state = state
        
        self.change = change
        
        def on_click(e):       
            change_btn(not self.state)
            
            if(self.state):
                stop_action()
            else:
                start_action()
                
            self.state = not self.state
            
        def on_long_click(e):       
            if(self.state):
                long_action()
        
        self.on_click = on_click
        self.on_long_press = on_long_click
        
    def setEnable(self, state):
        self.disabled = not state
        self.update()

import re
import chardet 

class OpenFileWidget(ft.Column):
    def __init__(self, page, action):
        super().__init__(horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                                          alignment=ft.MainAxisAlignment.CENTER, 
                                          expand=1,)
        def parseText(s):
            splt = re.split('\n| ', s)
            while splt.count('') != 0:
                splt.remove('')
            return splt
  
        def detect_encoding(file_path): 
            with open(file_path, 'rb') as file: 
                detector = chardet.universaldetector.UniversalDetector() 
                for line in file: 
                    detector.feed(line) 
                    if detector.done: 
                        break
                detector.close() 
            return detector.result['encoding'] 
        
        def pick_files_result(e: ft.FilePickerResultEvent):
            def getText(file):
                enc = detect_encoding(file.path)
                with open(file.path, encoding=enc) as f:
                    return f.read()
            
            if e.files:
                text = list(map(getText, e.files))[0]
                data = parseText(text)
                action(data)
            else:
                action([])
                
            getFileName = lambda f: f.name
            selected_file_text.value = ", ".join(map(getFileName, e.files)) if e.files else "Файл не выбран..."
            selected_file_text.update()

        pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
        selected_file_text = ft.Text("Файл не выбран...")
        page.overlay.append(pick_files_dialog)
        
        pick_btn = ft.ElevatedButton(
                        "Выбрать файл",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: pick_files_dialog.pick_files(
                            allow_multiple=False
                        ),
                    )

        self.controls = [selected_file_text, pick_btn]
        
from threading import Thread, Event
from time import sleep    
        
class StartStopWidget(ft.Column):
    def __init__(self):
        super().__init__(horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                                          alignment=ft.MainAxisAlignment.CENTER, 
                                          expand=1,)
        
        self.event = Event()
        self.isWait = False
        self.isStop_t = False
        self.isWorking = True
        
        self.all_words = []
        self.interval = 0.1
        
        self.output_text = ft.Text("Текст...", expand=1)
        self.start_stop_btn = StartStopButton("Старт", "Стоп", self.start_change_words, self.pause_change_words, self.stop_change_words)
        self.change_words_t = None
        
        def on_change_slider(e):
            self.interval = e.control.value / 1000
            self.interval_text.value = f'{self.interval}с'
            self.interval_text.update()
            
        self.interval_s = ft.Slider(label="Интервал {value}мс", scale=0.7, min=100, max=1100, divisions=10, on_change=on_change_slider)
        self.interval_text = ft.Text(f'{self.interval}с')
        self.controls = [self.output_text, self.start_stop_btn, self.interval_s, self.interval_text]
    
    def setWords(self, all_words):
        self.all_words.clear()
        self.all_words.extend(all_words)
        if self.all_words:
            self.start_stop_btn.setEnable(True)
        else:
            self.start_stop_btn.setEnable(False)
            
    def start_change_words(self):
        if self.change_words_t != None:
            self.isWait = False
            self.event.set()
            self.event.clear()
        else:
            self.change_words_t = Thread(target=self.change_words)
            self.change_words_t.start()
        
    def pause_change_words(self):
        self.isWait = True
        
    def stop_change_words(self):
        self.isStop_t = True
        self.change_words_t.join()
        self.isStop_t = False
        
    def change_words(self):
        index = 0
        while index != len(self.all_words) and not self.isStop_t:
            if self.isWait:
                self.event.wait()
            self.output_text.value = self.all_words[index]
            self.output_text.update()
            index += 1
            sleep(self.interval)
        else:
            self.output_text.value = "Текст..."
            self.output_text.update()
            self.start_stop_btn.change(False)
            self.change_words_t = None
            self.page.update()
            return
        
def main(page: ft.Page):
    
    #Настройки окна
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme=ft.ColorScheme(primary='red', on_primary='white'))
    page.window_maximizable = False
    page.window_minimizable = False
    page.window_width = 600
    page.window_height = 500
    page.window_resizable = False
    page.window_center()
    
    startStopWidget = StartStopWidget()
    openFileWidget = OpenFileWidget(page, startStopWidget.setWords)
    body = ft.Container(
                        content=ft.Column(
                            controls=[startStopWidget, ft.Divider(), openFileWidget], 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                            alignment=ft.MainAxisAlignment.CENTER, 
                            expand=1,
                            ), 
                        expand=1, 
                        alignment=ft.alignment.center,
                        )
    
    page.add(body)

if __name__ == '__main__':
    ft.app(main, assets_dir='assets')
