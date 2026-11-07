from pathlib import Path

from PyQt6 import QtCore, QtWebChannel, QtWebEngineWidgets


class BlocklyBridge(QtCore.QObject):
    codeChanged = QtCore.pyqtSignal(str)
    ready = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot(str)
    def update_code(self, code: str) -> None:
        self.codeChanged.emit(code)

    @QtCore.pyqtSlot()
    def request_code(self) -> None:
        self.ready.emit("")


class BlocklyEditor(QtWebEngineWidgets.QWebEngineView):
    codeChanged = QtCore.pyqtSignal(str)

    def __init__(self, source: str = "", dark_mode: bool = False, parent=None) -> None:
        super().__init__(parent)
        self._bridge = BlocklyBridge()
        self._bridge.codeChanged.connect(self.codeChanged)
        self._bridge.codeChanged.connect(self._set_current_source)
        self.page().setWebChannel(self._channel())
        self.loadFinished.connect(self._on_load_finished)
        self.setMinimumWidth(520)
        self._dark_mode = dark_mode

        page = Path(__file__).with_name("blockly").joinpath("index.html")
        self._source = source
        self.load(QtCore.QUrl.fromLocalFile(str(page)))

    def _channel(self) -> QtWebChannel.QWebChannel:
        channel = QtWebChannel.QWebChannel(self.page())
        channel.registerObject("bridge", self._bridge)
        return channel

    def code(self) -> str:
        return self._source

    def _set_current_source(self, source: str) -> None:
        self._source = source

    def _on_load_finished(self, ok: bool) -> None:
        if ok:
            self.set_dark_mode(self._dark_mode)
            self._bridge.ready.emit(self._source)

    def reload_source(self, source: str) -> None:
        self._source = source
        self._bridge.ready.emit(source)

    def highlight_line(self, line_number: int) -> None:
        self.page().runJavaScript(f"highlightLine({int(line_number)})")

    def clear_highlight(self) -> None:
        self.page().runJavaScript("clearHighlight()")

    def set_dark_mode(self, dark_mode: bool) -> None:
        self._dark_mode = dark_mode
        self.page().runJavaScript(f"setDarkMode({str(dark_mode).lower()})")
