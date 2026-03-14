import sys
import os
import webbrowser

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSystemTrayIcon,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QInputDialog,
    QMessageBox,
    QMenu
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtGui import (
    QIcon,
    QMouseEvent,
    QAction
    )
from PyQt6.QtCore import (
    QUrl,
    Qt,
    pyqtSignal,
    QObject,
    QEvent
    )
import win32con
import win32gui


# 获取资源文件路径
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

check_url= 'https://designer.hyperate.io/'
def open_website():
        webbrowser.open(check_url)


class MenuWin(QMainWindow):

    sgn_hpr_cls = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        
        # 初始化主窗口ui
        self.setWindowTitle("心率显示")
        self.setGeometry(100, 100, 220, 200)
        self.setFixedSize(self.size()) # 固定尺寸
        self.setWindowIcon(QIcon(get_resource_path('heart.ico')))
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
            ) # 限制最大化

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.menu = self.init_menu()
        self.loading = self.init_loading()

        self.stacked_widget.addWidget(self.menu)
        self.stacked_widget.addWidget(self.loading)

        self.stacked_widget.setCurrentIndex(0)


    def init_menu(self):
        menu = QWidget()
        layout = QVBoxLayout()

        tip_label = QLabel("请选择样式")
        tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_default = QPushButton("默认样式")
        button_default.clicked.connect(self.get_id)

        button_url = QPushButton("自定义url")
        button_url.clicked.connect(self.get_url)

        button_jump = QPushButton("快进到DIY网站")
        button_jump.clicked.connect(open_website)

        layout.addWidget(tip_label)
        layout.addWidget(button_default)
        layout.addWidget(button_url)
        layout.addWidget(button_jump)

        menu.setLayout(layout)

        return menu


    hprID = ''

    def get_id(self):
        #self.hprID, ok = QInputDialog.getText(self, 'HypeRateID', "请输入你的ID:")
        
        dialog = QInputDialog(self)
        dialog.setWindowTitle('HypeRateID')
        dialog.setLabelText("请输入你的ID :")
        dialog.setFixedSize(300, 100)

        dialog.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint |
            #Qt.WindowType.Window |
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint | # 保留标题栏
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.MSWindowsFixedSizeDialogHint # 固定大小
        )
        ok = dialog.exec()
        self.hprID = dialog.textValue()

        if ok and self.hprID:
            if len(self.hprID) == 5:
                self.is_default = True
                self.switch_to_loading()
            else:
                self.show_invalid_msg()
        elif ok:
            self.show_empty_msg()
            

    custom_url = ''

    def get_url(self):
        #self.custom_url, ok = QInputDialog.getText(self, 'CustomUrl', "请输入自定义url:")

        dialog = QInputDialog(self)
        dialog.setWindowTitle('CustomUrl')
        dialog.setLabelText("请输入自定义url :")
        dialog.setFixedSize(300, 100)

        dialog.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.MSWindowsFixedSizeDialogHint
        )
        ok = dialog.exec()
        self.custom_url = dialog.textValue()

        if ok and self.custom_url:
            if check_url in self.custom_url:
                self.is_default = False
                self.switch_to_loading()
            else:
                self.show_invalid_msg()
        elif ok:
            self.show_empty_msg()

    def show_empty_msg(self):
        #QMessageBox.information(self, "提示", "输入不能为空", QMessageBox.StandardButton.Ok)

        msg = QMessageBox(self)
        msg.setWindowTitle("提示")
        msg.setText("输入不能为空")
        msg.setFixedSize(200, 100)

        msg.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.MSWindowsFixedSizeDialogHint
        )
        msg.setIcon(QMessageBox.Icon.Information)

        msg.exec()
    
    def show_invalid_msg(self):
        #QMessageBox.information(self, "提示", "输入不正确", QMessageBox.StandardButton.Ok)

        msg = QMessageBox(self)
        msg.setWindowTitle("提示")
        msg.setText("输入不正确")
        msg.setFixedSize(200, 100)

        msg.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.MSWindowsFixedSizeDialogHint
        )
        msg.setIcon(QMessageBox.Icon.Information)

        msg.exec()

    def init_loading(self):
        loading = QWidget()
        layout = QVBoxLayout()

        tip_label = QLabel("正在加载url, 请稍候...")
        tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(tip_label)

        loading.setLayout(layout)

        return loading

    def switch_to_loading(self):
        self.stacked_widget.setCurrentIndex(1)

        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowMinimizeButtonHint
            )
        self.show()

        # hpr窗口关闭信号 在创建新的hpr窗口之前
        self.sgn_hpr_cls.emit(True)

        # 设置并加载url
        self.default_url = 'https://app.hyperate.io/' + self.hprID
        
        if self.is_default:
            self.hpr_win = HypeRateWin(self.default_url)
        else:
            self.hpr_win = HypeRateWin(self.custom_url)

        self.hpr_win.sgn_loading_done.connect(self.recv_sgn_done)
        self.hpr_win.show()
    
    def recv_sgn_done(self, done):
        if done:
            self.close()

# 窗口状态变量
is_killed = False
last_pos_win = None
is_hidding = False

class HypeRateWin(QMainWindow):

    sgn_loading_done = pyqtSignal(bool)

    def __init__(self, url):
        super().__init__()

        self.setWindowTitle("心率显示")
        #self.setGeometry(350, 100, 250, 100)
        global last_pos_win
        if last_pos_win:
            self.move(last_pos_win)
        else:
            self.move(350, 100)
        self.setFixedSize(250, 100)
        self.setWindowIcon(QIcon(get_resource_path('heart.ico')))
        self.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowDoesNotAcceptFocus # 在任务栏不出现
            ) # 无边框 始终置顶
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True) # 窗口透明

        # 初始化留存坐标
        last_pos_win = self.pos()

        # 安装事件过滤器
        self.installEventFilter(self)

        # 初始化浏览器组件
        self.browser = QWebEngineView()
        self.browser.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) # 浏览器忽略鼠标事件
        self.browser.setFocusPolicy(Qt.FocusPolicy.NoFocus) # 浏览器禁用键盘
        self.browser.page().settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False) # 隐藏滚动条
        self.browser.page().setBackgroundColor(Qt.GlobalColor.transparent) # 将页面的背景设为透明
        self.browser.setVisible(False) # 初始化不可见
        self.browser.page().loadFinished.connect(self.load_done) # 设置当页面加载完成再渲染可见 否则出现渲染错误
        self.setCentralWidget(self.browser)
        self.browser.load(QUrl(url))

        # 初始化系统托盘
        self.tray_icon = QSystemTrayIcon(QIcon(get_resource_path('heart.ico')))
        self.tray_icon.setToolTip("心率显示")
        
        self.tray_menu = QMenu(self)

        self.show_action = QAction("隐藏窗口", self)
        self.show_action.triggered.connect(self.toggle_hide)
        self.tray_menu.addAction(self.show_action)

        change_action = QAction("切换样式", self)
        change_action.triggered.connect(self.open_menu)
        self.tray_menu.addAction(change_action)

        web_action = QAction("设计网站", self)
        web_action.triggered.connect(open_website)
        self.tray_menu.addAction(web_action)

        self.killmouse_action = QAction("窗口穿透", self)
        self.killmouse_action.triggered.connect(self.toggle_kill_mouse)
        self.tray_menu.addAction(self.killmouse_action)

        quit_action = QAction("退出应用", self)
        quit_action.triggered.connect(self.quit_app)
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_click) # 托盘图标被激活
        self.tray_icon.show()

        # 恢复之前状态
        if is_killed:
            self.kill_mouse()
        if is_hidding:
            self.move_away()


    def on_tray_click(self,reason):
        global last_pos_win
        global is_hidding
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            is_hidding = False
            self.move(last_pos_win)
            self.show()
            self.raise_()
            self.show_action.setText("隐藏窗口")

    def load_done(self):
        self.sgn_loading_done.emit(True)
        self.browser.setVisible(True)


    def toggle_hide(self):
        global is_hidding
        if not is_hidding:
            is_hidding = True
            self.move_away()
        else:
            is_hidding = False
            self.move_back()
            
    
    def move_back(self):
        global last_pos_win
        self.move(last_pos_win) # 回到原来的位置
        self.show_action.setText("隐藏窗口")

    def move_away(self):
        global last_pos_win
        last_pos_win = self.pos() # 记录隐藏前的位置
        self.move(-1000, -1000) # 使窗口离开视线的同时能继续加载动画
        self.show_action.setText("显示窗口")

    def open_menu(self):
        self.menu_win = MenuWin()
        self.menu_win.sgn_hpr_cls.connect(self.hpr_close)
        self.menu_win.show()
    
    def hpr_close(self, close):
        if close:
            self.tray_icon.hide()
            self.close()


    def toggle_kill_mouse(self):
        global is_killed

        if is_killed:
            is_killed = False
            self.kill_mouse_deny()
        else:
            is_killed = True
            self.kill_mouse()

    def kill_mouse(self):
        hwnd = self.winId().__int__()
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setMouseTracking(False)
        ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        self.killmouse_action.setText("窗口穿透√")
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

    def kill_mouse_deny(self):
        hwnd = self.winId().__int__()
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)
        ex_style &= ~(win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        self.killmouse_action.setText("窗口穿透")
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

    def quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()


    is_dragging = False

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        global last_pos_win
        if obj != self:
            return False

        if event.type() == QEvent.Type.MouseButtonPress:
            mouse_event: QMouseEvent = event
            if mouse_event.button() == Qt.MouseButton.LeftButton:
                self.is_dragging = True
                self.last_pos = mouse_event.pos()
            elif mouse_event.button() == Qt.MouseButton.RightButton and not self.is_dragging:
                self.tray_menu.exec(self.pos()+mouse_event.pos())  # 右键菜单
            return True

        elif event.type() == QEvent.Type.MouseMove:
            if self.is_dragging:
                mouse_event: QMouseEvent = event
                delta = mouse_event.pos() - self.last_pos
                self.move(self.pos()+delta)
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            return True

        elif event.type() == QEvent.Type.MouseButtonRelease:
            mouse_event: QMouseEvent = event
            if mouse_event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
                self.is_dragging = False
                last_pos_win = self.pos()
                self.setCursor(Qt.CursorShape.ArrowCursor)
            return True

        return False     

if __name__ == "__main__":
    app = QApplication(sys.argv)

    menu_win = MenuWin()
    menu_win.show()

    sys.exit(app.exec())