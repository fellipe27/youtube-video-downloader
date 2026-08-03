from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QRadioButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal
from pytubefix import YouTube
from pytubefix.cli import on_progress
import sys

class DownloadThread(QThread):
    download_completed = pyqtSignal(str)
    download_failed = pyqtSignal(str)

    def __init__(self, url, path, is_only_audio):
        super().__init__()
        self.url = url
        self.path = path
        self.is_only_audio = is_only_audio

    def run(self):
        try:
            yt = YouTube(self.url, on_progress_callback=on_progress)
            ys = yt.streams.get_audio_only() if self.is_only_audio else yt.streams.get_highest_resolution()
            ys.download(output_path=self.path)

            self.download_completed.emit(yt.title)
        except Exception as e:
            self.download_failed.emit(str(e))

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('YouTube video downloader')
        self.setFixedSize(600, 200)
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
        self.path_input.setReadOnly(True)
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

        self.status_label = QLabel('Download your favorite YouTube video ❤️')
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

        self.setStyleSheet('''
        QWidget {
            background-color: #2b2b2b;
            color: white;
            font-size: 10pt;
        }
        QLineEdit {
            background-color: #3c3f41;
            color: white;
            border: 1px solid #5a5a5a;
            border-radius: 6px;
            padding: 2px;
        }
        QPushButton {
            background-color: #2196F3;
            border: none;
            border-radius: 6px;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: #42A5F5;
        }
        QPushButton:disabled {
            background-color: #666666;
        }
        ''')

    def reset_ui(self):
        self.url_input.clear()
        self.status_label.setText('Download your favorite YouTube video ❤️')
        self.download_btn.setEnabled(True)

    def on_download_failed(self, error_msg):
        QMessageBox.critical(self, 'Error', f'An error occurred: {error_msg}')
        self.reset_ui()

    def on_download_success(self, title):
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

        self.thread.download_completed.connect(self.on_download_success)
        self.thread.download_failed.connect(self.on_download_failed)
        self.thread.start()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(caption='Select Folder')

        if folder:
            self.path_input.setText(folder)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = YouTubeDownloader()
    window.show()

    sys.exit(app.exec_())
