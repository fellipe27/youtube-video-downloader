from pytubefix import YouTube
from pytubefix.cli import on_progress
from threading import Thread
import PySimpleGUI as sg

def download(url, path, is_only_audio):
    global have_error, is_download_complete, video_title
    have_error = False

    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        video_title = yt.title

        if is_only_audio:
            yt.streams.get_audio_only().download(output_path=path)
        else:
            yt.streams.get_highest_resolution().download(output_path=path)
    except Exception as e:
        have_error = True
        print(e)
    finally:
        is_download_complete = True

def download_thread(url, path, is_only_audio):
    Thread(target=download, args=(url, path, is_only_audio), daemon=True).start()

have_error = False
is_download_complete = False
video_title = ''

sg.theme('Black')

title = 'Youtube video downloader'
layout = [
    [sg.Text('Youtube video downloader')],
    [sg.Text('Video URL:'), sg.InputText(key='url')],
    [sg.Text('Path:'), sg.InputText(key='path'), sg.FolderBrowse()],
    [
        sg.Text('Format:'),
        sg.Radio(text='video', group_id='format', key='format_0', default=True),
        sg.Radio(text='audio', group_id='format', key='format_1')
    ],
    [sg.Text('Download your favorite Youtube video <3', key='status')],
    [sg.Button('Download'), sg.Button('Exit')]
]

window = sg.Window(title, layout)

while True:
    event, values = window.read(timeout=100)

    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == 'Download':
        url_value = values['url']
        path_value = values['path']
        is_only_audio_value = False if values['format_0'] else True

        if url_value and path_value:
            window['status'].update('Download in progress...')
            window['Download'].update(disabled=True)

            download_thread(url_value, path_value, is_only_audio_value)

    if is_download_complete:
        if have_error:
            sg.popup('Something is wrong :(', title='An error has occurred')
        else:
            sg.popup(f'{video_title} has been downloaded', title='Download successful')

        window['url'].update('')
        window['path'].update('')
        window['format_0'].update(value=True)
        window['Download'].update(disabled=False)
        window['status'].update('Download your favorite Youtube video <3')

        is_download_complete = False

window.close()
