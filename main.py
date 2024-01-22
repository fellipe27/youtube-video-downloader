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
        self.downloadComplete = False
        self.haveError = False
        self.videoTitle = ''

    def download(self, url, path, onlyAudio):
        try:
            requests.get('https://github.com/fellipe27')
        except requests.ConnectionError:
            self.haveError = True
        else:
            try:
                yt = YouTube(url)
                resolution = yt.streams.get_highest_resolution()

                yt.streams.filter(only_audio=onlyAudio, resolution=resolution).first().download(path)
                self.videoTitle = yt.title
            except RegexMatchError:
                self.haveError = True
            else:
                self.haveError = False
            finally:
                self.downloadComplete = True

    def downloadThread(self, url, path, onlyAudio):
        threading.Thread(target=self.download, args=(url, path, onlyAudio), daemon=True).start()

    def run(self):
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            elif event == 'Download':
                urlValue = values['url']
                pathValue = values['path']
                onlyAudio = False if values['format_0'] else True

                if urlValue and pathValue:
                    self.window['status'].update('Download in progress...')
                    self.window['Download'].update(disabled=True)

                    self.downloadThread(urlValue, pathValue, onlyAudio)

                    while not self.downloadComplete:
                        event, _ = self.window.read(timeout=100)
                        if event == sg.WIN_CLOSED or event == 'Exit':
                            break

                    if self.downloadComplete:
                        if self.haveError:
                            sg.popup('Something is wrong! :(', title='No connection!')
                        else:
                            sg.popup(f'{self.videoTitle} has been downloaded', title='Download successful!')
                            self.window['url'].update('')
                            self.window['path'].update('')
                            self.window['format_0'].update(value=True)
                            self.window['Download'].update(disabled=False)

                        self.window['status'].update('Download your favorite Youtube video <3')
                        self.downloadComplete = False

        self.window.close()

if __name__ == '__main__':
    window = Window()
    window.run()
