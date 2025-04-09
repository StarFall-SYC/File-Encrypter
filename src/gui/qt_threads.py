#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyQt5线程模块 - 用于处理耗时的后台任务
"""

import os
import time
import traceback
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt, QMutex

from ..utils.logger import logger
from ..crypto.crypto_factory import crypto_factory

class WorkerSignals(QObject):
    """
    定义线程工作信号
    """
    started = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)
    result = pyqtSignal(object)

class EncryptionWorker(QThread):
    """文件加密工作线程"""
    
    def __init__(self, files, output_dir, algorithm, key, delete_original=False, verify=False):
        """
        初始化加密工作线程
        
        Args:
            files: 要加密的文件列表
            output_dir: 输出目录（如果为None，则输出到原文件所在目录）
            algorithm: 加密算法
            key: 加密密钥
            delete_original: 是否删除原文件
            verify: 是否验证加密结果
        """
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.algorithm = algorithm
        self.key = key
        self.delete_original = delete_original
        self.verify = verify
        
        self.signals = WorkerSignals()
        self.mutex = QMutex()
        self.abort = False
    
    def stop(self):
        """停止工作线程"""
        self.mutex.lock()
        self.abort = True
        self.mutex.unlock()
    
    def run(self):
        """运行线程"""
        try:
            self.signals.started.emit()
            
            total_files = len(self.files)
            processed_files = 0
            
            # 获取加密算法实例
            crypto = crypto_factory.get_crypto_by_name(self.algorithm)
            if not crypto:
                raise ValueError(f"不支持的加密算法: {self.algorithm}")
            
            # 如果是文件夹，递归获取所有文件
            all_files = []
            for file_path in self.files:
                if os.path.isdir(file_path):
                    for root, _, files in os.walk(file_path):
                        for file in files:
                            all_files.append(os.path.join(root, file))
                else:
                    all_files.append(file_path)
            
            total_size = sum(os.path.getsize(f) for f in all_files if os.path.isfile(f))
            processed_size = 0
            
            # 处理每个文件
            for file_path in all_files:
                if not os.path.isfile(file_path):
                    continue
                
                # 检查是否取消
                self.mutex.lock()
                if self.abort:
                    self.mutex.unlock()
                    break
                self.mutex.unlock()
                
                # 确定输出文件路径
                if self.output_dir:
                    # 保持相对路径结构
                    rel_path = os.path.relpath(file_path, os.path.commonpath(self.files))
                    output_path = os.path.join(self.output_dir, rel_path + ".enc")
                    # 确保输出目录存在
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                else:
                    output_path = file_path + ".enc"
                
                file_size = os.path.getsize(file_path)
                file_name = os.path.basename(file_path)
                
                self.signals.progress.emit(
                    int(processed_size / total_size * 100) if total_size else 0,
                    f"正在加密 {file_name} ({processed_files+1}/{len(all_files)})"
                )
                
                # 执行加密
                try:
                    # 检查密钥是否是字典，如果是，获取实际的密钥和IV
                    if isinstance(self.key, dict):
                        key_bytes = self.key.get('key')
                        iv = self.key.get('iv')
                        crypto.encrypt_file(file_path, output_path, key_bytes, iv=iv)
                    else:
                        # 如果密钥不是字典，直接使用
                        crypto.encrypt_file(file_path, output_path, self.key)
                    
                    # 验证加密结果
                    if self.verify:
                        # 这里应该实现验证逻辑
                        pass
                    
                    # 删除原文件
                    if self.delete_original:
                        os.remove(file_path)
                    
                    processed_files += 1
                    processed_size += file_size
                    
                    self.signals.progress.emit(
                        int(processed_size / total_size * 100) if total_size else 0,
                        f"已完成 {file_name} ({processed_files}/{len(all_files)})"
                    )
                    
                except Exception as e:
                    logger.error(f"加密文件 {file_path} 失败: {str(e)}")
                    self.signals.error.emit(f"加密文件 {file_path} 失败: {str(e)}")
            
            self.signals.finished.emit()
            
        except Exception as e:
            logger.error(f"加密过程中发生错误: {str(e)}")
            logger.error(traceback.format_exc())
            self.signals.error.emit(f"加密过程中发生错误: {str(e)}")
            self.signals.finished.emit()

class DecryptionWorker(QThread):
    """文件解密工作线程"""
    
    def __init__(self, files, output_dir, key, delete_original=False):
        """
        初始化解密工作线程
        
        Args:
            files: 要解密的文件列表
            output_dir: 输出目录（如果为None，则输出到原文件所在目录）
            key: 解密密钥
            delete_original: 是否删除原文件
        """
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.key = key
        self.delete_original = delete_original
        
        self.signals = WorkerSignals()
        self.mutex = QMutex()
        self.abort = False
    
    def stop(self):
        """停止工作线程"""
        self.mutex.lock()
        self.abort = True
        self.mutex.unlock()
    
    def run(self):
        """运行线程"""
        try:
            self.signals.started.emit()
            
            total_files = len(self.files)
            processed_files = 0
            
            # 如果是文件夹，递归获取所有文件
            all_files = []
            for file_path in self.files:
                if os.path.isdir(file_path):
                    for root, _, files in os.walk(file_path):
                        for file in files:
                            if file.endswith(".enc"):
                                all_files.append(os.path.join(root, file))
                elif file_path.endswith(".enc"):
                    all_files.append(file_path)
            
            total_size = sum(os.path.getsize(f) for f in all_files if os.path.isfile(f))
            processed_size = 0
            
            # 处理每个文件
            for file_path in all_files:
                if not os.path.isfile(file_path):
                    continue
                    
                # 检查是否取消
                self.mutex.lock()
                if self.abort:
                    self.mutex.unlock()
                    break
                self.mutex.unlock()
                
                # 确定输出文件路径
                if self.output_dir:
                    # 保持相对路径结构
                    rel_path = os.path.relpath(file_path, os.path.commonpath(self.files))
                    # 去掉.enc后缀
                    if rel_path.endswith(".enc"):
                        rel_path = rel_path[:-4]
                    output_path = os.path.join(self.output_dir, rel_path)
                    # 确保输出目录存在
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                else:
                    # 去掉.enc后缀
                    if file_path.endswith(".enc"):
                        output_path = file_path[:-4]
                    else:
                        output_path = file_path + ".dec"
                
                file_size = os.path.getsize(file_path)
                file_name = os.path.basename(file_path)
                
                self.signals.progress.emit(
                    int(processed_size / total_size * 100) if total_size else 0,
                    f"正在解密 {file_name} ({processed_files+1}/{len(all_files)})"
                )
                
                # 尝试解密文件
                try:
                    # 找到合适的解密算法
                    crypto = None
                    # 使用get_all_algorithms代替list_algorithms
                    for algorithm in crypto_factory.get_all_algorithms():
                        try:
                            crypto = crypto_factory.get_crypto_by_name(algorithm)
                            
                            # 检查密钥是否是字典，如果是，获取实际的密钥和IV
                            if isinstance(self.key, dict):
                                key_bytes = self.key.get('key')
                                iv = self.key.get('iv')
                                crypto.decrypt_file(file_path, output_path, key_bytes, iv=iv)
                            else:
                                # 如果密钥不是字典，直接使用
                                crypto.decrypt_file(file_path, output_path, self.key)
                                
                            # 如果没有异常，说明找到了正确的算法
                            break
                        except Exception:
                            # 如果解密失败，尝试下一个算法
                            continue
                    
                    if not crypto:
                        raise ValueError(f"无法找到合适的解密算法")
                    
                    # 删除原文件
                    if self.delete_original:
                        os.remove(file_path)
                    
                    processed_files += 1
                    processed_size += file_size
                    
                    self.signals.progress.emit(
                        int(processed_size / total_size * 100) if total_size else 0,
                        f"已完成 {file_name} ({processed_files}/{len(all_files)})"
                    )
                
                except Exception as e:
                    logger.error(f"解密文件 {file_path} 失败: {str(e)}")
                    self.signals.error.emit(f"解密文件 {file_path} 失败: {str(e)}")
            
            self.signals.finished.emit()
            
        except Exception as e:
            logger.error(f"解密过程中发生错误: {str(e)}")
            logger.error(traceback.format_exc())
            self.signals.error.emit(f"解密过程中发生错误: {str(e)}")
            self.signals.finished.emit()

class KeyGenerationWorker(QThread):
    """密钥生成工作线程"""
    
    def __init__(self, key_type, algorithm, name, password=None):
        """
        初始化密钥生成工作线程
        
        Args:
            key_type: 密钥类型 ('symmetric' 或 'asymmetric')
            algorithm: 加密算法
            name: 密钥名称
            password: 密钥保护密码（可选）
        """
        super().__init__()
        self.key_type = key_type
        self.algorithm = algorithm
        self.name = name
        self.password = password
        
        self.signals = WorkerSignals()
        self.mutex = QMutex()
        self.abort = False
    
    def stop(self):
        """停止工作线程"""
        self.mutex.lock()
        self.abort = True
        self.mutex.unlock()
    
    def run(self):
        """运行线程"""
        try:
            self.signals.started.emit()
            
            # 发送初始进度
            self.signals.progress.emit(0, "正在初始化...")
            
            # 获取加密算法实例
            crypto = crypto_factory.get_crypto_by_name(self.algorithm)
            if not crypto:
                raise ValueError(f"不支持的加密算法: {self.algorithm}")
            
            # 更新进度
            self.signals.progress.emit(20, "正在生成密钥...")
            
            # 生成密钥
            key_data = crypto.generate_key()
            
            # 检查是否取消
            self.mutex.lock()
            if self.abort:
                self.mutex.unlock()
                return
            self.mutex.unlock()
            
            # 更新进度
            self.signals.progress.emit(60, "正在保存密钥...")
            
            # 保存密钥
            from ..crypto.key_manager import key_manager
            key_manager.save_key(key_data, self.name, self.password)
            
            # 更新进度
            self.signals.progress.emit(100, "密钥生成完成!")
            
            self.signals.finished.emit()
        except Exception as e:
            logger.error(f"密钥生成错误: {str(e)}")
            logger.error(traceback.format_exc())
            self.signals.error.emit(f"密钥生成错误: {str(e)}")
            self.signals.finished.emit() 