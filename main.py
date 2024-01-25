import PySimpleGUI as sg
from pytube import YouTube
import requests
from pytube.exceptions import RegexMatchError
import threading

class Window:
    def __init__(self):
        sg.theme('Black')
        self.layout = [
            [sg.Text('Youtube Video Downloader!')],
            [sg.Text('Youtube Video URL:'), sg.InputText(key='url')],
            [sg.Text('Download path:'), sg.InputText(key='path'), sg.FolderBrowse()],
            [sg.Text('Format:'), sg.Radio(text='Video', group_id='format', key='format_0', default=True), sg.Radio(text='Only audio', group_id='format', key='format_1')],
            [sg.Text('Download your favorite Youtube video <3', key='status')],
            [sg.Button('Download'), sg.Button('Exit')]
        ]
        self.title = 'Youtube Video Downloader'
        self.window = sg.Window(self.title, self.layout)
        self.download_complete = False
        self.have_error = False
        self.video_title = ''

    def download(self, url, path, only_audio):
        try:
            requests.get('https://github.com/fellipe27')
        except requests.ConnectionError:
            self.have_error = True
        else:
            try:
                yt = YouTube(url)
                resolution = yt.streams.get_highest_resolution()

                yt.streams.filter(only_audio=only_audio, resolution=resolution).first().download(path)
                self.video_title = yt.title
            except RegexMatchError:
                self.have_error = True
            else:
                self.have_error = False
            finally:
                self.download_complete = True

    def download_thread(self, url, path, only_audio):
        threading.Thread(target=self.download, args=(url, path, only_audio), daemon=True).start()

    def run(self):
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            elif event == 'Download':
                url_value = values['url']
                path_value = values['path']
                only_audio = False if values['format_0'] else True

                if url_value and path_value:
                    self.window['status'].update('Download in progress...')
                    self.window['Download'].update(disabled=True)

                    self.download_thread(url_value, path_value, only_audio)

                    while not self.download_complete:
                        event, _ = self.window.read(timeout=100)
                        if event == sg.WIN_CLOSED or event == 'Exit':
                            break

                    if self.download_complete:
                        if self.have_error:
                            sg.popup('Something is wrong! :(', title='No connection!')
                        else:
                            sg.popup(f'{self.video_title} has been downloaded', title='Download successful!')
                            self.window['url'].update('')
                            self.window['path'].update('')
                            self.window['format_0'].update(value=True)
                            self.window['Download'].update(disabled=False)

                        self.window['status'].update('Download your favorite Youtube video <3')
                        self.download_complete = False

        self.window.close()

if __name__ == '__main__':
    window = Window()
    window.run()
