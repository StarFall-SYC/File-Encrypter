#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件监控模块 - 监控目录变化并自动处理新文件
"""

import os
import time
import threading
import queue
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileMovedEvent

from .logger import logger
from ..crypto.crypto_factory import crypto_factory


class FileMonitorHandler(FileSystemEventHandler):
    """文件系统事件处理器，处理文件创建、修改等事件"""
    
    def __init__(self, queue_instance, patterns=None, ignore_patterns=None,
                 ignore_directories=True, case_sensitive=True):
        """
        初始化事件处理器
        
        Args:
            queue_instance: 事件队列
            patterns: 匹配的文件模式
            ignore_patterns: 忽略的文件模式
            ignore_directories: 是否忽略目录事件
            case_sensitive: 是否区分大小写
        """
        super().__init__()
        self.queue = queue_instance
        self.patterns = patterns
        self.ignore_patterns = ignore_patterns
        self.ignore_directories = ignore_directories
        self.case_sensitive = case_sensitive
    
    def on_created(self, event):
        """处理文件创建事件"""
        if self.ignore_directories and event.is_directory:
            return
            
        if self._should_process_file(event.src_path):
            self.queue.put(('created', event.src_path))
            logger.debug(f"检测到新文件: {event.src_path}")
    
    def on_modified(self, event):
        """处理文件修改事件"""
        if self.ignore_directories and event.is_directory:
            return
            
        if self._should_process_file(event.src_path):
            self.queue.put(('modified', event.src_path))
            logger.debug(f"检测到文件修改: {event.src_path}")
    
    def on_moved(self, event):
        """处理文件移动事件"""
        if self.ignore_directories and event.is_directory:
            return
            
        if self._should_process_file(event.dest_path):
            self.queue.put(('moved', event.dest_path))
            logger.debug(f"检测到文件移动: {event.dest_path}")
    
    def _should_process_file(self, file_path):
        """
        检查是否应该处理该文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否处理该文件
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False
            
        # 检查文件是否是隐藏文件
        filename = os.path.basename(file_path)
        if filename.startswith('.'):
            return False
            
        # 检查文件是否匹配模式
        if self.patterns:
            matched = False
            for pattern in self.patterns:
                if self._match_pattern(filename, pattern):
                    matched = True
                    break
            if not matched:
                return False
                
        # 检查文件是否匹配忽略模式
        if self.ignore_patterns:
            for pattern in self.ignore_patterns:
                if self._match_pattern(filename, pattern):
                    return False
                    
        return True
    
    def _match_pattern(self, filename, pattern):
        """
        检查文件名是否匹配模式
        
        Args:
            filename: 文件名
            pattern: 匹配模式
            
        Returns:
            bool: 是否匹配
        """
        if not self.case_sensitive:
            filename = filename.lower()
            pattern = pattern.lower()
            
        # 简单的通配符匹配
        if pattern.startswith('*'):
            return filename.endswith(pattern[1:])
        elif pattern.endswith('*'):
            return filename.startswith(pattern[:-1])
        elif '*' in pattern:
            parts = pattern.split('*')
            return filename.startswith(parts[0]) and filename.endswith(parts[1])
        else:
            return filename == pattern


class FileMonitor:
    """文件监控器，监控目录并处理文件变化"""
    
    def __init__(self):
        """初始化文件监控器"""
        self.observers = {}
        self.event_queue = queue.Queue()
        self.is_running = False
        self.processing_thread = None
        self.auto_process_handlers = {}
        
        # 监控系统是否已启动
        self.is_monitoring = False
    
    def start_monitoring(self, directory, patterns=None, ignore_patterns=None,
                        recursive=True, auto_process=False, process_handler=None):
        """
        开始监控目录
        
        Args:
            directory: 要监控的目录
            patterns: 匹配的文件模式列表
            ignore_patterns: 忽略的文件模式列表
            recursive: 是否递归监控子目录
            auto_process: 是否自动处理新文件
            process_handler: 自动处理回调函数，接收 (event_type, file_path) 参数
            
        Returns:
            str: 监控任务ID
        """
        if not os.path.isdir(directory):
            raise ValueError(f"无效的目录: {directory}")
            
        # 生成唯一的监控任务ID
        monitor_id = f"{directory}_{int(time.time())}"
        
        # 如果设置了自动处理，保存处理函数
        if auto_process and process_handler:
            self.auto_process_handlers[monitor_id] = process_handler
        
        # 创建观察者
        observer = Observer()
        event_handler = FileMonitorHandler(
            self.event_queue,
            patterns=patterns,
            ignore_patterns=ignore_patterns,
            ignore_directories=True
        )
        
        # 开始监控
        observer.schedule(event_handler, directory, recursive=recursive)
        observer.start()
        
        # 保存观察者
        self.observers[monitor_id] = {
            'observer': observer,
            'directory': directory,
            'patterns': patterns,
            'ignore_patterns': ignore_patterns,
            'recursive': recursive,
            'auto_process': auto_process
        }
        
        logger.info(f"开始监控目录: {directory}, 任务ID: {monitor_id}")
        
        # 如果处理线程未运行，启动处理线程
        if not self.is_running:
            self._start_processing_thread()
        
        return monitor_id
    
    def stop_monitoring(self, monitor_id=None):
        """
        停止监控
        
        Args:
            monitor_id: 监控任务ID，如果为None则停止所有监控
        """
        if monitor_id:
            if monitor_id in self.observers:
                observer_info = self.observers.pop(monitor_id)
                observer_info['observer'].stop()
                observer_info['observer'].join()
                
                # 如果有自动处理函数，移除
                if monitor_id in self.auto_process_handlers:
                    del self.auto_process_handlers[monitor_id]
                    
                logger.info(f"停止监控目录: {observer_info['directory']}, 任务ID: {monitor_id}")
        else:
            # 停止所有监控
            for mid, observer_info in list(self.observers.items()):
                observer_info['observer'].stop()
                observer_info['observer'].join()
                
                # 如果有自动处理函数，移除
                if mid in self.auto_process_handlers:
                    del self.auto_process_handlers[mid]
                    
                logger.info(f"停止监控目录: {observer_info['directory']}, 任务ID: {mid}")
                
            self.observers.clear()
        
        # 如果没有监控任务，停止处理线程
        if not self.observers and self.is_running:
            self.is_running = False
            if self.processing_thread:
                self.processing_thread.join()
                self.processing_thread = None
    
    def get_monitoring_tasks(self):
        """
        获取所有监控任务
        
        Returns:
            List[Dict]: 监控任务信息列表
        """
        result = []
        for monitor_id, observer_info in self.observers.items():
            task_info = {
                'id': monitor_id,
                'directory': observer_info['directory'],
                'patterns': observer_info['patterns'],
                'ignore_patterns': observer_info['ignore_patterns'],
                'recursive': observer_info['recursive'],
                'auto_process': observer_info['auto_process'],
                'has_handler': monitor_id in self.auto_process_handlers
            }
            result.append(task_info)
            
        return result
    
    def _start_processing_thread(self):
        """启动事件处理线程"""
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
        logger.info("文件监控处理线程已启动")
    
    def _process_events(self):
        """处理事件队列中的事件"""
        while self.is_running:
            try:
                # 从队列中获取事件，超时1秒
                event_type, file_path = self.event_queue.get(timeout=1)
                
                # 检查是否有自动处理函数
                for monitor_id, handler in self.auto_process_handlers.items():
                    observer_info = self.observers.get(monitor_id)
                    if not observer_info:
                        continue
                        
                    # 检查文件是否在监控目录下
                    directory = observer_info['directory']
                    if os.path.normpath(file_path).startswith(os.path.normpath(directory)):
                        try:
                            # 调用处理函数
                            handler(event_type, file_path)
                        except Exception as e:
                            logger.error(f"处理文件事件时出错: {str(e)}")
                
                # 标记任务完成
                self.event_queue.task_done()
                
            except queue.Empty:
                # 队列为空，继续循环
                continue
            except Exception as e:
                logger.error(f"处理文件监控事件时出错: {str(e)}")


# 创建全局文件监控器实例
file_monitor = FileMonitor() 