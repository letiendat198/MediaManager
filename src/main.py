import os
import sys
import json
import urllib3

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Popups import *
from FileHelper import *
from ThreadWorker import *
from MetadataHelper import *
from DataManager import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(6)
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.MenuBar = MenuBar()
        self.MenuBar.connect_actions(self.update_tracks, self.threadpool)
        self.setMenuBar(self.MenuBar)

        self.setWindowTitle("Music Manager")
        self.resize(1200, 800)

        main_layout = QHBoxLayout()

        self.side_media_list = SideMediaList()
        self.info_editing_panel = InfoEditingPanel()

        main_layout.addWidget(self.side_media_list, 45)
        main_layout.addWidget(self.info_editing_panel, 65)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        self.info_editing_panel.save_for_later(self.update_tracks, self.threadpool)

        self.update_tracks()

    def update_tracks(self):
        self.side_media_list.populate()
        for button in self.side_media_list.media_button_list:
            button.connect(self.info_editing_panel.populate)


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

        f = FileHelper("data.json")
        if f.exists():
            self.default_label.hide()
            tracks = json.loads(f.read())
            pre = ""
            for track in tracks:
                playlist = track.split(":")[0]
                if playlist != pre:
                    self.view.addWidget(QLabel(playlist))
                    self.view.addWidget(HLine())
                    pre = playlist
                media_button = MediaTitleButton(tracks[track]["name"], track)
                if "download-path" in tracks[track]:
                    media_button.set_downloaded()
                self.media_button_list.append(media_button)
                self.view.addWidget(self.media_button_list[len(self.media_button_list) - 1])
                self.media_button_group.addButton(self.media_button_list[len(self.media_button_list) - 1])


class InfoEditingPanel(QScrollArea):
    def __init__(self):
        super().__init__()

        self.setWidgetResizable(True)

        self.view = QFormLayout()

        self.default_off = False
        self.default_label = QLabel("No info to show")
        self.view.addWidget(self.default_label)

        self.widget = QWidget()
        self.widget.setLayout(self.view)
        self.setWidget(self.widget)

        self.path_chooser = GenericPathChooser("Choose a folder to save", "Save path")
        self.search_popup = GetYtUrlPopup()

    def switch_off_default(self):
        self.default_off = True

        self.default_label.hide()

        self.image_row = QHBoxLayout()
        self.image = ImageLabel()
        self.image.set_image_from_file("resources/placeholder.jpg")
        self.image.signal.clicked.connect(self.on_image_click)

        self.info_side = QFormLayout()
        self.name_edit = QLineEdit()
        self.info_side.addRow("Track name", self.name_edit)
        self.artist_edit = QLineEdit()
        self.info_side.addRow("Artist", self.artist_edit)
        self.album_edit = QLineEdit()
        self.info_side.addRow("Album", self.album_edit)
        self.image_row.addWidget(self.image)
        self.image_row.addLayout(self.info_side)

        self.view.addRow(self.image_row)

        self.view.addRow(HLine())

        self.yt_link_row = QHBoxLayout()
        self.yt_link_edit = QLineEdit()
        self.yt_search_but = QPushButton("Search")
        self.yt_link_row.addWidget(self.yt_link_edit)
        self.yt_link_row.addWidget(self.yt_search_but)
        self.view.addRow("Youtube Link", self.yt_link_row)

        self.title_row = QHBoxLayout()
        self.yt_title = QLabel()
        self.yt_title_refresh = QPushButton("Refresh")
        self.title_row.addWidget(self.yt_title)
        self.title_row.addWidget(self.yt_title_refresh)
        self.view.addRow("Youtube Video Title", self.title_row)

        self.button_row = QHBoxLayout()
        self.save_but = QPushButton("Save")
        self.button_row.addWidget(self.save_but)
        self.download_but = QPushButton("Download")
        self.button_row.addWidget(self.download_but)
        self.delete_but = QPushButton("Delete")
        self.button_row.addWidget(self.delete_but)

        self.save_but.clicked.connect(self.on_save_click)

        self.view.addRow(self.button_row)

        self.delete_but.clicked.connect(lambda: self.on_delete_click(self.callback))
        self.download_but.clicked.connect(lambda: self.on_download_click(self.callback, self.threadpool))
        self.yt_search_but.clicked.connect(lambda: self.on_search_click(self.populate, self.threadpool))
        self.yt_title_refresh.clicked.connect(lambda: self.on_refresh_click(self.populate, self.threadpool))

    def save_for_later(self, callback, threadpool):
        self.callback = callback
        self.threadpool = threadpool

    def populate(self, id):
        print(id)
        self.id = id
        if not self.default_off:
            self.switch_off_default()

        f = FileHelper("data.json")
        tracks = json.loads(f.read())
        self.name_edit.setText(tracks[id]["name"])
        self.artist_edit.setText(tracks[id]["artist"])
        self.album_edit.setText(tracks[id]["album"])
        if "yt-url" in tracks[id]:
            self.yt_link_edit.setText(tracks[id]["yt-url"])
            self.yt_link_edit.setCursorPosition(0)
            self.yt_title.setText(tracks[id]["yt-title"])
        else:
            self.yt_link_edit.setText("")
            self.yt_title.setText("")
        if "download-path" in tracks[id]:
            img_data = MetadataHelper(tracks[id]["download-path"]).get_album_image()
            if img_data is not None:
                print("Loading image from local file")
                self.image.set_image_from_data(img_data)
            else:
                print("No image data found. Using placeholder")
                self.image.set_image_from_file("resources/placeholder.jpg")
        elif "album-image-url" in tracks[id] and tracks[id]["album-image-url"] != "":
            url = tracks[id]["album-image-url"]
            print("Fetching image via url", url)
            http = urllib3.PoolManager()
            resp = http.request("GET", url)
            self.image.set_image_from_data(resp.data)
        else:
            print("No image data found. Using placeholder")
            self.image.set_image_from_file("resources/placeholder.jpg")

    def on_image_click(self):
        self.image_chooser = ImageChooserPopup(self.populate, self.id)

    def on_save_click(self):
        f = FileHelper("data.json")
        tracks = json.loads(f.read())
        tracks[self.id]["name"] = self.name_edit.text()
        tracks[self.id]["artist"] = self.artist_edit.text()
        tracks[self.id]["album"] = self.album_edit.text()
        tracks[self.id]["yt-url"] = self.yt_link_edit.text()
        tracks[self.id]["yt-title"] = self.yt_title.text()
        js = json.dumps(tracks)
        f.overwrite(js)

        if "download-path" in tracks[self.id]:
            path = tracks[self.id]["download-path"]
            metadata = MetadataHelper(path)
            metadata.write(tracks[self.id])
            # if "album-image-url" in tracks[self.id]:
            #     if tracks[self.id]["album-image-url"] != "":
            #         metadata.add_image_from_url(tracks[self.id]["album-image-url"])

    def on_delete_click(self, update_callback):
        f = FileHelper("data.json")
        tracks = json.loads(f.read())
        if "download-path" in tracks[self.id]:
            path = tracks[self.id]["download-path"]
            tf = FileHelper(path)
            if tf.exists():
                print("Downloaded file found, removing", path)
                tf.delete()
        print("Deleting", tracks[self.id]["name"])
        tracks.pop(self.id)
        js = json.dumps(tracks)
        f.overwrite(js)
        update_callback()

    def on_download_click(self, fn, threadpool):
        self.path_chooser.update_params(DownloadYtPopup,self.yt_link_edit.text(), self.name_edit.text(), self.id,
                                        callback=fn, threadpool=threadpool)
        self.path_chooser.show()

    def on_search_click(self, fn, threadpool):
        self.search_popup.update_params(self.id, self.name_edit.text(), fn, threadpool)
        self.search_popup.show()

    def on_refresh_click(self, callback, threadpool):
        self.yt_title.setText("")
        self.refresh_popup = YtTitleRefreshPopup(self.id, self.yt_link_edit.text(), callback, threadpool)


class MenuBar(QMenuBar):
    def __init__(self):
        super().__init__()

        fileMenu = QMenu("File", self)
        importMenu = fileMenu.addMenu("Import")
        self.action_import_json = QAction("Import from JSON...", importMenu)
        importMenu.addAction(self.action_import_json)
        self.action_import_spotify = QAction("Import from Spotify...", importMenu)
        importMenu.addAction(self.action_import_spotify)

        addMenu = fileMenu.addMenu("Add")
        self.action_add_sp_playlist = QAction("Add a Spotify playlist...", addMenu)
        addMenu.addAction(self.action_add_sp_playlist)
        self.action_add_yt = QAction("Add a Youtube video...", addMenu)
        addMenu.addAction(self.action_add_yt)
        self.action_add_yt_playlist = QAction("Add a Youtube playlist...", addMenu)
        addMenu.addAction(self.action_add_yt_playlist)
        self.addMenu(fileMenu)

        editMenu = QMenu("Action", self)
        self.action_refresh = QAction("Refresh", editMenu)
        editMenu.addAction(self.action_refresh)
        self.action_batch_get_yt_link = QAction("Batch: Get Youtube Urls", editMenu)
        editMenu.addAction(self.action_batch_get_yt_link)
        self.action_batch_download_yt = QAction("Batch: Download from Youtube", editMenu)
        editMenu.addAction(self.action_batch_download_yt)
        self.action_batch_write_metadata = QAction("Batch: Write metadata to downloaded files", editMenu)
        editMenu.addAction(self.action_batch_write_metadata)
        self.addMenu(editMenu)

    def connect_actions(self, fn, threadpool):
        # self.action_import_json.triggered.connect()
        self.action_import_spotify.triggered.connect(lambda: self.open_import_spotify_popup(fn, threadpool))
        self.action_add_sp_playlist.triggered.connect(lambda: self.open_add_sp_playlist(fn, threadpool))
        self.action_add_yt.triggered.connect(lambda: self.open_add_yt(fn, threadpool))
        self.action_batch_get_yt_link.triggered.connect(lambda: self.open_batch_get_yt_url_popup(threadpool))
        self.action_batch_download_yt.triggered.connect(lambda: self.open_batch_download_yt_popup(threadpool))
        self.action_batch_write_metadata.triggered.connect(lambda: self.open_batch_write_metadata_popup(threadpool))
        self.action_refresh.triggered.connect(lambda: self.on_refresh(fn))

    def on_refresh(self, fn):
        DataManager().validate_download()
        fn()

    def open_import_spotify_popup(self, fn, threadpool):
        self.import_spotify_popup = ImportSpotifyPopup(fn, threadpool)
        self.import_spotify_popup.show()

    def open_add_sp_playlist(self, fn, threadpool):
        self.add_sp_playlist_popup = AddSpotifyPlaylistPopup(fn, threadpool)
        self.add_sp_playlist_popup.show()

    def open_add_yt(self, fn, threadpool):
        self.add_yt_popup = AddYtVideoPopup(fn, threadpool)
        self.add_yt_popup.show()

    def open_batch_get_yt_url_popup(self, threadpool):
        self.batch_get_yt_url_popup = BatchGetYtUrlPopup(threadpool)
        self.batch_get_yt_url_popup.show()

    def open_batch_download_yt_popup(self, threadpool):
        self.batch_download_yt = GenericPathChooser("Choose a folder to save", "Save path")
        self.batch_download_yt.update_params(BatchDownloadYtPopup, threadpool=threadpool)
        self.batch_download_yt.show()

    def open_batch_write_metadata_popup(self, threadpool):
        self.batch_write_metadata = BatchWriteMetadataPopup(threadpool)
        self.batch_write_metadata.show()


class MediaTitleButton(QPushButton):
    def __init__(self, label, id):
        super(MediaTitleButton, self).__init__()

        self.id = id
        self.setText(label)
        self.setStyleSheet("QPushButton { text-align: left; border: 0px; font-size: 15px; padding: 5px} "
                           "QPushButton:checked { text-align: left; border: 0px; font-size: 15px; padding: 5px; "
                           "background-color:lightblue}")
        self.setCheckable(True)

    def set_downloaded(self):
        self.setStyleSheet(
            "QPushButton { text-align: left; border: 0px; font-size: 15px; padding: 5px; background-color:lightgreen} "
            "QPushButton:checked { text-align: left; border: 0px; font-size: 15px; padding: 5px; "
            "background-color:limegreen}")

    def set_normal(self):
        self.setStyleSheet("QPushButton { text-align: left; border: 0px; font-size: 15px; padding: 5px} "
                           "QPushButton:checked { text-align: left; border: 0px; font-size: 15px; padding: 5px; "
                           "background-color:lightblue}")

    def connect(self, fn):
        self.clicked.connect(lambda: fn(self.id))


class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class PlaylistSeperator(QHBoxLayout):
    def __init__(self, name):
        super(PlaylistSeperator, self).__init__()

        self.line = HLine()

        self.label = QLabel(name)
        self.font = QFont()
        self.font.setPointSize(10)
        self.label.setFont(self.font)
        self.label.setContentsMargins(0, 0, 5, 5)
        self.label.setWordWrap(True)
        self.label.setFrameShape(QFrame.NoFrame)
        self.label.setLineWidth(0)

        self.addWidget(self.label)
        self.addWidget(self.line)


class ImageLabel(QLabel):
    def __init__(self):
        super(ImageLabel, self).__init__()
        self.pixmap = QPixmap()
        self.signal = Signal()

    def mousePressEvent(self, ev, QMouseEvent=None):
        self.signal.clicked.emit()

    def set_image_from_data(self, img):
        self.pixmap.loadFromData(img)
        self.pixmap = self.pixmap.scaled(128, 128, Qt.KeepAspectRatio)
        self.setPixmap(self.pixmap)

    def set_image_from_file(self, path):
        self.pixmap.load(path)
        self.pixmap = self.pixmap.scaled(128, 128, Qt.KeepAspectRatio)
        self.setPixmap(self.pixmap)


class Signal(QObject):
    clicked = pyqtSignal()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    app.exec()
