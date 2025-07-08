import os
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
    os.path.dirname(__file__),
    "venv", "Lib", "site-packages", "PyQt5", "Qt5", "plugins", "platforms"
)

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QFileDialog, QLabel, QTabWidget, QDateEdit, QLineEdit, QComboBox, QMenuBar, QMenu, QAction, QInputDialog, QMessageBox, QDialog
)
from PyQt5.QtCore import QDate, QThread, pyqtSignal, QSettings, Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QStyle
from git_utils import get_git_commits
from ai_client import call_qwen
from exporter import export_report
import pyperclip
import re

class AIStreamThread(QThread):
    chunk_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        for chunk in call_qwen(self.prompt):
            self.chunk_received.emit(chunk)
        self.finished.emit()

class ApiKeyDialog(QDialog):
    def __init__(self, current_key, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置API Key")
        self.setMinimumWidth(500)
        self.api_key = None

        layout = QVBoxLayout(self)

        label = QLabel("请输入新的API Key：")
        layout.addWidget(label)

        self.input = QLineEdit(self)
        self.input.setText(current_key)
        layout.addWidget(self.input)

        # 蓝色超链接风格的帮助按钮
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        help_btn = QPushButton("API Key获取帮助？", self)
        help_btn.setCursor(Qt.PointingHandCursor)
        help_btn.setStyleSheet("QPushButton { color: #409eff; background: transparent; border: none; text-decoration: underline; font-size: 14px; } QPushButton:hover { color: #66b1ff; }")
        help_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://bailian.console.aliyun.com/console?tab=model#/api-key")))
        hbox.addWidget(help_btn)
        layout.addLayout(hbox)

        btn_box = QHBoxLayout()
        ok_btn = QPushButton("确定", self)
        cancel_btn = QPushButton("取消", self)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_box.addStretch(1)
        btn_box.addWidget(ok_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

    def get_api_key(self):
        return self.input.text().strip()

class DailyReportApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI日报生成工具 v0.0.1")
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        self.resize(1200, 700)
        self.selected_dirs = []
        self.user_combos = {}  # 每个tab的用户下拉框

        # 菜单栏
        self.menu_bar = QMenuBar(self)
        settings_menu = QMenu("设置", self)
        set_api_action = QAction("设置API Key", self)
        set_api_action.triggered.connect(self.set_api_key)
        settings_menu.addAction(set_api_action)
        self.menu_bar.addMenu(settings_menu)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setMenuBar(self.menu_bar)
        hbox = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.dir_label = QLabel("选择项目目录：")
        self.dir_button = QPushButton(QIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon)), "选择目录（覆盖）")
        self.dir_button.clicked.connect(self.select_dirs)
        self.add_dir_button = QPushButton(QIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder)), "添加目录")
        self.add_dir_button.clicked.connect(self.add_dir)
        # 按钮并排
        dir_btn_layout = QHBoxLayout()
        dir_btn_layout.addWidget(self.dir_button)
        dir_btn_layout.addWidget(self.add_dir_button)

        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        self.date_picker.dateChanged.connect(self.on_date_changed)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlainText("你是一名专业的产品开发人员，请根据以下 Git 提交记录中的标题和描述信息，帮我生成一份简洁明了的开发日报。要求如下：1.使用中文编写；2.分点列出每个提交的主要改动；3.总结今日工作成果；4.控制在 200~300 字以内；")
        self.prompt_input.setMinimumHeight(60)
        self.prompt_input.setMaximumHeight(120)

        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        left_layout.addWidget(self.dir_label)
        left_layout.addLayout(dir_btn_layout)
        left_layout.addWidget(QLabel("选择日期："))
        left_layout.addWidget(self.date_picker)
        left_layout.addWidget(QLabel("提示词："))
        left_layout.addWidget(self.prompt_input)
        left_layout.addWidget(self.tab_widget)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setMinimumHeight(300)
        self.output_edit.setStyleSheet("border-radius: 8px;")
        self.generate_button = QPushButton(QIcon(self.style().standardIcon(QStyle.SP_MediaPlay)), "生成日报")
        self.generate_button.clicked.connect(self.generate_report)
        self.copy_button = QPushButton(QIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton)), "复制内容")
        self.copy_button.clicked.connect(self.copy_report)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.copy_button)

        right_layout.addWidget(self.output_edit)
        right_layout.addLayout(button_layout)

        hbox.addLayout(left_layout, 3)
        hbox.addLayout(right_layout, 5)
        main_layout.addLayout(hbox)
        self.setLayout(main_layout)

        # 现代风格QSS样式表（精简Tab高度，去除QComboBox样式，Tab与下拉框有间距）
        self.setStyleSheet("""
            QWidget {
                font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
                font-size: 15px;
            }
            QTabWidget::pane {
                border: none;
                background: #f5f7fa;
                margin: 0 0 0 0;
            }
            QTabBar::tab {
                background: transparent;
                border: none;
                border-bottom: 2px solid transparent;
                min-width: 90px;
                min-height: 24px;
                margin-right: 16px;
                padding: 2px 0 2px 0;
                color: #606266;
                font-weight: 500;
                font-size: 15px;
                transition: color 0.2s, border-bottom 0.2s;
            }
            QTabBar::tab:selected {
                color: #409eff;
                border-bottom: 2px solid #409eff;
                background: transparent;
            }
            QTabBar::tab:hover {
                color: #409eff;
                background: #f0faff;
            }
            QTabBar::tab:!selected {
                background: transparent;
            }
            QLabel {
                color: #333;
                font-weight: bold;
            }
            QLineEdit, QDateEdit, QTextEdit {
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                padding: 6px;
                background: #f9f9f9;
            }
            QPushButton {
                background: #409eff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: bold;
                margin-top: 6px;
                margin-bottom: 6px;
            }
            QPushButton:hover {
                background: #66b1ff;
            }
            QPushButton:pressed {
                background: #337ecc;
            }
            QTextEdit[readOnly=\"true\"] {
                background: #f5f7fa;
                color: #666;
            }
        """)

    def select_dirs(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录", "", QFileDialog.ShowDirsOnly)
        if dir_path:
            self.selected_dirs = [dir_path]
            self.load_commits()

    def add_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "添加目录", "", QFileDialog.ShowDirsOnly)
        if dir_path and dir_path not in self.selected_dirs:
            self.selected_dirs.append(dir_path)
            self.load_commits()

    def load_commits(self):
        self.tab_widget.clear()
        self.user_combos = {}
        for path in self.selected_dirs:
            commits = get_git_commits(path, self.date_picker.date().toPyDate())
            # 按"【提交"分块
            blocks = re.split(r'(?=【提交)', commits)
            authors = set()
            block_info = []  # [(author, block)]
            for block in blocks:
                if not block.strip():
                    continue
                m = re.search(r'作者:\s*(.+)', block)
                if m:
                    author = m.group(1).strip()
                    authors.add(author)
                    block_info.append((author, block.strip()))
            # 用户下拉框
            user_combo = QComboBox()
            user_icon = QIcon(self.style().standardIcon(QStyle.SP_FileIcon))
            for author in sorted(authors):
                user_combo.addItem(user_icon, author)
            user_combo.currentIndexChanged.connect(self.on_user_changed)
            self.user_combos[path] = (user_combo, block_info)
            # 默认显示第一个用户的提交
            user_commits = self.filter_commits_by_author(block_info, user_combo.currentText())
            # tab内容布局
            tab_content = QWidget()
            vbox = QVBoxLayout()
            vbox.setContentsMargins(0,0,0,0)
            vbox.setSpacing(4)
            vbox.addSpacing(8)  # Tab和下拉框之间加间距
            vbox.addWidget(user_combo)
            vbox.addSpacing(8)  # 下拉框和内容之间加间距
            text_edit = QTextEdit()
            text_edit.setPlainText(user_commits)
            text_edit.setReadOnly(True)
            vbox.addWidget(text_edit)
            tab_content.setLayout(vbox)
            icon = self.style().standardIcon(QStyle.SP_DirIcon)
            self.tab_widget.addTab(tab_content, icon, os.path.basename(path))
        self.tab_widget.setCurrentIndex(0)

    def filter_commits_by_author(self, block_info, author):
        user_commits = [block for a, block in block_info if a == author]
        return '\n\n'.join(user_commits)

    def on_user_changed(self):
        idx = self.tab_widget.currentIndex()
        if idx < 0:
            return
        path = self.selected_dirs[idx]
        user_combo, block_info = self.user_combos.get(path, (None, []))
        if not user_combo:
            return
        author = user_combo.currentText()
        user_commits = self.filter_commits_by_author(block_info, author)
        tab_content = self.tab_widget.widget(idx)
        text_edit = tab_content.findChild(QTextEdit)
        if text_edit:
            text_edit.setPlainText(user_commits)

    def on_tab_changed(self, idx):
        self.on_user_changed()

    def on_date_changed(self, qdate):
        self.load_commits()

    def generate_report(self):
        settings = QSettings("daily_report_tool", "config")
        api_key = settings.value("api_key", "")
        if not api_key:
            QMessageBox.warning(self, "API Key未设置", "请先在设置菜单中输入有效的API Key！")
            return
        self.generate_button.setText("生成中...")
        self.generate_button.setEnabled(False)
        QApplication.processEvents()
        text = ""
        for i in range(self.tab_widget.count()):
            tab_content = self.tab_widget.widget(i)
            text_edit = tab_content.findChild(QTextEdit)
            if text_edit:
                text += text_edit.toPlainText() + "\n"
        selected_date = self.date_picker.date().toString("yyyy-MM-dd")
        prompt = f"{self.prompt_input.toPlainText()}\n今日日期：{selected_date}\n\n{text}"

        self.output_edit.clear()
        QApplication.processEvents()

        # 启动AI流式线程
        self.ai_thread = AIStreamThread(prompt)
        self.ai_thread.chunk_received.connect(self.output_edit.insertPlainText)
        self.ai_thread.finished.connect(self.on_ai_finished)
        self.ai_thread.start()

    def copy_report(self):
        pyperclip.copy(self.output_edit.toPlainText())

    def on_ai_finished(self):
        self.generate_button.setText("生成日报")
        self.generate_button.setEnabled(True)

    def set_api_key(self):
        settings = QSettings("daily_report_tool", "config")
        current_key = settings.value("api_key", "")
        dialog = ApiKeyDialog(current_key, self)
        if dialog.exec_() == QDialog.Accepted:
            key = dialog.get_api_key()
            if key:
                settings.setValue("api_key", key)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DailyReportApp()
    win.show()
    sys.exit(app.exec_())