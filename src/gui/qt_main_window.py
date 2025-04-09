#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyQt5主窗口模块
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTabWidget, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLabel, QStatusBar,
                            QAction, QToolBar, QFileDialog, QMessageBox,
                            QPushButton, QLineEdit, QComboBox, QCheckBox,
                            QProgressBar, QGroupBox, QRadioButton, QFrame,
                            QTreeWidget, QTreeWidgetItem)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize

from ..crypto.crypto_factory import crypto_factory
from ..crypto.key_manager import key_manager
from ..crypto.hash import hash_algorithms
from ..utils.logger import logger
from ..utils.translator import translator
from ..utils.theme_manager import theme_manager
from ..utils.app_updater import app_updater

from .. import __version__

class MainWindow(QMainWindow):
    """PyQt5主窗口类"""
    
    # 定义信号
    from PyQt5.QtCore import pyqtSignal
    encrypt_files_requested = pyqtSignal(list, bool)
    decrypt_files_requested = pyqtSignal(list, bool)
    generate_key_requested = pyqtSignal()
    import_key_requested = pyqtSignal()
    export_key_requested = pyqtSignal(str)
    delete_key_requested = pyqtSignal(str)
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口标题和大小
        self.setWindowTitle(translator.get_text("app_title"))
        self.resize(900, 600)
        
        # 居中显示
        self.center_window()
        
        # 设置应用图标
        self.set_app_icon()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央控件
        self.create_central_widget()
        
        # 加载设置
        self.load_settings()
        
        # 更新界面文本
        self.update_ui_texts()
        
        # 刷新密钥列表
        self.refresh_key_list()
        
        # 初始化和连接控制器
        from .controller import controller
        self.controller = controller
        self.controller.set_main_window(self)
        
        logger.info("PyQt5主窗口初始化完成")
    
    def center_window(self):
        """使窗口在屏幕上居中显示"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def set_app_icon(self):
        """设置应用图标"""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icon.png")
            if os.path.exists(icon_path):
                app_icon = QIcon(icon_path)
                self.setWindowIcon(app_icon)
                logger.info("已设置应用程序图标")
        except Exception as e:
            logger.warning(f"设置应用图标失败: {str(e)}")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        self.file_menu = menu_bar.addMenu("文件")
        
        # 加密文件菜单项
        self.encrypt_action = QAction(QIcon(), "加密文件", self)
        self.encrypt_action.setShortcut("Ctrl+E")
        self.encrypt_action.triggered.connect(self.encrypt_file_action)
        self.file_menu.addAction(self.encrypt_action)
        
        # 解密文件菜单项
        self.decrypt_action = QAction(QIcon(), "解密文件", self)
        self.decrypt_action.setShortcut("Ctrl+D")
        self.decrypt_action.triggered.connect(self.decrypt_file_action)
        self.file_menu.addAction(self.decrypt_action)
        
        self.file_menu.addSeparator()
        
        # 退出菜单项
        self.exit_action = QAction(QIcon(), "退出", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        # 工具菜单
        self.tools_menu = menu_bar.addMenu("工具")
        
        # 密钥管理菜单项
        self.keys_action = QAction(QIcon(), "密钥管理", self)
        self.keys_action.setShortcut("Ctrl+K")
        self.keys_action.triggered.connect(self.manage_keys_action)
        self.tools_menu.addAction(self.keys_action)
        
        # 设置菜单项
        self.settings_action = QAction(QIcon(), "设置", self)
        self.settings_action.setShortcut("Ctrl+P")
        self.settings_action.triggered.connect(self.settings_action_handler)
        self.tools_menu.addAction(self.settings_action)
        
        # 帮助菜单
        self.help_menu = menu_bar.addMenu("帮助")
        
        # 关于菜单项
        self.about_action = QAction(QIcon(), "关于", self)
        self.about_action.triggered.connect(self.about_action_handler)
        self.help_menu.addAction(self.about_action)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 状态标签
        self.status_label = QLabel(translator.get_text("ready"))
        self.status_label.setObjectName("status_main_label")  # 添加唯一对象名
        self.status_bar.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 任务标签
        self.task_label = QLabel("")
        self.task_label.setVisible(False)
        self.status_bar.addPermanentWidget(self.task_label)
    
    def create_central_widget(self):
        """创建中央窗口部件"""
        # 创建主标签页
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # 创建各个选项卡
        self.create_encrypt_tab()
        self.create_decrypt_tab()
        self.create_keys_tab()
        self.create_monitor_tab()
        self.create_settings_tab()
    
    def create_encrypt_tab(self):
        """创建加密选项卡"""
        encrypt_tab = QWidget()
        layout = QVBoxLayout(encrypt_tab)
        
        # 标题和说明
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel("文件加密")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # 描述
        description = QLabel("加密您的文件和文件夹，确保数据安全")
        description.setFont(QFont("Arial", 9))
        header_layout.addWidget(description)
        
        layout.addWidget(header_frame)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 加密算法选择组
        algo_group = QGroupBox("加密算法")
        algo_layout = QHBoxLayout(algo_group)
        
        algo_label = QLabel("选择加密算法:")
        algo_layout.addWidget(algo_label)
        
        self.encrypt_algorithm_combo = QComboBox()
        self.encrypt_algorithm_combo.addItems(crypto_factory.get_all_algorithms())
        algo_layout.addWidget(self.encrypt_algorithm_combo)
        
        algo_layout.addStretch(1)
        layout.addWidget(algo_group)
        
        # 文件选择组
        file_group = QGroupBox("要加密的文件/文件夹")
        file_layout = QHBoxLayout(file_group)
        
        self.encrypt_file_edit = QLineEdit()
        self.encrypt_file_edit.setPlaceholderText("选择文件或文件夹...")
        file_layout.addWidget(self.encrypt_file_edit)
        
        file_button = QPushButton("选择文件")
        file_button.clicked.connect(self.select_encrypt_file)
        file_layout.addWidget(file_button)
        
        folder_button = QPushButton("选择文件夹")
        folder_button.clicked.connect(self.select_encrypt_folder)
        file_layout.addWidget(folder_button)
        
        layout.addWidget(file_group)
        
        # 密钥选择组
        key_group = QGroupBox("加密密钥")
        key_layout = QHBoxLayout(key_group)
        
        key_label = QLabel("选择密钥:")
        key_layout.addWidget(key_label)
        
        self.encrypt_key_combo = QComboBox()
        key_layout.addWidget(self.encrypt_key_combo)
        
        key_button = QPushButton("管理密钥")
        key_button.clicked.connect(self.manage_keys_action)
        key_layout.addWidget(key_button)
        
        new_key_button = QPushButton("生成新密钥")
        new_key_button.clicked.connect(self.generate_encrypt_key)
        key_layout.addWidget(new_key_button)
        
        layout.addWidget(key_group)
        
        # 加密选项组
        options_group = QGroupBox("加密选项")
        options_layout = QVBoxLayout(options_group)
        
        self.delete_after_encrypt = QCheckBox("加密后删除原文件")
        options_layout.addWidget(self.delete_after_encrypt)
        
        self.verify_after_encrypt = QCheckBox("加密后验证文件完整性")
        self.verify_after_encrypt.setChecked(True)
        options_layout.addWidget(self.verify_after_encrypt)
        
        layout.addWidget(options_group)
        
        # 添加间隔
        layout.addStretch(1)
        
        # 执行按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        encrypt_button = QPushButton("加密")
        encrypt_button.setMinimumWidth(100)
        encrypt_button.clicked.connect(self.start_encrypt)
        button_layout.addWidget(encrypt_button)
        
        layout.addLayout(button_layout)
        
        # 将选项卡添加到选项卡控件
        self.tab_widget.addTab(encrypt_tab, "加密")
    
    def create_decrypt_tab(self):
        """创建解密选项卡"""
        decrypt_tab = QWidget()
        layout = QVBoxLayout(decrypt_tab)
        
        # 标题和说明
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel("文件解密")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # 描述
        description = QLabel("解密之前使用本工具加密的文件")
        description.setFont(QFont("Arial", 9))
        header_layout.addWidget(description)
        
        layout.addWidget(header_frame)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 文件选择组
        file_group = QGroupBox("要解密的文件")
        file_layout = QHBoxLayout(file_group)
        
        self.decrypt_file_edit = QLineEdit()
        self.decrypt_file_edit.setPlaceholderText("选择已加密的文件...")
        file_layout.addWidget(self.decrypt_file_edit)
        
        file_button = QPushButton("选择文件")
        file_button.clicked.connect(self.select_decrypt_file)
        file_layout.addWidget(file_button)
        
        layout.addWidget(file_group)
        
        # 密钥选择组
        key_group = QGroupBox("解密密钥")
        key_layout = QHBoxLayout(key_group)
        
        key_label = QLabel("选择密钥:")
        key_layout.addWidget(key_label)
        
        self.decrypt_key_combo = QComboBox()
        key_layout.addWidget(self.decrypt_key_combo)
        
        key_button = QPushButton("管理密钥")
        key_button.clicked.connect(self.manage_keys_action)
        key_layout.addWidget(key_button)
        
        layout.addWidget(key_group)
        
        # 输出目录组
        output_group = QGroupBox("输出设置")
        output_layout = QHBoxLayout(output_group)
        
        output_label = QLabel("输出到:")
        output_layout.addWidget(output_label)
        
        self.decrypt_output_edit = QLineEdit()
        self.decrypt_output_edit.setPlaceholderText("默认使用源文件所在目录")
        output_layout.addWidget(self.decrypt_output_edit)
        
        output_button = QPushButton("选择目录")
        output_button.clicked.connect(self.select_decrypt_output)
        output_layout.addWidget(output_button)
        
        layout.addWidget(output_group)
        
        # 解密选项组
        options_group = QGroupBox("解密选项")
        options_layout = QVBoxLayout(options_group)
        
        self.delete_after_decrypt = QCheckBox("解密后删除加密文件")
        options_layout.addWidget(self.delete_after_decrypt)
        
        self.verify_after_decrypt = QCheckBox("解密后验证文件完整性")
        self.verify_after_decrypt.setChecked(True)
        options_layout.addWidget(self.verify_after_decrypt)
        
        layout.addWidget(options_group)
        
        # 添加间隔
        layout.addStretch(1)
        
        # 执行按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        decrypt_button = QPushButton("解密")
        decrypt_button.setMinimumWidth(100)
        decrypt_button.clicked.connect(self.start_decrypt)
        button_layout.addWidget(decrypt_button)
        
        layout.addLayout(button_layout)
        
        # 将选项卡添加到选项卡控件
        self.tab_widget.addTab(decrypt_tab, "解密")
    
    def create_keys_tab(self):
        """创建密钥管理选项卡"""
        keys_tab = QWidget()
        layout = QVBoxLayout(keys_tab)
        
        # 标题和说明
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel("密钥管理")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # 描述
        description = QLabel("管理您的加密密钥")
        description.setFont(QFont("Arial", 9))
        header_layout.addWidget(description)
        
        layout.addWidget(header_frame)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 密钥列表框架
        keys_group = QGroupBox("密钥列表")
        keys_layout = QVBoxLayout(keys_group)
        
        # 搜索栏
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        search_layout.addWidget(search_label)
        
        self.key_search_edit = QLineEdit()
        self.key_search_edit.setPlaceholderText("按密钥名称搜索...")
        self.key_search_edit.textChanged.connect(self.filter_keys)
        search_layout.addWidget(self.key_search_edit)
        
        keys_layout.addLayout(search_layout)
        
        # 密钥列表
        self.key_tree = QTreeWidget()
        self.key_tree.setHeaderLabels(["密钥名称", "类型", "算法", "受密码保护"])
        self.key_tree.setAlternatingRowColors(True)
        self.key_tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.key_tree.setRootIsDecorated(False)
        self.key_tree.itemSelectionChanged.connect(self.on_key_selection_changed)
        keys_layout.addWidget(self.key_tree)
        
        layout.addWidget(keys_group)
        
        # 密钥操作按钮
        buttons_layout = QHBoxLayout()
        
        self.create_key_button = QPushButton("新建密钥")
        self.create_key_button.clicked.connect(self.generate_key)
        buttons_layout.addWidget(self.create_key_button)
        
        self.import_key_button = QPushButton("导入密钥")
        self.import_key_button.clicked.connect(self.import_key)
        buttons_layout.addWidget(self.import_key_button)
        
        self.export_key_button = QPushButton("导出密钥")
        self.export_key_button.clicked.connect(self.export_key)
        self.export_key_button.setEnabled(False)
        buttons_layout.addWidget(self.export_key_button)
        
        self.delete_key_button = QPushButton("删除密钥")
        self.delete_key_button.clicked.connect(self.delete_key)
        self.delete_key_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_key_button)
        
        layout.addLayout(buttons_layout)
        
        # 将选项卡添加到选项卡控件
        self.tab_widget.addTab(keys_tab, "密钥管理")
    
    def create_monitor_tab(self):
        """创建文件监控选项卡"""
        monitor_tab = QWidget()
        layout = QVBoxLayout(monitor_tab)
        
        # 标题和说明
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel("文件监控")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # 描述
        description = QLabel("监控目录中的文件变化，自动加密或解密新文件")
        description.setFont(QFont("Arial", 9))
        header_layout.addWidget(description)
        
        layout.addWidget(header_frame)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 监控任务列表
        task_group = QGroupBox("监控任务")
        task_layout = QVBoxLayout(task_group)
        
        # 创建监控任务列表
        self.monitor_tree = QTreeWidget()
        self.monitor_tree.setHeaderLabels(["任务ID", "监控目录", "是否自动处理", "状态"])
        self.monitor_tree.setAlternatingRowColors(True)
        self.monitor_tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.monitor_tree.itemSelectionChanged.connect(self.on_monitor_selection_changed)
        
        # 调整列宽
        self.monitor_tree.setColumnWidth(0, 100)
        self.monitor_tree.setColumnWidth(1, 250)
        self.monitor_tree.setColumnWidth(2, 100)
        
        task_layout.addWidget(self.monitor_tree)
        
        # 按钮面板
        button_layout = QHBoxLayout()
        
        # 添加任务按钮
        self.add_monitor_btn = QPushButton("添加监控")
        self.add_monitor_btn.setIcon(QIcon())
        self.add_monitor_btn.clicked.connect(self.add_monitor_task)
        button_layout.addWidget(self.add_monitor_btn)
        
        # 编辑任务按钮
        self.edit_monitor_btn = QPushButton("编辑")
        self.edit_monitor_btn.setIcon(QIcon())
        self.edit_monitor_btn.clicked.connect(self.edit_monitor_task)
        self.edit_monitor_btn.setEnabled(False)
        button_layout.addWidget(self.edit_monitor_btn)
        
        # 删除任务按钮
        self.delete_monitor_btn = QPushButton("删除")
        self.delete_monitor_btn.setIcon(QIcon())
        self.delete_monitor_btn.clicked.connect(self.delete_monitor_task)
        self.delete_monitor_btn.setEnabled(False)
        button_layout.addWidget(self.delete_monitor_btn)
        
        # 刷新按钮
        self.refresh_monitor_btn = QPushButton("刷新")
        self.refresh_monitor_btn.setIcon(QIcon())
        self.refresh_monitor_btn.clicked.connect(self.refresh_monitor_tasks)
        button_layout.addWidget(self.refresh_monitor_btn)
        
        task_layout.addLayout(button_layout)
        layout.addWidget(task_group)
        
        # 详细信息组
        detail_group = QGroupBox("任务详情")
        detail_layout = QVBoxLayout(detail_group)
        
        # 创建详细信息文本框
        self.monitor_detail = QLabel("选择一个监控任务查看详细信息")
        self.monitor_detail.setWordWrap(True)
        self.monitor_detail.setTextInteractionFlags(Qt.TextSelectableByMouse)
        detail_layout.addWidget(self.monitor_detail)
        
        layout.addWidget(detail_group)
        
        # 添加到主标签页
        self.tab_widget.addTab(monitor_tab, "文件监控")
    
    def create_settings_tab(self):
        """创建设置选项卡"""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        
        # 标题和说明
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel(translator.get_text("settings_title"))
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # 描述
        description = QLabel(translator.get_text("settings_desc"))
        description.setFont(QFont("Arial", 9))
        header_layout.addWidget(description)
        
        layout.addWidget(header_frame)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 通用设置组
        general_group = QGroupBox(translator.get_text("settings_general"))
        general_layout = QVBoxLayout(general_group)
        
        # 语言设置
        lang_layout = QHBoxLayout()
        lang_label = QLabel(translator.get_text("settings_language"))
        lang_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        # 获取可用的语言
        available_languages = translator.get_available_languages()
        for lang_code, lang_name in available_languages.items():
            self.language_combo.addItem(lang_name, lang_code)
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch(1)
        general_layout.addLayout(lang_layout)
        
        # 主题设置
        theme_layout = QHBoxLayout()
        theme_label = QLabel(translator.get_text("settings_theme"))
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        # 获取可用的主题
        available_themes = theme_manager.get_available_themes()
        theme_display_names = {
            "light": translator.get_text("theme_light"),
            "dark": translator.get_text("theme_dark"),
            "blue": translator.get_text("theme_blue"),
            "green": translator.get_text("theme_green"),
            "purple": translator.get_text("theme_purple")
        }
        
        for theme in available_themes:
            display_name = theme_display_names.get(theme, theme)
            self.theme_combo.addItem(display_name, theme)
            
        # 主题预览功能
        self.theme_combo.currentIndexChanged.connect(self.preview_theme)
        theme_layout.addWidget(self.theme_combo)
        
        # 预览按钮
        preview_button = QPushButton(translator.get_text("preview"))
        preview_button.clicked.connect(self.preview_theme)
        theme_layout.addWidget(preview_button)
        
        theme_layout.addStretch(1)
        general_layout.addLayout(theme_layout)
        
        layout.addWidget(general_group)
        
        # 加密设置组
        encrypt_group = QGroupBox(translator.get_text("settings_encryption"))
        encrypt_layout = QVBoxLayout(encrypt_group)
        
        # 文件分块大小
        chunk_layout = QHBoxLayout()
        chunk_label = QLabel(translator.get_text("settings_buffer"))
        chunk_layout.addWidget(chunk_label)
        
        self.chunk_size_combo = QComboBox()
        self.chunk_size_combo.addItems(["1KB", "2KB", "4KB", "8KB", "16KB", "32KB"])
        chunk_layout.addWidget(self.chunk_size_combo)
        chunk_layout.addStretch(1)
        encrypt_layout.addLayout(chunk_layout)
        
        # 默认加密算法
        algo_layout = QHBoxLayout()
        algo_label = QLabel(translator.get_text("settings_default_algorithm"))
        algo_layout.addWidget(algo_label)
        
        self.default_algo_combo = QComboBox()
        self.default_algo_combo.addItems(crypto_factory.get_all_algorithms())
        algo_layout.addWidget(self.default_algo_combo)
        algo_layout.addStretch(1)
        encrypt_layout.addLayout(algo_layout)
        
        layout.addWidget(encrypt_group)
        
        # 添加间隔
        layout.addStretch(1)
        
        # 保存按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        reset_button = QPushButton(translator.get_text("settings_reset"))
        reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_button)
        
        save_button = QPushButton(translator.get_text("settings_save"))
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        # 将选项卡添加到选项卡控件
        self.tab_widget.addTab(settings_tab, translator.get_text("tab_settings"))
    
    def load_settings(self):
        """加载设置"""
        from ..config.app_settings import settings
        
        # 加载UI设置
        # 设置当前语言
        lang_code = settings.get("ui", "language", "zh_CN")
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == lang_code:
                self.language_combo.setCurrentIndex(i)
                break
        
        # 设置当前主题
        theme_name = settings.get("ui", "theme", "light")
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == theme_name:
                self.theme_combo.setCurrentIndex(i)
                break
        
        # 加载加密设置
        chunk_size = settings.get("encryption", "chunk_size", 4096)
        chunk_map = {1024: "1KB", 2048: "2KB", 4096: "4KB", 8192: "8KB", 16384: "16KB", 32768: "32KB"}
        self.chunk_size_combo.setCurrentText(chunk_map.get(chunk_size, "4KB"))
        
        algo = settings.get("encryption", "default_algorithm", "AES-256-CBC")
        index = self.default_algo_combo.findText(algo)
        if index >= 0:
            self.default_algo_combo.setCurrentIndex(index)
            
        # 更新加密解密默认选项
        self.verify_after_encrypt.setChecked(settings.get("encryption", "verify_after_encryption", True))
        self.verify_after_decrypt.setChecked(settings.get("encryption", "verify_after_encryption", True))
        self.delete_after_encrypt.setChecked(settings.get("encryption", "secure_delete_original", False))
    
    def save_settings(self):
        """保存设置"""
        from ..config.app_settings import settings
        
        # 保存UI设置
        lang_code = self.language_combo.currentData()
        settings.set("ui", "language", lang_code)
        
        theme_name = self.theme_combo.currentData()
        settings.set("ui", "theme", theme_name)
        
        # 保存加密设置
        chunk_map = {"1KB": 1024, "2KB": 2048, "4KB": 4096, "8KB": 8192, "16KB": 16384, "32KB": 32768}
        chunk_size = chunk_map.get(self.chunk_size_combo.currentText(), 4096)
        settings.set("encryption", "chunk_size", chunk_size)
        
        algo = self.default_algo_combo.currentText()
        settings.set("encryption", "default_algorithm", algo)
        
        # 保存验证和安全删除设置
        settings.set("encryption", "verify_after_encryption", self.verify_after_encrypt.isChecked())
        settings.set("encryption", "secure_delete_original", self.delete_after_encrypt.isChecked())
        
        # 保存所有设置
        settings.save_all()
        
        # 使用应用更新器更新语言和主题
        app_updater.update_language(lang_code)
        app_updater.update_theme(theme_name)
        
        # 显示成功消息
        QMessageBox.information(self, translator.get_text("dialog_info"), 
                             translator.get_text("settings_saved"))
    
    def update_ui_texts(self):
        """更新界面上的所有文本为当前语言"""
        # 更新窗口标题
        self.setWindowTitle(translator.get_text("app_title"))
        
        # 更新菜单
        self.file_menu.setTitle(translator.get_text("menu_file"))
        self.tools_menu.setTitle(translator.get_text("menu_tools"))
        self.help_menu.setTitle(translator.get_text("menu_help"))
        
        # 更新菜单项
        self.encrypt_action.setText(translator.get_text("menu_encrypt"))
        self.decrypt_action.setText(translator.get_text("menu_decrypt"))
        self.exit_action.setText(translator.get_text("menu_exit"))
        self.keys_action.setText(translator.get_text("menu_keys"))
        self.settings_action.setText(translator.get_text("menu_settings"))
        self.about_action.setText(translator.get_text("menu_about"))
        
        # 更新标签页标题
        for i in range(self.tab_widget.count()):
            tab_name = ""
            if i == 0:
                tab_name = translator.get_text("tab_encrypt")
            elif i == 1:
                tab_name = translator.get_text("tab_decrypt")
            elif i == 2:
                tab_name = translator.get_text("tab_keys")
            elif i == 3:
                tab_name = translator.get_text("tab_monitor")
            elif i == 4:
                tab_name = translator.get_text("tab_settings")
            
            if tab_name:
                self.tab_widget.setTabText(i, tab_name)
                
        # 更新设置页面
        self._update_settings_tab_texts()
        
        # 更新加密/解密标签页
        self._update_encrypt_decrypt_tab_texts()
        
        # 更新密钥管理标签页
        self._update_keys_tab_texts()
        
        # 更新文件监控标签页
        self._update_monitor_tab_texts()
                
        # 更新状态栏 - 使用updateStatusBarMessage方法而不是直接设置
        self.updateStatusBarMessage(translator.get_text("ready"))
    
    def _update_settings_tab_texts(self):
        """更新设置标签页的文本"""
        # 只有在设置标签页已创建的情况下才更新
        if not hasattr(self, 'theme_combo') or not hasattr(self, 'language_combo'):
            return
            
        # 刷新可用主题的显示名称
        theme_display_names = {
            "light": translator.get_text("theme_light"),
            "dark": translator.get_text("theme_dark"),
            "blue": translator.get_text("theme_blue"),
            "green": translator.get_text("theme_green"),
            "purple": translator.get_text("theme_purple")
        }
        
        # 保存当前选中的主题
        current_theme_data = self.theme_combo.currentData()
        
        # 清空并重新填充主题下拉框
        self.theme_combo.blockSignals(True)  # 阻止信号触发预览
        self.theme_combo.clear()
        
        for theme in theme_manager.get_available_themes():
            display_name = theme_display_names.get(theme, theme)
            self.theme_combo.addItem(display_name, theme)
        
        # 恢复选中的主题
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme_data:
                self.theme_combo.setCurrentIndex(i)
                break
        
        self.theme_combo.blockSignals(False)  # 恢复信号
    
    def _update_encrypt_decrypt_tab_texts(self):
        """更新加密/解密标签页的文本"""
        # 这里添加加密解密标签页文本的更新逻辑
        pass
    
    def _update_keys_tab_texts(self):
        """更新密钥管理标签页的文本"""
        # 检查密钥管理标签页是否已创建
        if not hasattr(self, 'key_tree'):
            return
            
        # 更新树形控件标题
        header_labels = [
            translator.get_text("keys_name"),
            translator.get_text("keys_type"),
            translator.get_text("keys_algo"),
            translator.get_text("keys_protected")
        ]
        self.key_tree.setHeaderLabels(header_labels)
        
        # 更新按钮文本
        if hasattr(self, 'create_key_button'):
            self.create_key_button.setText(translator.get_text("keys_create"))
        if hasattr(self, 'import_key_button'):
            self.import_key_button.setText(translator.get_text("keys_import"))
        if hasattr(self, 'export_key_button'):
            self.export_key_button.setText(translator.get_text("keys_export"))
        if hasattr(self, 'delete_key_button'):
            self.delete_key_button.setText(translator.get_text("keys_delete"))
        
        # 更新标题和说明
        if hasattr(self, 'key_title_label'):
            self.key_title_label.setText(translator.get_text("keys_title"))
        if hasattr(self, 'key_desc_label'):
            self.key_desc_label.setText(translator.get_text("keys_desc"))
        
        # 更新过滤标签
        if hasattr(self, 'filter_label'):
            self.filter_label.setText(translator.get_text("keys_filter"))
            
        # 更新现有项的"是"/"否"文本（受保护）
        for i in range(self.key_tree.topLevelItemCount()):
            item = self.key_tree.topLevelItem(i)
            protected = item.text(3)
            # 如果是"是"或"否"，更新为当前语言的值
            if protected == "是" or protected == "Yes":
                item.setText(3, translator.get_text("yes"))
            elif protected == "否" or protected == "No":
                item.setText(3, translator.get_text("no"))
                
        # 更新现有项的类型文本
        for i in range(self.key_tree.topLevelItemCount()):
            item = self.key_tree.topLevelItem(i)
            key_type = item.text(1)
            if key_type == "对称密钥" or key_type == "Symmetric":
                item.setText(1, translator.get_text("key_type_symmetric"))
            elif key_type == "非对称密钥" or key_type == "Asymmetric":
                item.setText(1, translator.get_text("key_type_asymmetric"))
        
        # 调整列宽以适应新文本
        for i in range(self.key_tree.columnCount()):
            self.key_tree.resizeColumnToContents(i)
    
    def _update_monitor_tab_texts(self):
        """更新文件监控标签页的文本"""
        # 检查监控标签页是否已创建
        if not hasattr(self, 'monitor_tree'):
            return
            
        # 更新树形控件标题
        header_labels = [
            translator.get_text("monitor_id"),
            translator.get_text("monitor_dir"),
            translator.get_text("monitor_auto"),
            translator.get_text("monitor_status")
        ]
        self.monitor_tree.setHeaderLabels(header_labels)
        
        # 更新按钮文本
        if hasattr(self, 'add_monitor_button'):
            self.add_monitor_button.setText(translator.get_text("monitor_add"))
        if hasattr(self, 'edit_monitor_button'):
            self.edit_monitor_button.setText(translator.get_text("monitor_edit"))
        if hasattr(self, 'delete_monitor_button'):
            self.delete_monitor_button.setText(translator.get_text("monitor_delete"))
        if hasattr(self, 'refresh_monitor_button'):
            self.refresh_monitor_button.setText(translator.get_text("monitor_refresh"))
        
        # 更新标题和说明
        if hasattr(self, 'monitor_title_label'):
            self.monitor_title_label.setText(translator.get_text("monitor_title"))
        if hasattr(self, 'monitor_desc_label'):
            self.monitor_desc_label.setText(translator.get_text("monitor_desc"))
        
        # 更新详情区域
        if hasattr(self, 'detail_box'):
            self.detail_box.setTitle(translator.get_text("monitor_details"))
        if hasattr(self, 'select_info_label'):
            self.select_info_label.setText(translator.get_text("monitor_select"))
            
        # 更新现有项的是/否文本
        for i in range(self.monitor_tree.topLevelItemCount()):
            item = self.monitor_tree.topLevelItem(i)
            auto_process = item.text(2)
            # 如果是'是'或'否'，更新为当前语言的值
            if auto_process == "是" or auto_process == "Yes":
                item.setText(2, translator.get_text("yes"))
            elif auto_process == "否" or auto_process == "No":
                item.setText(2, translator.get_text("no"))
                
        # 调整列宽以适应新文本
        for i in range(self.monitor_tree.columnCount()):
            self.monitor_tree.resizeColumnToContents(i)
        
    def update_ui_style(self):
        """更新界面样式"""
        # 更新所有标签页的样式
        self._update_settings_tab_style()
        self._update_encrypt_decrypt_tab_style()
        self._update_keys_tab_style()
        self._update_monitor_tab_style()
        
        # 刷新所有控件
        self.repaint()
    
    def _update_settings_tab_style(self):
        """更新设置标签页的样式"""
        # 这里添加更新设置标签页样式的逻辑
        pass
    
    def _update_encrypt_decrypt_tab_style(self):
        """更新加密/解密标签页的样式"""
        # 这里添加更新加密解密标签页样式的逻辑
        pass
    
    def _update_keys_tab_style(self):
        """更新密钥管理标签页的样式"""
        # 这里添加更新密钥管理标签页样式的逻辑
        pass
    
    def _update_monitor_tab_style(self):
        """更新文件监控标签页的样式"""
        # 这里添加更新文件监控标签页样式的逻辑
        pass

    def reset_settings(self):
        """重置设置为默认值"""
        from ..config.app_settings import settings
        
        # 确认重置
        reply = QMessageBox.question(self, translator.get_text("dialog_confirm"), 
                                    translator.get_text("settings_reset_confirm"),
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
            
        # 重置设置
        settings.reset()
        
        # 获取默认主题和语言
        default_theme = settings.get("ui", "theme", "light")
        default_language = settings.get("ui", "language", "zh_CN")
        
        # 应用默认主题和语言
        app_updater.update_theme(default_theme)
        app_updater.update_language(default_language)
        
        # 重新加载设置
        self.load_settings()
        
        QMessageBox.information(self, translator.get_text("dialog_info"), 
                             translator.get_text("settings_reset_success"))

    def preview_theme(self):
        """预览选中的主题"""
        theme_name = self.theme_combo.currentData()
        if theme_name:
            # 预览主题，但不保存设置
            theme_manager.apply_theme(theme_name)
            # 更新UI文本以匹配新主题
            self.update_ui_texts()
    
    def select_encrypt_file(self):
        """选择要加密的文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择要加密的文件", "", "所有文件 (*)")
        if file_path:
            self.encrypt_file_edit.setText(file_path)
    
    def select_encrypt_folder(self):
        """选择要加密的文件夹"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择要加密的文件夹", "")
        if folder_path:
            self.encrypt_file_edit.setText(folder_path)
    
    def select_decrypt_file(self):
        """选择要解密的文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择要解密的文件", "", "加密文件 (*.enc);;所有文件 (*)")
        if file_path:
            self.decrypt_file_edit.setText(file_path)
    
    def select_decrypt_output(self):
        """选择解密输出目录"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择解密输出目录", "")
        if folder_path:
            self.decrypt_output_edit.setText(folder_path)
    
    def generate_encrypt_key(self):
        """生成新的加密密钥"""
        self.generate_key_requested.emit()
    
    def start_encrypt(self):
        """开始加密操作"""
        file_path = self.encrypt_file_edit.text()
        if not file_path:
            QMessageBox.warning(self, "错误", "请选择要加密的文件或文件夹")
            return
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", "所选文件或文件夹不存在")
            return
        
        # 检查是否有选择密钥
        key_name = self.encrypt_key_combo.currentText()
        if not key_name:
            QMessageBox.warning(self, "错误", "请选择加密密钥")
            return
        
        # 获取文件路径列表
        file_paths = []
        if os.path.isfile(file_path):
            file_paths.append(file_path)
        else:
            file_paths.append(file_path)  # 添加文件夹路径，控制器会递归处理
        
        # 发送加密请求
        delete_original = self.delete_after_encrypt.isChecked()
        self.encrypt_files_requested.emit(file_paths, delete_original)
    
    def start_decrypt(self):
        """开始解密操作"""
        file_path = self.decrypt_file_edit.text()
        if not file_path:
            QMessageBox.warning(self, "错误", "请选择要解密的文件")
            return
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", "所选文件不存在")
            return
        
        # 检查是否有选择密钥
        key_name = self.decrypt_key_combo.currentText()
        if not key_name:
            QMessageBox.warning(self, "错误", "请选择解密密钥")
            return
        
        # 获取文件路径列表
        file_paths = []
        if os.path.isfile(file_path):
            file_paths.append(file_path)
        else:
            # 如果是文件夹，只获取有.enc后缀的文件
            for root, _, files in os.walk(file_path):
                for file in files:
                    if file.endswith(".enc"):
                        file_paths.append(os.path.join(root, file))
        
        if not file_paths:
            QMessageBox.warning(self, "错误", "找不到可解密的文件")
            return
        
        # 发送解密请求
        delete_original = self.delete_after_decrypt.isChecked()
        self.decrypt_files_requested.emit(file_paths, delete_original)
    
    def encrypt_file_action(self):
        """加密文件菜单动作"""
        self.tab_widget.setCurrentIndex(0)  # 切换到加密选项卡
    
    def decrypt_file_action(self):
        """解密文件菜单动作"""
        self.tab_widget.setCurrentIndex(1)  # 切换到解密选项卡
    
    def manage_keys_action(self):
        """密钥管理菜单动作"""
        self.tab_widget.setCurrentIndex(2)  # 切换到密钥管理选项卡
    
    def settings_action_handler(self):
        """处理设置菜单项点击"""
        # 切换到设置标签页
        self.tab_widget.setCurrentIndex(4)  # 假设设置是第5个标签页
    
    def about_action_handler(self):
        """显示关于对话框"""
        about_text = f"""文件加密工具 v{__version__}
        
版权所有 (c) 2025 
        
此软件使用多种加密算法保护您的文件安全，
包括AES、RSA和ChaCha20等。
        
感谢您的使用！
        """
        QMessageBox.about(self, translator.get_text("menu_about"), about_text)
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        reply = QMessageBox.question(self, "退出", "确定要退出吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    def refresh_key_list(self):
        """刷新密钥列表"""
        # 保存当前选择
        selected_key = None
        selected_items = self.key_tree.selectedItems()
        if selected_items:
            selected_key = selected_items[0].text(0)
        
        # 清空列表
        self.key_tree.clear()
        
        # 获取所有密钥
        keys_dict = key_manager.list_keys()
        
        # 填充列表
        for key_name, key_info in keys_dict.items():
            item = QTreeWidgetItem()
            item.setText(0, key_name)
            item.setText(1, key_info.get('algorithm', '未知'))
            
            # 创建时间暂时不显示
            item.setText(2, '未知')
            
            # 是否受密码保护
            is_protected = key_info.get('is_encrypted', False)
            item.setText(3, '是' if is_protected else '否')
            
            self.key_tree.addTopLevelItem(item)
        
        # 恢复之前的选择
        if selected_key:
            for i in range(self.key_tree.topLevelItemCount()):
                item = self.key_tree.topLevelItem(i)
                if item.text(0) == selected_key:
                    self.key_tree.setCurrentItem(item)
                    break
        
        # 调整列宽
        for i in range(4):
            self.key_tree.resizeColumnToContents(i)
        
        # 更新加密和解密选项卡的密钥下拉列表
        self.encrypt_key_combo.clear()
        self.decrypt_key_combo.clear()
        
        for key_name in keys_dict.keys():
            self.encrypt_key_combo.addItem(key_name)
            self.decrypt_key_combo.addItem(key_name)
    
    def filter_keys(self, text):
        """根据搜索文本过滤密钥列表"""
        text = text.lower()
        for i in range(self.key_tree.topLevelItemCount()):
            item = self.key_tree.topLevelItem(i)
            item.setHidden(text and text not in item.text(0).lower())
    
    def on_key_selection_changed(self):
        """处理密钥选择变化"""
        selected = len(self.key_tree.selectedItems()) > 0
        self.export_key_button.setEnabled(selected)
        self.delete_key_button.setEnabled(selected)
    
    def get_key_selection(self, keys_dict):
        """
        获取用户选择的密钥
        
        Args:
            keys_dict: 可用的密钥字典 (key_name -> key_info)
            
        Returns:
            str: 选择的密钥名称，如果取消则为None
        """
        from PyQt5.QtWidgets import QInputDialog
        
        key_names = list(keys_dict.keys())
        if not key_names:
            return None
            
        item, ok = QInputDialog.getItem(self, "选择密钥", "请选择密钥:", key_names, 0, False)
        if ok and item:
            return item
        return None
    
    def get_directory_selection(self, title, default_dir):
        """
        获取用户选择的目录
        
        Args:
            title: 对话框标题
            default_dir: 默认目录
            
        Returns:
            str: 选择的目录路径，如果取消则为None
        """
        directory = QFileDialog.getExistingDirectory(self, title, default_dir)
        return directory if directory else None
    
    def get_file_selection(self, title, default_dir, filter_str):
        """
        获取用户选择的文件
        
        Args:
            title: 对话框标题
            default_dir: 默认目录
            filter_str: 文件过滤器
            
        Returns:
            str: 选择的文件路径，如果取消则为None
        """
        file_path, _ = QFileDialog.getOpenFileName(self, title, default_dir, filter_str)
        return file_path if file_path else None
    
    def get_text_input(self, title, label, default_text=""):
        """
        获取用户文本输入
        
        Args:
            title: 对话框标题
            label: 标签文本
            default_text: 默认文本
            
        Returns:
            str: 输入的文本，如果取消则为None
        """
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, title, label, text=default_text)
        return text if ok else None
    
    def get_yes_no(self, title, message):
        """
        获取用户是/否选择
        
        Args:
            title: 对话框标题
            message: 消息文本
            
        Returns:
            bool: 用户是否选择"是"
        """
        reply = QMessageBox.question(self, title, message,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes
    
    def show_message(self, title, message):
        """
        显示消息对话框
        
        Args:
            title: 对话框标题
            message: 消息文本
        """
        QMessageBox.information(self, title, message)
    
    def generate_key(self):
        """生成新密钥"""
        self.generate_key_requested.emit()
    
    def import_key(self):
        """导入密钥"""
        self.import_key_requested.emit()
    
    def export_key(self):
        """导出选中的密钥"""
        selected_items = self.key_tree.selectedItems()
        if not selected_items:
            return
            
        key_name = selected_items[0].text(0)
        self.export_key_requested.emit(key_name)
    
    def delete_key(self):
        """删除选中的密钥"""
        selected_items = self.key_tree.selectedItems()
        if not selected_items:
            return
            
        key_name = selected_items[0].text(0)
        self.delete_key_requested.emit(key_name)
    
    def on_monitor_selection_changed(self):
        """处理监控任务选择变化"""
        items = self.monitor_tree.selectedItems()
        has_selection = len(items) > 0
        
        self.edit_monitor_btn.setEnabled(has_selection)
        self.delete_monitor_btn.setEnabled(has_selection)
        
        if has_selection:
            item = items[0]
            task_id = item.text(0)
            
            # 从控制器获取任务详情
            task_detail = self.controller.get_monitor_task_detail(task_id)
            if task_detail:
                # 构建详细信息文本
                detail_text = f"<b>监控目录:</b> {task_detail['directory']}<br>"
                detail_text += f"<b>递归子目录:</b> {'是' if task_detail['recursive'] else '否'}<br>"
                
                if 'patterns' in task_detail and task_detail['patterns']:
                    detail_text += f"<b>包含模式:</b> {', '.join(task_detail['patterns'])}<br>"
                
                if 'ignore_patterns' in task_detail and task_detail['ignore_patterns']:
                    detail_text += f"<b>排除模式:</b> {', '.join(task_detail['ignore_patterns'])}<br>"
                
                detail_text += f"<b>自动处理:</b> {'是' if task_detail['auto_process'] else '否'}<br>"
                
                if task_detail['auto_process']:
                    detail_text += f"<b>处理类型:</b> {task_detail.get('process_type', '')}<br>"
                    detail_text += f"<b>使用密钥:</b> {task_detail.get('key_name', '')}<br>"
                    detail_text += f"<b>输出目录:</b> {task_detail.get('output_dir', '')}<br>"
                    detail_text += f"<b>删除原文件:</b> {'是' if task_detail.get('delete_original', False) else '否'}<br>"
                
                self.monitor_detail.setText(detail_text)
            else:
                self.monitor_detail.setText("无法获取任务详情")
        else:
            self.monitor_detail.setText("选择一个监控任务查看详细信息")
    
    def add_monitor_task(self):
        """添加新的监控任务"""
        from .qt_dialogs import MonitorConfigDialog
        
        # 创建配置对话框
        dialog = MonitorConfigDialog(self)
        
        # 获取可用密钥列表
        keys = self.controller.get_key_list()
        dialog.set_keys(keys)
        
        # 显示对话框
        if dialog.exec_():
            # 获取配置
            config = dialog.get_config()
            if config:
                # 添加监控任务
                self.controller.add_monitor_task(config)
                
                # 刷新任务列表
                self.refresh_monitor_tasks()
    
    def edit_monitor_task(self):
        """编辑已有的监控任务"""
        items = self.monitor_tree.selectedItems()
        if not items:
            return
            
        task_id = items[0].text(0)
        
        # 获取任务详情
        task_detail = self.controller.get_monitor_task_detail(task_id)
        if not task_detail:
            self.show_message("错误", "无法获取任务详情")
            return
        
        from .qt_dialogs import MonitorConfigDialog
        
        # 创建配置对话框
        dialog = MonitorConfigDialog(self, task_detail)
        
        # 获取可用密钥列表
        keys = self.controller.get_key_list()
        dialog.set_keys(keys)
        
        # 显示对话框
        if dialog.exec_():
            # 获取配置
            config = dialog.get_config()
            if config:
                # 更新任务
                self.controller.update_monitor_task(task_id, config)
                
                # 刷新任务列表
                self.refresh_monitor_tasks()
    
    def delete_monitor_task(self):
        """删除监控任务"""
        items = self.monitor_tree.selectedItems()
        if not items:
            return
            
        task_id = items[0].text(0)
        
        # 确认删除
        if self.get_yes_no("确认删除", f"确定要删除监控任务 {task_id} 吗？"):
            # 删除任务
            self.controller.delete_monitor_task(task_id)
            
            # 刷新任务列表
            self.refresh_monitor_tasks()
    
    def refresh_monitor_tasks(self):
        """刷新监控任务列表"""
        # 清空列表
        self.monitor_tree.clear()
        
        # 获取任务列表
        tasks = self.controller.get_monitor_tasks()
        
        # 填充列表
        for task in tasks:
            item = QTreeWidgetItem([
                task['id'],
                task['directory'],
                "是" if task['auto_process'] else "否",
                "运行中"
            ])
            self.monitor_tree.addTopLevelItem(item)
        
        # 调整列宽
        self.monitor_tree.resizeColumnToContents(0)
        self.monitor_tree.resizeColumnToContents(2)
        self.monitor_tree.resizeColumnToContents(3)
    
    def updateStatusBarMessage(self, message: str, timeout: int = 0):
        """
        更新状态栏消息

        Args:
            message (str): 显示的消息
            timeout (int, optional): 消息显示的超时时间，单位为毫秒。默认为0（不超时）。
        """
        # 获取状态栏实例
        status_bar = self.statusBar()
        
        # 清除原有消息
        status_bar.clearMessage()
        
        # 查找并更新主状态标签
        main_label = status_bar.findChild(QLabel, "status_main_label")
        if main_label:
            main_label.setText(message)
        
        # 移除所有临时小部件
        for widget in status_bar.findChildren(QLabel):
            if widget != main_label and widget.objectName().startswith("temp_"):
                widget.deleteLater()
        
        # 显示新消息
        if timeout > 0:
            status_bar.showMessage(message, timeout)
        else:
            status_bar.showMessage(message) 