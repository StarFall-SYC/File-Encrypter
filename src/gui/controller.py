#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
控制器模块 - 连接GUI与底层功能
"""

import os
import sys
import time
import random
import string
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSlot, QSettings, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

from .qt_threads import EncryptionWorker, DecryptionWorker, KeyGenerationWorker
from .qt_dialogs import PasswordDialog, KeyGenerateDialog, ProgressDialog
from ..crypto.key_manager import key_manager
from ..crypto.crypto_base import CryptoBase
from ..crypto.crypto_factory import crypto_factory
from ..utils.logger import logger
from ..utils.file_monitor import file_monitor
from ..utils.batch_processor import batch_processor
from ..config.app_settings import settings
from ..utils.theme_manager import theme_manager
from ..utils.translator import translator
from ..utils.app_updater import app_updater

class Controller(QObject):
    """控制器类，协调GUI操作与核心加密/解密功能"""
    
    def __init__(self, parent=None):
        """初始化控制器"""
        super().__init__(parent)
        self.main_window = None
        self.settings = QSettings("FileEncrypter", "FileEncrypter")
        self.current_worker = None
        self.progress_dialog = None
        self.monitor_tasks = {}
        
        # 加载设置
        self._load_settings()
        
        # 初始化翻译器
        self._init_translator()
        
        # 初始化主题
        self._init_theme()
        
        # 线程和工作器
        self.encrypt_thread = None
        self.decrypt_thread = None
        self.key_thread = None
        self.worker = None
    
    def set_main_window(self, main_window):
        """设置主窗口引用"""
        self.main_window = main_window
        
        # 连接信号
        if self.main_window:
            # 文件操作信号
            self.main_window.encrypt_files_requested.connect(self.encrypt_files)
            self.main_window.decrypt_files_requested.connect(self.decrypt_files)
            
            # 密钥管理信号
            self.main_window.generate_key_requested.connect(self.generate_key)
            self.main_window.import_key_requested.connect(self.import_key)
            self.main_window.export_key_requested.connect(self.export_key)
            self.main_window.delete_key_requested.connect(self.delete_key)
    
    def _load_settings(self):
        """加载应用设置"""
        # 加载应用设置
        settings.save_all()  # 确保设置已保存
        logger.info("已加载应用程序设置")
        
        # 从QSettings中加载UI设置
        self.last_dir = self.settings.value("last_directory", "")
        self.dark_mode = self.settings.value("dark_mode", False, type=bool)
        self.verify_encryptions = self.settings.value("verify_encryptions", True, type=bool)
    
    def _save_settings(self):
        """保存应用设置"""
        # 将设置保存到QSettings
        self.settings.setValue("last_directory", self.last_dir)
        self.settings.setValue("dark_mode", self.dark_mode)
        self.settings.setValue("verify_encryptions", self.verify_encryptions)
        self.settings.sync()
    
    def update_last_dir(self, directory):
        """更新上次使用的目录"""
        if directory and os.path.isdir(directory):
            self.last_dir = directory
            self.settings.setValue("last_directory", self.last_dir)
    
    @pyqtSlot(list, bool)
    def encrypt_files(self, file_paths, delete_original=False):
        """
        加密文件
        
        Args:
            file_paths: 要加密的文件路径列表
            delete_original: 加密后是否删除原文件
        """
        if not file_paths:
            return
            
        # 更新上次使用的目录
        if os.path.isdir(file_paths[0]):
            self.update_last_dir(file_paths[0])
        else:
            self.update_last_dir(os.path.dirname(file_paths[0]))
        
        # 选择密钥
        keys = key_manager.list_keys()
        if not keys:
            self.main_window.show_message("错误", "没有可用的加密密钥。请先生成或导入密钥。")
            return
            
        # 获取选择的密钥
        key_name = self.main_window.get_key_selection(keys)
        if not key_name:
            return
            
        # 尝试加载密钥
        try:
            key_info = next((k for k in keys if k['name'] == key_name), None)
            if not key_info:
                self.main_window.show_message("错误", f"找不到名为 {key_name} 的密钥。")
                return
                
            password = None
            # 如果密钥受密码保护，获取密码
            if key_info.get('protected', False):
                password_dialog = PasswordDialog(self.main_window, "请输入密钥密码", confirm_password=False)
                if password_dialog.exec_():
                    password = password_dialog.get_password()
                else:
                    return
            
            # 加载密钥
            key_data = key_manager.load_key(key_name, password)
            
            # 获取输出目录
            output_dir = self.main_window.get_directory_selection("选择加密文件输出目录", 
                                                                 self.last_dir)
            if not output_dir:
                # 用户取消了选择
                return
                
            # 更新上次使用的目录
            self.update_last_dir(output_dir)
            
            # 创建进度对话框
            self.progress_dialog = ProgressDialog(self.main_window, "加密进度")
            
            # 创建工作线程
            self.current_worker = EncryptionWorker(
                files=file_paths,
                output_dir=output_dir,
                algorithm=key_info['algorithm'],
                key=key_data,
                delete_original=delete_original,
                verify=self.verify_encryptions
            )
            
            # 连接信号
            self.current_worker.signals.started.connect(self.progress_dialog.show)
            self.current_worker.signals.finished.connect(self._on_encryption_finished)
            self.current_worker.signals.error.connect(self._on_worker_error)
            self.current_worker.signals.progress.connect(self.progress_dialog.update_progress)
            
            # 连接取消信号
            self.progress_dialog.cancel_requested.connect(self.current_worker.stop)
            
            # 启动工作线程
            self.current_worker.start()
                
        except Exception as e:
            logger.error(f"加密错误: {str(e)}")
            self.main_window.show_message("加密错误", str(e))
    
    @pyqtSlot()
    def _on_encryption_finished(self):
        """加密完成时的处理"""
        # 清理
        self.current_worker.signals.started.disconnect(self.progress_dialog.show)
        self.current_worker.signals.finished.disconnect(self._on_encryption_finished)
        self.current_worker.signals.error.disconnect(self._on_worker_error)
        self.current_worker.signals.progress.disconnect(self.progress_dialog.update_progress)
        
        # 关闭进度对话框
        self.progress_dialog.accept()
        self.progress_dialog = None
        
        # 等待线程结束
        self.current_worker.wait()
        self.current_worker = None
        
        # 显示成功消息
        self.main_window.show_message("加密完成", "文件加密完成！")
    
    @pyqtSlot(list, bool)
    def decrypt_files(self, file_paths, delete_original=False):
        """
        解密文件
        
        Args:
            file_paths: 要解密的文件路径列表
            delete_original: 解密后是否删除原文件
        """
        if not file_paths:
            return
            
        # 更新上次使用的目录
        if os.path.isdir(file_paths[0]):
            self.update_last_dir(file_paths[0])
        else:
            self.update_last_dir(os.path.dirname(file_paths[0]))
        
        # 选择密钥
        keys = key_manager.list_keys()
        if not keys:
            self.main_window.show_message("错误", "没有可用的解密密钥。请先导入密钥。")
            return
            
        # 获取选择的密钥
        key_name = self.main_window.get_key_selection(keys)
        if not key_name:
            return
            
        # 尝试加载密钥
        try:
            key_info = next((k for k in keys if k['name'] == key_name), None)
            if not key_info:
                self.main_window.show_message("错误", f"找不到名为 {key_name} 的密钥。")
                return
                
            password = None
            # 如果密钥受密码保护，获取密码
            if key_info.get('protected', False):
                password_dialog = PasswordDialog(self.main_window, "请输入密钥密码", confirm_password=False)
                if password_dialog.exec_():
                    password = password_dialog.get_password()
                else:
                    return
            
            # 加载密钥
            key_data = key_manager.load_key(key_name, password)
            
            # 获取输出目录
            output_dir = self.main_window.get_directory_selection("选择解密文件输出目录", 
                                                                 self.last_dir)
            if not output_dir:
                # 用户取消了选择
                return
                
            # 更新上次使用的目录
            self.update_last_dir(output_dir)
            
            # 创建进度对话框
            self.progress_dialog = ProgressDialog(self.main_window, "解密进度")
            
            # 创建工作线程
            self.current_worker = DecryptionWorker(
                files=file_paths,
                output_dir=output_dir,
                key=key_data,
                delete_original=delete_original
            )
            
            # 连接信号
            self.current_worker.signals.started.connect(self.progress_dialog.show)
            self.current_worker.signals.finished.connect(self._on_decryption_finished)
            self.current_worker.signals.error.connect(self._on_worker_error)
            self.current_worker.signals.progress.connect(self.progress_dialog.update_progress)
            
            # 连接取消信号
            self.progress_dialog.cancel_requested.connect(self.current_worker.stop)
            
            # 启动工作线程
            self.current_worker.start()
                
        except Exception as e:
            logger.error(f"解密错误: {str(e)}")
            self.main_window.show_message("解密错误", str(e))
    
    @pyqtSlot()
    def _on_decryption_finished(self):
        """解密完成时的处理"""
        # 清理
        self.current_worker.signals.started.disconnect(self.progress_dialog.show)
        self.current_worker.signals.finished.disconnect(self._on_decryption_finished)
        self.current_worker.signals.error.disconnect(self._on_worker_error)
        self.current_worker.signals.progress.disconnect(self.progress_dialog.update_progress)
        
        # 关闭进度对话框
        self.progress_dialog.accept()
        self.progress_dialog = None
        
        # 等待线程结束
        self.current_worker.wait()
        self.current_worker = None
        
        # 显示成功消息
        self.main_window.show_message("解密完成", "文件解密完成！")
    
    @pyqtSlot(str)
    def _on_worker_error(self, error_message):
        """处理工作线程错误"""
        logger.error(f"工作线程错误: {error_message}")
        self.main_window.show_message("错误", error_message)
    
    @pyqtSlot()
    def generate_key(self):
        """生成新密钥"""
        dialog = KeyGenerateDialog(self.main_window)
        if dialog.exec_():
            key_type = dialog.get_key_type()
            algorithm = dialog.get_algorithm()
            name = dialog.get_key_name()
            password = dialog.get_password() if dialog.use_password() else None
            
            # 创建进度对话框
            self.progress_dialog = ProgressDialog(self.main_window, "密钥生成进度")
            
            # 创建工作线程
            self.current_worker = KeyGenerationWorker(
                key_type=key_type,
                algorithm=algorithm,
                name=name,
                password=password
            )
            
            # 连接信号
            self.current_worker.signals.started.connect(self.progress_dialog.show)
            self.current_worker.signals.finished.connect(self._on_key_generation_finished)
            self.current_worker.signals.error.connect(self._on_worker_error)
            self.current_worker.signals.progress.connect(self.progress_dialog.update_progress)
            
            # 启动工作线程
            self.current_worker.start()
    
    @pyqtSlot()
    def _on_key_generation_finished(self):
        """密钥生成完成时的处理"""
        # 清理
        self.current_worker.signals.started.disconnect(self.progress_dialog.show)
        self.current_worker.signals.finished.disconnect(self._on_key_generation_finished)
        self.current_worker.signals.error.disconnect(self._on_worker_error)
        self.current_worker.signals.progress.disconnect(self.progress_dialog.update_progress)
        
        # 关闭进度对话框
        self.progress_dialog.accept()
        self.progress_dialog = None
        
        # 等待线程结束
        self.current_worker.wait()
        self.current_worker = None
        
        # 刷新密钥列表
        self.main_window.refresh_key_list()
        
        # 显示成功消息
        self.main_window.show_message("密钥生成", "密钥生成成功！")
    
    @pyqtSlot()
    def import_key(self):
        """导入密钥"""
        # 选择密钥文件
        key_file = self.main_window.get_file_selection("选择要导入的密钥文件",
                                                       self.last_dir,
                                                       "密钥文件 (*.key)")
        if not key_file:
            return
            
        # 获取密钥名称
        key_name = os.path.splitext(os.path.basename(key_file))[0]
        custom_name = self.main_window.get_text_input("密钥名称", "请输入密钥名称:", key_name)
        if not custom_name:
            return
            
        # 询问是否需要密码
        password = None
        if self.main_window.get_yes_no("密钥密码", "密钥是否受密码保护?"):
            password_dialog = PasswordDialog(self.main_window, "请输入密钥密码", confirm_password=False)
            if password_dialog.exec_():
                password = password_dialog.get_password()
            else:
                return
        
        try:
            # 读取密钥文件
            with open(key_file, 'rb') as f:
                key_data = f.read()
            
            # 导入密钥
            key_manager.import_key(custom_name, key_data, password)
            
            # 刷新密钥列表
            self.main_window.refresh_key_list()
            
            self.main_window.show_message("密钥导入", f"密钥 '{custom_name}' 导入成功！")
            
        except Exception as e:
            logger.error(f"密钥导入错误: {str(e)}")
            self.main_window.show_message("密钥导入错误", str(e))
    
    @pyqtSlot(str)
    def export_key(self, key_name):
        """
        导出密钥
        
        Args:
            key_name: 要导出的密钥名称
        """
        if not key_name:
            return
            
        # 获取密钥信息
        keys = key_manager.list_keys()
        key_info = next((k for k in keys if k['name'] == key_name), None)
        if not key_info:
            self.main_window.show_message("错误", f"找不到名为 {key_name} 的密钥。")
            return
            
        # 如果密钥受密码保护，获取密码
        password = None
        if key_info.get('protected', False):
            password_dialog = PasswordDialog(self.main_window, "请输入密钥密码", confirm_password=False)
            if password_dialog.exec_():
                password = password_dialog.get_password()
            else:
                return
                
        # 选择导出目录
        export_dir = self.main_window.get_directory_selection("选择密钥导出目录", 
                                                            self.last_dir)
        if not export_dir:
            return
            
        # 更新上次使用的目录
        self.update_last_dir(export_dir)
        
        try:
            # 加载密钥
            key_data = key_manager.load_key(key_name, password)
            
            # 导出密钥
            export_path = os.path.join(export_dir, f"{key_name}.key")
            with open(export_path, 'wb') as f:
                f.write(key_data)
                
            self.main_window.show_message("密钥导出", f"密钥 '{key_name}' 导出到 {export_path} 成功！")
            
        except Exception as e:
            logger.error(f"密钥导出错误: {str(e)}")
            self.main_window.show_message("密钥导出错误", str(e))
    
    @pyqtSlot(str)
    def delete_key(self, key_name):
        """
        删除密钥
        
        Args:
            key_name: 要删除的密钥名称
        """
        if not key_name:
            return
            
        # 确认删除
        if not self.main_window.get_yes_no("确认删除", 
                                          f"确定要删除密钥 '{key_name}'? 此操作不可恢复！"):
            return
            
        try:
            # 删除密钥
            key_manager.delete_key(key_name)
            
            # 刷新密钥列表
            self.main_window.refresh_key_list()
            
            self.main_window.show_message("密钥删除", f"密钥 '{key_name}' 已删除！")
            
        except Exception as e:
            logger.error(f"密钥删除错误: {str(e)}")
            self.main_window.show_message("密钥删除错误", str(e))
    
    def close(self):
        """关闭控制器，保存设置"""
        self._save_settings()
        
        # 停止所有工作线程
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.current_worker.wait()
        
        # 关闭所有对话框
        if self.progress_dialog:
            self.progress_dialog.accept()
            self.progress_dialog = None

    def get_key_list(self):
        """获取可用密钥列表"""
        return key_manager.list_keys()
    
    def add_monitor_task(self, config):
        """
        添加文件监控任务
        
        Args:
            config: 监控配置
        """
        directory = config.get('directory')
        recursive = config.get('recursive', True)
        auto_process = config.get('auto_process', False)
        patterns = config.get('patterns')
        ignore_patterns = config.get('ignore_patterns')
        
        # 创建处理函数
        process_handler = None
        if auto_process:
            process_type = config.get('process_type')
            key_name = config.get('key_name')
            output_dir = config.get('output_dir')
            delete_original = config.get('delete_original', False)
            
            # 创建处理函数
            process_handler = lambda event_type, file_path: self._handle_monitored_file(
                event_type, file_path, process_type, key_name, output_dir, delete_original
            )
        
        # 启动监控
        monitor_id = file_monitor.start_monitoring(
            directory=directory,
            patterns=patterns,
            ignore_patterns=ignore_patterns,
            recursive=recursive,
            auto_process=auto_process,
            process_handler=process_handler
        )
        
        # 保存任务配置
        self.monitor_tasks[monitor_id] = {
            'directory': directory,
            'recursive': recursive,
            'auto_process': auto_process,
            'patterns': patterns,
            'ignore_patterns': ignore_patterns
        }
        
        # 如果有自动处理，保存处理配置
        if auto_process:
            self.monitor_tasks[monitor_id].update({
                'process_type': config.get('process_type'),
                'key_name': config.get('key_name'),
                'output_dir': config.get('output_dir'),
                'delete_original': config.get('delete_original', False)
            })
        
        logger.info(f"添加监控任务: {monitor_id}, 目录: {directory}")
        
        return monitor_id
    
    def update_monitor_task(self, task_id, config):
        """
        更新文件监控任务
        
        Args:
            task_id: 任务ID
            config: 新的监控配置
        """
        # 先停止现有监控
        file_monitor.stop_monitoring(task_id)
        
        # 移除配置
        if task_id in self.monitor_tasks:
            del self.monitor_tasks[task_id]
        
        # 添加新的监控
        self.add_monitor_task(config)
        
        logger.info(f"更新监控任务: {task_id}")
    
    def delete_monitor_task(self, task_id):
        """
        删除文件监控任务
        
        Args:
            task_id: 任务ID
        """
        # 停止监控
        file_monitor.stop_monitoring(task_id)
        
        # 移除配置
        if task_id in self.monitor_tasks:
            del self.monitor_tasks[task_id]
        
        logger.info(f"删除监控任务: {task_id}")
    
    def get_monitor_tasks(self):
        """
        获取所有监控任务
        
        Returns:
            List[Dict]: 监控任务列表
        """
        # 从文件监控器获取最新任务列表
        active_tasks = file_monitor.get_monitoring_tasks()
        
        # 合并任务信息
        result = []
        for task in active_tasks:
            task_id = task['id']
            task_info = self.monitor_tasks.get(task_id, {})
            
            # 合并信息
            task_info.update(task)
            result.append(task_info)
        
        return result
    
    def get_monitor_task_detail(self, task_id):
        """
        获取监控任务详情
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务详情
        """
        # 从文件监控器获取任务信息
        active_tasks = file_monitor.get_monitoring_tasks()
        active_task = next((t for t in active_tasks if t['id'] == task_id), None)
        
        if not active_task:
            return None
        
        # 合并详细信息
        task_info = self.monitor_tasks.get(task_id, {})
        task_info.update(active_task)
        
        return task_info
    
    def _handle_monitored_file(self, event_type, file_path, process_type, key_name, output_dir, delete_original):
        """
        处理被监控的文件
        
        Args:
            event_type: 事件类型 (created, modified, moved)
            file_path: 文件路径
            process_type: 处理类型 (加密文件, 解密文件)
            key_name: 密钥名称
            output_dir: 输出目录
            delete_original: 是否删除原文件
        """
        # 只处理新创建的文件
        if event_type != 'created':
            return
        
        # 确保文件存在
        if not os.path.isfile(file_path):
            return
        
        # 等待文件写入完成
        self._wait_for_file_ready(file_path)
        
        # 加载密钥
        keys = key_manager.list_keys()
        key_info = next((k for k in keys if k['name'] == key_name), None)
        
        if not key_info:
            logger.error(f"无法找到密钥: {key_name}")
            return
        
        try:
            # 加载密钥
            key_data = key_manager.load_key(key_name)
            
            # 根据处理类型执行操作
            if process_type == "加密文件":
                # 加密文件
                self._encrypt_monitored_file(file_path, key_info, key_data, output_dir, delete_original)
            elif process_type == "解密文件":
                # 解密文件
                self._decrypt_monitored_file(file_path, key_info, key_data, output_dir, delete_original)
                
        except Exception as e:
            logger.error(f"处理监控文件时出错: {str(e)}")
    
    def _wait_for_file_ready(self, file_path, timeout=5, check_interval=0.5):
        """
        等待文件写入完成
        
        Args:
            file_path: 文件路径
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            bool: 文件是否就绪
        """
        start_time = time.time()
        last_size = -1
        
        while time.time() - start_time < timeout:
            try:
                current_size = os.path.getsize(file_path)
                if current_size == last_size and current_size > 0:
                    # 文件大小稳定，认为写入完成
                    return True
                
                last_size = current_size
                time.sleep(check_interval)
                
            except Exception:
                # 文件可能被删除或其他错误
                time.sleep(check_interval)
                
        return False
    
    def _encrypt_monitored_file(self, file_path, key_info, key_data, output_dir, delete_original):
        """
        加密被监控的文件
        
        Args:
            file_path: 文件路径
            key_info: 密钥信息
            key_data: 密钥数据
            output_dir: 输出目录
            delete_original: 是否删除原文件
        """
        try:
            # 获取文件名
            file_name = os.path.basename(file_path)
            output_path = os.path.join(output_dir, f"{file_name}.enc")
            
            # 创建加密实例
            crypto = crypto_factory.get_crypto_by_name(key_info['algorithm'])
            
            if not crypto:
                logger.error(f"不支持的加密算法: {key_info['algorithm']}")
                return
            
            # 读取文件
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # 加密数据
            encrypted_data, meta = crypto.encrypt(data, key_data)
            
            # 写入加密文件
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"自动加密文件: {file_path} -> {output_path}")
            
            # 如果需要删除原文件
            if delete_original:
                try:
                    os.remove(file_path)
                    logger.info(f"删除原文件: {file_path}")
                except Exception as e:
                    logger.error(f"删除原文件失败: {str(e)}")
                    
        except Exception as e:
            logger.error(f"加密文件失败: {str(e)}")
    
    def _decrypt_monitored_file(self, file_path, key_info, key_data, output_dir, delete_original):
        """
        解密被监控的文件
        
        Args:
            file_path: 文件路径
            key_info: 密钥信息
            key_data: 密钥数据
            output_dir: 输出目录
            delete_original: 是否删除原文件
        """
        try:
            # 获取文件名并移除.enc扩展名
            file_name = os.path.basename(file_path)
            if file_name.endswith('.enc'):
                output_name = file_name[:-4]
            else:
                output_name = f"decrypted_{file_name}"
                
            output_path = os.path.join(output_dir, output_name)
            
            # 创建加密实例
            crypto = crypto_factory.get_crypto_by_name(key_info['algorithm'])
            
            if not crypto:
                logger.error(f"不支持的加密算法: {key_info['algorithm']}")
                return
            
            # 读取文件
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # 解密数据
            decrypted_data = crypto.decrypt(encrypted_data, key_data, {})
            
            # 写入解密文件
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"自动解密文件: {file_path} -> {output_path}")
            
            # 如果需要删除原文件
            if delete_original:
                try:
                    os.remove(file_path)
                    logger.info(f"删除原文件: {file_path}")
                except Exception as e:
                    logger.error(f"删除原文件失败: {str(e)}")
                    
        except Exception as e:
            logger.error(f"解密文件失败: {str(e)}")

    def _init_translator(self):
        """初始化翻译器"""
        # 获取界面语言设置
        language = settings.get("ui", "language", "zh_CN")
        
        # 切换到配置的语言
        translator.switch_language(language)
        logger.info(f"应用语言设置为: {language}")

    def _init_theme(self):
        """初始化应用主题"""
        # 获取主题设置
        theme_name = settings.get("ui", "theme", "light")
        
        # 注意：主题应用已在主程序中处理
        logger.info(f"应用主题设置为: {theme_name}")

# 创建全局控制器实例
controller = Controller() 