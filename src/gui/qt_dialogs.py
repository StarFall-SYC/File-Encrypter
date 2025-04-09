#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyQt5对话框模块
"""

import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QLineEdit, QFormLayout, QComboBox, QCheckBox, 
                           QGroupBox, QProgressBar, QTabWidget, QRadioButton,
                           QMessageBox, QFileDialog, QFrame, QWidget, QDialogButtonBox)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize

from ..crypto.crypto_factory import crypto_factory
from ..crypto.key_manager import key_manager
from ..utils.logger import logger

class PasswordDialog(QDialog):
    """密码输入对话框"""
    
    def __init__(self, parent=None, title="密码输入", prompt="请输入密码:", confirm=False):
        """
        初始化密码输入对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            prompt: 提示信息
            confirm: 是否需要确认密码
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setModal(True)
        
        self.prompt = prompt
        self.confirm = confirm
        self.password = None
        
        # 创建UI
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 添加图标和标题
        header_layout = QHBoxLayout()
        
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icon.png")
            if os.path.exists(icon_path):
                icon_label = QLabel()
                pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
                header_layout.addWidget(icon_label)
        except Exception as e:
            logger.warning(f"加载图标失败: {str(e)}")
        
        title_label = QLabel(self.prompt)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        
        layout.addLayout(header_layout)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 密码输入
        form_layout = QFormLayout()
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("密码:", self.password_edit)
        
        # 确认密码
        if self.confirm:
            self.confirm_edit = QLineEdit()
            self.confirm_edit.setEchoMode(QLineEdit.Password)
            form_layout.addRow("确认密码:", self.confirm_edit)
            
            # 密码强度提示
            hint_label = QLabel("密码提示: 使用字母、数字和特殊字符组合以提高安全性")
            hint_label.setStyleSheet("color: #757575; font-size: 9pt;")
            layout.addWidget(hint_label)
        
        layout.addLayout(form_layout)
        
        # 显示密码选项
        self.show_password_check = QCheckBox("显示密码")
        self.show_password_check.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_check)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        ok_button = QPushButton("确认")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
    
    def toggle_password_visibility(self, checked):
        """切换密码显示/隐藏状态"""
        echo_mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.password_edit.setEchoMode(echo_mode)
        if self.confirm and hasattr(self, 'confirm_edit'):
            self.confirm_edit.setEchoMode(echo_mode)
    
    def accept(self):
        """确认按钮点击事件"""
        password = self.password_edit.text()
        
        if not password:
            QMessageBox.warning(self, "错误", "密码不能为空")
            return
        
        if self.confirm:
            confirm_password = self.confirm_edit.text()
            if password != confirm_password:
                QMessageBox.warning(self, "错误", "两次输入的密码不一致")
                return
        
        self.password = password
        super().accept()

class KeyGenerateDialog(QDialog):
    """密钥生成对话框"""
    
    def __init__(self, parent=None, title="生成新密钥"):
        """
        初始化密钥生成对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setModal(True)
        
        self.key_params = {}
        self.algorithms = crypto_factory.get_algorithm_by_category()
        
        # 创建UI
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 添加图标和标题
        header_layout = QHBoxLayout()
        
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icon.png")
            if os.path.exists(icon_path):
                icon_label = QLabel()
                pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
                header_layout.addWidget(icon_label)
        except Exception as e:
            logger.warning(f"加载图标失败: {str(e)}")
        
        title_label = QLabel("生成新密钥")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        
        layout.addLayout(header_layout)
        
        # 添加描述
        description = QLabel("请输入密钥信息以创建新密钥。\n密钥名称应当能够帮助您识别其用途。")
        layout.addWidget(description)
        
        # 密钥名称
        form_layout = QFormLayout()
        
        import time
        import random
        default_key_name = f"key_{int(time.time())}_{random.randint(1000, 9999)}"
        
        self.name_edit = QLineEdit(default_key_name)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.name_edit)
        
        random_button = QPushButton("随机")
        random_button.clicked.connect(self.generate_random_name)
        name_layout.addWidget(random_button)
        
        form_layout.addRow("密钥名称:", name_layout)
        
        layout.addLayout(form_layout)
        
        # 创建选项卡控件
        tab_widget = QTabWidget()
        
        # 对称加密选项卡
        symmetric_tab = QWidget()
        symmetric_layout = QVBoxLayout(symmetric_tab)
        
        symmetric_info = QLabel("对称加密使用相同的密钥进行加密和解密，适合大文件加密")
        symmetric_info.setStyleSheet("color: #757575; font-size: 9pt;")
        symmetric_layout.addWidget(symmetric_info)
        
        self.symmetric_algo_combo = QComboBox()
        if "对称加密" in self.algorithms:
            self.symmetric_algo_combo.addItems(self.algorithms["对称加密"])
        
        symmetric_layout.addWidget(QLabel("选择算法:"))
        symmetric_layout.addWidget(self.symmetric_algo_combo)
        symmetric_layout.addStretch(1)
        
        tab_widget.addTab(symmetric_tab, "对称加密")
        
        # 非对称加密选项卡
        asymmetric_tab = QWidget()
        asymmetric_layout = QVBoxLayout(asymmetric_tab)
        
        asymmetric_info = QLabel("非对称加密使用公钥加密和私钥解密，适合安全密钥交换")
        asymmetric_info.setStyleSheet("color: #757575; font-size: 9pt;")
        asymmetric_layout.addWidget(asymmetric_info)
        
        self.asymmetric_algo_combo = QComboBox()
        if "非对称加密" in self.algorithms:
            self.asymmetric_algo_combo.addItems(self.algorithms["非对称加密"])
        
        asymmetric_layout.addWidget(QLabel("选择算法:"))
        asymmetric_layout.addWidget(self.asymmetric_algo_combo)
        
        key_length_info = QLabel("注意：密钥长度越大越安全，但加密解密速度越慢")
        key_length_info.setStyleSheet("color: #757575; font-size: 9pt;")
        asymmetric_layout.addWidget(key_length_info)
        
        asymmetric_layout.addStretch(1)
        
        tab_widget.addTab(asymmetric_tab, "非对称加密")
        
        layout.addWidget(tab_widget)
        
        # 密码保护选项
        protection_group = QGroupBox("安全选项")
        protection_layout = QVBoxLayout(protection_group)
        
        self.password_protect = QCheckBox("使用密码保护密钥")
        protection_layout.addWidget(self.password_protect)
        
        protection_info = QLabel("密码保护可以防止未授权访问您的密钥")
        protection_info.setStyleSheet("color: #757575; font-size: 9pt;")
        protection_layout.addWidget(protection_info)
        
        layout.addWidget(protection_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        generate_button = QPushButton("生成密钥")
        generate_button.setDefault(True)
        generate_button.clicked.connect(self.accept)
        button_layout.addWidget(generate_button)
        
        layout.addLayout(button_layout)
        
        # 保存tab索引
        self.tab_widget = tab_widget
    
    def generate_random_name(self):
        """生成随机密钥名称"""
        import time
        import random
        name = f"key_{int(time.time())}_{random.randint(1000, 9999)}"
        self.name_edit.setText(name)
    
    def accept(self):
        """确认按钮点击事件"""
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "错误", "密钥名称不能为空")
            return
        
        # 确定当前选中的选项卡和算法
        current_tab = self.tab_widget.currentIndex()
        
        # 根据当前选项卡获取选定的算法
        if current_tab == 0:  # 对称加密
            key_type = "symmetric"
            algorithm = self.symmetric_algo_combo.currentText()
        else:  # 非对称加密
            key_type = "asymmetric"
            algorithm = self.asymmetric_algo_combo.currentText()
        
        if not algorithm:
            QMessageBox.warning(self, "错误", "请选择加密算法")
            return
        
        # 如果启用密码保护，获取密码
        if self.password_protect.isChecked():
            password_dialog = PasswordDialog(self, prompt="请输入密钥保护密码:", confirm=True)
            if password_dialog.exec_() != QDialog.Accepted or not password_dialog.password:
                return
            self.key_params["password"] = password_dialog.password
        
        self.key_params["name"] = name
        self.key_params["key_type"] = key_type
        self.key_params["algorithm"] = algorithm
        
        super().accept()

    def get_key_type(self):
        """获取密钥类型"""
        return self.key_params.get("key_type", "")
    
    def get_algorithm(self):
        """获取选定的算法"""
        return self.key_params.get("algorithm", "")
    
    def get_key_name(self):
        """获取密钥名称"""
        return self.key_params.get("name", "")
    
    def use_password(self):
        """是否使用密码保护"""
        return "password" in self.key_params
    
    def get_password(self):
        """获取密码"""
        return self.key_params.get("password", "")

class ProgressDialog(QDialog):
    """进度对话框"""
    
    # 定义信号
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None, title="处理中", message="请稍候...", cancelable=True):
        """
        初始化进度对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 提示消息
            cancelable: 是否可取消
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setModal(True)
        
        self.message = message
        self.cancelable = cancelable
        self.cancelled = False
        
        # 创建UI
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 尝试添加图标
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icon.png")
            if os.path.exists(icon_path):
                icon_label = QLabel()
                pixmap = QPixmap(icon_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
                icon_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(icon_label)
        except Exception as e:
            logger.warning(f"加载图标失败: {str(e)}")
        
        # 标题标签
        title_label = QLabel(self.windowTitle())
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # 消息标签
        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 详细信息标签
        self.detail_label = QLabel("初始化...")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setStyleSheet("color: #757575;")
        layout.addWidget(self.detail_label)
        
        # 如果可取消，添加取消按钮
        if self.cancelable:
            self.cancel_button = QPushButton("取消操作")
            self.cancel_button.clicked.connect(self.cancel_operation)
            layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)
    
    def set_progress(self, value, message=None):
        """
        设置进度值和消息
        
        Args:
            value: 进度值 (0-100)
            message: 进度消息
        """
        self.progress_bar.setValue(int(value))
        
        if message:
            self.detail_label.setText(message)
    
    def update_progress(self, value, message=None):
        """
        更新进度条
        
        Args:
            value: 进度值（0-100）
            message: 可选的消息文本
        """
        self.progress_bar.setValue(value)
        if message:
            self.detail_label.setText(message)
    
    def cancel_operation(self):
        """取消操作"""
        from PyQt5.QtWidgets import QMessageBox
        
        # 确认取消
        reply = QMessageBox.question(self, "确认取消", "确定要取消当前操作吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.cancelled = True
            self.cancel_requested.emit()
            self.cancel_button.setEnabled(False)
            self.detail_label.setText("正在取消操作...")
            self.progress_bar.setRange(0, 0)  # 切换为不确定模式 

class MonitorConfigDialog(QDialog):
    """监控配置对话框，用于设置自动监控和处理功能"""
    
    def __init__(self, parent=None, monitor_info=None):
        """
        初始化监控配置对话框
        
        Args:
            parent: 父窗口
            monitor_info: 现有监控配置信息，用于编辑现有监控
        """
        super().__init__(parent)
        self.setWindowTitle("文件监控配置")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.monitor_info = monitor_info or {}
        
        # 创建UI
        self.create_ui()
        
        # 如果是编辑现有监控，填充数据
        if monitor_info:
            self.fill_data()
    
    def create_ui(self):
        """创建对话框UI"""
        layout = QVBoxLayout(self)
        
        # 监控目录组
        directory_group = QGroupBox("监控目录")
        directory_layout = QHBoxLayout(directory_group)
        
        self.directory_edit = QLineEdit()
        self.directory_edit.setReadOnly(True)
        directory_layout.addWidget(self.directory_edit)
        
        self.select_dir_btn = QPushButton("选择目录")
        self.select_dir_btn.clicked.connect(self.select_directory)
        directory_layout.addWidget(self.select_dir_btn)
        
        layout.addWidget(directory_group)
        
        # 监控设置组
        monitor_group = QGroupBox("监控设置")
        monitor_layout = QVBoxLayout(monitor_group)
        
        # 递归子目录
        self.recursive_cb = QCheckBox("递归监控子目录")
        self.recursive_cb.setChecked(True)
        monitor_layout.addWidget(self.recursive_cb)
        
        # 自动处理
        self.auto_process_cb = QCheckBox("自动处理新文件")
        self.auto_process_cb.setChecked(False)
        self.auto_process_cb.stateChanged.connect(self.toggle_auto_process)
        monitor_layout.addWidget(self.auto_process_cb)
        
        layout.addWidget(monitor_group)
        
        # 文件过滤组
        filter_group = QGroupBox("文件过滤")
        filter_layout = QVBoxLayout(filter_group)
        
        # 文件模式说明
        filter_note = QLabel("文件模式支持通配符，多个模式请用英文分号(;)分隔")
        filter_note.setWordWrap(True)
        filter_layout.addWidget(filter_note)
        
        # 包含模式
        include_layout = QHBoxLayout()
        include_layout.addWidget(QLabel("包含模式:"))
        self.include_edit = QLineEdit()
        self.include_edit.setPlaceholderText("例如: *.txt;*.doc;*.pdf")
        include_layout.addWidget(self.include_edit)
        filter_layout.addLayout(include_layout)
        
        # 排除模式
        exclude_layout = QHBoxLayout()
        exclude_layout.addWidget(QLabel("排除模式:"))
        self.exclude_edit = QLineEdit()
        self.exclude_edit.setPlaceholderText("例如: *.tmp;~*;.git*")
        exclude_layout.addWidget(self.exclude_edit)
        filter_layout.addLayout(exclude_layout)
        
        layout.addWidget(filter_group)
        
        # 自动处理设置
        self.auto_process_group = QGroupBox("自动处理设置")
        auto_process_layout = QVBoxLayout(self.auto_process_group)
        
        # 处理类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("处理类型:"))
        self.process_type_combo = QComboBox()
        self.process_type_combo.addItems(["加密文件", "解密文件"])
        type_layout.addWidget(self.process_type_combo)
        auto_process_layout.addLayout(type_layout)
        
        # 加密密钥
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("使用密钥:"))
        self.key_combo = QComboBox()
        # 密钥列表将在显示对话框时填充
        key_layout.addWidget(self.key_combo)
        auto_process_layout.addLayout(key_layout)
        
        # 输出目录
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出目录:"))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_layout.addWidget(self.output_edit)
        
        self.select_output_btn = QPushButton("选择")
        self.select_output_btn.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.select_output_btn)
        auto_process_layout.addLayout(output_layout)
        
        # 删除原文件
        self.delete_original_cb = QCheckBox("处理后删除原文件")
        self.delete_original_cb.setChecked(False)
        auto_process_layout.addWidget(self.delete_original_cb)
        
        layout.addWidget(self.auto_process_group)
        self.auto_process_group.setVisible(False)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def toggle_auto_process(self, state):
        """切换自动处理设置的可见性"""
        self.auto_process_group.setVisible(state == Qt.Checked)
        
        # 调整对话框大小
        self.adjustSize()
    
    def select_directory(self):
        """选择要监控的目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择要监控的目录",
            os.path.expanduser("~")
        )
        
        if directory:
            self.directory_edit.setText(directory)
    
    def select_output_directory(self):
        """选择输出目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            os.path.expanduser("~")
        )
        
        if directory:
            self.output_edit.setText(directory)
    
    def fill_data(self):
        """填充现有监控数据"""
        if 'directory' in self.monitor_info:
            self.directory_edit.setText(self.monitor_info['directory'])
            
        if 'recursive' in self.monitor_info:
            self.recursive_cb.setChecked(self.monitor_info['recursive'])
            
        if 'auto_process' in self.monitor_info:
            self.auto_process_cb.setChecked(self.monitor_info['auto_process'])
            
        if 'patterns' in self.monitor_info and self.monitor_info['patterns']:
            self.include_edit.setText(';'.join(self.monitor_info['patterns']))
            
        if 'ignore_patterns' in self.monitor_info and self.monitor_info['ignore_patterns']:
            self.exclude_edit.setText(';'.join(self.monitor_info['ignore_patterns']))
            
        if 'process_type' in self.monitor_info:
            index = self.process_type_combo.findText(self.monitor_info['process_type'])
            if index >= 0:
                self.process_type_combo.setCurrentIndex(index)
                
        if 'key_name' in self.monitor_info:
            # 密钥将在显示时设置
            self.key_name = self.monitor_info['key_name']
            
        if 'output_dir' in self.monitor_info:
            self.output_edit.setText(self.monitor_info['output_dir'])
            
        if 'delete_original' in self.monitor_info:
            self.delete_original_cb.setChecked(self.monitor_info['delete_original'])
    
    def set_keys(self, keys):
        """设置可用的密钥列表"""
        self.key_combo.clear()
        
        for key in keys:
            self.key_combo.addItem(key['name'])
            
        # 如果是编辑现有监控，选择原来的密钥
        if hasattr(self, 'key_name') and self.key_name:
            index = self.key_combo.findText(self.key_name)
            if index >= 0:
                self.key_combo.setCurrentIndex(index)
    
    def get_config(self):
        """获取配置信息"""
        directory = self.directory_edit.text().strip()
        if not directory:
            QMessageBox.warning(self, "错误", "请选择要监控的目录")
            return None
            
        if self.auto_process_cb.isChecked():
            output_dir = self.output_edit.text().strip()
            if not output_dir:
                QMessageBox.warning(self, "错误", "请选择输出目录")
                return None
                
            if self.key_combo.count() == 0:
                QMessageBox.warning(self, "错误", "没有可用的密钥")
                return None
        
        # 构建配置
        config = {
            'directory': directory,
            'recursive': self.recursive_cb.isChecked(),
            'auto_process': self.auto_process_cb.isChecked()
        }
        
        # 处理文件模式
        include_text = self.include_edit.text().strip()
        if include_text:
            config['patterns'] = [p.strip() for p in include_text.split(';') if p.strip()]
            
        exclude_text = self.exclude_edit.text().strip()
        if exclude_text:
            config['ignore_patterns'] = [p.strip() for p in exclude_text.split(';') if p.strip()]
        
        # 自动处理设置
        if self.auto_process_cb.isChecked():
            config['process_type'] = self.process_type_combo.currentText()
            config['key_name'] = self.key_combo.currentText()
            config['output_dir'] = output_dir
            config['delete_original'] = self.delete_original_cb.isChecked()
        
        return config 