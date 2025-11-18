from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QRadioButton,
    QFileDialog, QVBoxLayout,QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal
from yt_dlp import YoutubeDL
import sys

class DownloadThread(QThread):
    download_complete = pyqtSignal(str)
    download_error = pyqtSignal(str)

    def __init__(self, url, path, is_only_audio):
        super().__init__()
        self.url = url
        self.path = path
        self.is_only_audio = is_only_audio

    def run(self):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{self.path}/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3'
                }],
                'ffmpeg_location': 'ffmpeg'
            } if self.is_only_audio else {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f'{self.path}/%(title)s.%(ext)s',
                'merge_output_format': 'mp4',
                'ffmpeg_location': 'ffmpeg'
            }

            with YoutubeDL(ydl_opts) as ydl:
                target = ydl.extract_info(self.url, download=True)
                target_title = target.get('title')

            self.download_complete.emit(target_title)
        except Exception as e:
            self.download_error.emit(str(e))

class YoutubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Youtube Video Downloader')
        self.setFixedSize(600, 250)
        self.thread = None
        self.layout = QVBoxLayout()

        self.url_layout = QHBoxLayout()
        self.url_layout.addWidget(QLabel('Video URL:'))
        self.url_input = QLineEdit()
        self.url_layout.addWidget(self.url_input)
        self.layout.addLayout(self.url_layout)

        self.path_layout = QHBoxLayout()
        self.path_layout.addWidget(QLabel('Path:'))
        self.path_input = QLineEdit()
        self.browse_btn = QPushButton('Browse')
        self.browse_btn.clicked.connect(self.browse_folder)
        self.path_layout.addWidget(self.path_input)
        self.path_layout.addWidget(self.browse_btn)
        self.layout.addLayout(self.path_layout)

        self.format_layout = QHBoxLayout()
        self.format_layout.addWidget(QLabel('Format:'))
        self.video_radio = QRadioButton('Video')
        self.video_radio.setChecked(True)
        self.audio_radio = QRadioButton('Only audio')
        self.format_layout.addWidget(self.video_radio)
        self.format_layout.addWidget(self.audio_radio)
        self.layout.addLayout(self.format_layout)

        self.status_label = QLabel('Download your favorite YouTube video <3')
        self.layout.addWidget(self.status_label)

        self.btn_layout = QHBoxLayout()
        self.download_btn = QPushButton('Download')
        self.download_btn.clicked.connect(self.start_download)
        self.close_btn = QPushButton('Close')
        self.close_btn.clicked.connect(self.close)
        self.btn_layout.addWidget(self.download_btn)
        self.btn_layout.addWidget(self.close_btn)
        self.layout.addLayout(self.btn_layout)

        self.setLayout(self.layout)

    def reset_ui(self):
        self.url_input.clear()
        self.status_label.setText('Download your favorite YouTube video <3')
        self.download_btn.setEnabled(True)

    def on_download_error(self, error_msg):
        QMessageBox.critical(self, 'Error', f'An error occurred: {error_msg}')
        self.reset_ui()

    def on_download_complete(self, title):
        QMessageBox.information(self, 'Success', f'{title} has been downloaded')
        self.reset_ui()

    def start_download(self):
        url = self.url_input.text().strip()
        path = self.path_input.text().strip()
        is_only_audio = self.audio_radio.isChecked()

        if not url or not path:
            QMessageBox.warning(self, 'Warning', 'Please enter URL and path')

            return

        self.status_label.setText('Downloading...')
        self.download_btn.setEnabled(False)

        self.thread = DownloadThread(url, path, is_only_audio)

        self.thread.download_complete.connect(self.on_download_complete)
        self.thread.download_error.connect(self.on_download_error)
        self.thread.start()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')

        if folder:
            self.path_input.setText(folder)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = YoutubeDownloader()
    window.show()

    sys.exit(app.exec_())
