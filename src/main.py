import sys
import json

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Popups import *
from FileHelper import *
from ThreadWorker import Worker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.MenuBar = MenuBar()
        self.MenuBar.connect_actions(self.update_tracks, self.threadpool)
        self.setMenuBar(self.MenuBar)

        self.setWindowTitle("Media Manager")
        self.resize(1200, 800)

        main_layout = QHBoxLayout()

        self.side_media_list = SideMediaList()
        self.info_editing_panel = InfoEditingPanel()

        main_layout.addWidget(self.side_media_list, 45)
        main_layout.addWidget(self.info_editing_panel, 65)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        self.update_tracks()

    def update_tracks(self):
        self.side_media_list.populate()
        for button in self.side_media_list.media_button_list:
            button.connect(self.connect_stuffs)

    def connect_stuffs(self, name):
        self.info_editing_panel.populate(name)
        self.info_editing_panel.delete_connect(self.update_tracks)
        self.info_editing_panel.download_connect(self.threadpool)
        self.info_editing_panel.search_connect(self.threadpool)


class SideMediaList(QScrollArea):
    def __init__(self):
        super().__init__()

        self.widget = None
        self.media_button_list = None
        self.media_button_group = None
        self.default_label = None
        self.view = None
        self.populate()

    def populate(self):
        self.setWidgetResizable(True)
        # self.setFixedWidth(200)

        self.view = QVBoxLayout()

        self.default_label = QLabel("Nothing yet!")
        self.view.addWidget(self.default_label)

        self.media_button_group = QButtonGroup(self)
        self.media_button_list = []

        self.widget = QWidget()
        self.widget.setLayout(self.view)
        self.setWidget(self.widget)

        f = FileHelper("liked.json")
        if f.exists():
            self.default_label.hide()
            tracks = json.loads(f.read())
            for track in tracks:
                self.media_button_list.append(MediaTitleButton(track))
                self.view.addWidget(self.media_button_list[len(self.media_button_list)-1])
                self.media_button_group.addButton(self.media_button_list[len(self.media_button_list)-1])


class InfoEditingPanel(QScrollArea):
    def __init__(self):
        super().__init__()

        self.setWidgetResizable(True)

        self.view = QFormLayout()
        self.name = None

        self.default_off = False
        self.default_label = QLabel("No info to show")
        self.view.addWidget(self.default_label)

        self.widget = QWidget()
        self.widget.setLayout(self.view)
        self.setWidget(self.widget)

    def switch_off_default(self):
        self.default_off = True

        self.default_label.hide()

        self.name_edit = QLineEdit()
        self.view.addRow("Track name", self.name_edit)

        self.artist_edit = QLineEdit()
        self.view.addRow("Artist", self.artist_edit)

        self.album_edit = QLineEdit()
        self.view.addRow("Album", self.album_edit)

        self.view.addRow(HLine())

        self.yt_link_row = QHBoxLayout()
        self.yt_link_edit = QLineEdit()
        self.yt_search_but = QPushButton("Search")
        self.yt_link_row.addWidget(self.yt_link_edit)
        self.yt_link_row.addWidget(self.yt_search_but)
        self.view.addRow("Youtube Link", self.yt_link_row)

        self.yt_title = QLabel()
        self.view.addRow("Youtube Video Title", self.yt_title)

        self.button_row = QHBoxLayout()
        self.save_but = QPushButton("Save")
        self.button_row.addWidget(self.save_but)
        self.download_but = QPushButton("Download")
        self.button_row.addWidget(self.download_but)
        self.delete_but = QPushButton("Delete")
        self.button_row.addWidget(self.delete_but)

        self.save_but.clicked.connect(self.on_save_click)

        self.view.addRow(self.button_row)

    def populate(self, name):
        print(name)
        self.name = name
        if not self.default_off:
            self.switch_off_default()

        f = FileHelper("liked.json")
        tracks = json.loads(f.read())
        for track in tracks:
            if track == name:
                self.name_edit.setText(track)
                self.artist_edit.setText(tracks[name]["artist"])
                if "yt-url" in tracks[name]:
                    self.yt_link_edit.setText(tracks[name]["yt-url"])
                    self.yt_link_edit.setCursorPosition(0)
                    self.yt_title.setText(tracks[name]["yt-title"])
                else:
                    self.yt_link_edit.setText("")
                    self.yt_title.setText("")

    def delete_connect(self, fn):
        self.delete_but.clicked.connect(lambda: self.on_delete_click(fn))

    def download_connect(self, threadpool):
        self.download_but.clicked.connect(lambda: self.on_download_click(threadpool))

    def search_connect(self, threadpool):
        self.yt_search_but.clicked.connect(lambda: self.on_search_click(self.populate, threadpool))

    def on_save_click(self):
        f = FileHelper("liked.json")
        tracks = json.loads(f.read())
        for track in tracks:
            if track == self.name:
                obj = {
                    self.name: {
                        "artist": self.artist_edit.text(),
                        "id": tracks[self.name]["id"],
                        "yt-url": self.yt_link_edit.text(),
                        "yt-title": self.yt_title.text()
                    }
                }
                tracks.update(obj)
        js = json.dumps(tracks)
        f.overwrite(js)

    def on_delete_click(self, update_callback):
        f = FileHelper("liked.json")
        tracks = json.loads(f.read())
        for track in tracks:
            if track == self.name:
                tracks.pop(self.name)
                break
        js = json.dumps(tracks)
        f.overwrite(js)
        update_callback()

    def on_download_click(self, threadpool):
        self.download_popup = DownloadYtPopup(self.yt_link_edit.text(), self.name, threadpool)
        self.download_popup.show()

    def on_search_click(self, fn, threadpool):
        self.search_popup = GetYtUrlPopup(self.name, fn, threadpool)
        self.search_popup.show()


class MenuBar(QMenuBar):
    def __init__(self):
        super().__init__()

        fileMenu = QMenu("File", self)
        importMenu = fileMenu.addMenu("Import")
        self.action_import_json = QAction("Import from JSON...", importMenu)
        importMenu.addAction(self.action_import_json)
        self.action_import_spotify = QAction("Import from Spotify...", importMenu)
        importMenu.addAction(self.action_import_spotify)
        self.addMenu(fileMenu)

        editMenu = QMenu("Edit", self)
        self.action_get_yt_link = QAction("Batch: Get Youtube Urls", editMenu)
        editMenu.addAction(self.action_get_yt_link)
        self.addMenu(editMenu)

    def connect_actions(self, fn, threadpool):
        # self.action_import_json.triggered.connect()
        self.action_import_spotify.triggered.connect(lambda: self.open_import_spotify_popup(fn, threadpool))
        self.action_get_yt_link.triggered.connect(lambda : self.open_get_yt_url_popup(threadpool))

    def open_import_spotify_popup(self, fn, threadpool):
        self.import_spotify_popup = ImportSpotifyPopup(fn, threadpool)
        self.import_spotify_popup.show()

    def open_get_yt_url_popup(self, threadpool):
        self.get_yt_url_popup = BatchGetYtUrlPopup(threadpool)
        self.get_yt_url_popup.show()


class MediaTitleButton(QPushButton):
    def __init__(self, label):
        super(MediaTitleButton, self).__init__()

        self.name = label
        self.setFlat(True)
        self.setText(label)
        self.setStyleSheet("QPushButton { text-align: left; }")
        self.setCheckable(True)

    def connect(self, fn):
        self.clicked.connect(lambda: fn(self.name))


class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    app.exec()