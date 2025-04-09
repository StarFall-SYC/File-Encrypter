#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量处理模块 - 提供多线程并行处理文件的功能
"""

import os
import time
import queue
import threading
from typing import List, Dict, Any, Callable, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .logger import logger
from .file_utils import get_file_size, format_size


class BatchProcessor:
    """批量处理器类，提供多线程文件处理功能"""
    
    def __init__(self, max_workers=None):
        """
        初始化批量处理器
        
        Args:
            max_workers: 最大工作线程数，默认为CPU核心数 * 2
        """
        self.max_workers = max_workers or os.cpu_count() * 2
        self.stop_requested = False
        self.progress_callback = None
        self.error_callback = None
        self.completion_callback = None
        
        # 状态跟踪
        self.total_files = 0
        self.processed_files = 0
        self.total_size = 0
        self.processed_size = 0
        self.failed_files = []
        self.start_time = 0
        
        logger.info(f"批量处理器初始化，最大工作线程数: {self.max_workers}")
    
    def register_callbacks(self, progress_callback=None, error_callback=None, completion_callback=None):
        """
        注册回调函数
        
        Args:
            progress_callback: 进度回调函数，接收 (current, total, percentage, speed, eta) 参数
            error_callback: 错误回调函数，接收 (file_path, error) 参数
            completion_callback: 完成回调函数，接收 (success_count, fail_count, total_time) 参数
        """
        self.progress_callback = progress_callback
        self.error_callback = error_callback
        self.completion_callback = completion_callback
    
    def process_files(self, file_paths: List[str], process_func: Callable[[str, Any], Any], 
                      args: Any = None, process_name: str = "处理"):
        """
        并行处理多个文件
        
        Args:
            file_paths: 要处理的文件路径列表
            process_func: 处理函数，接收 (file_path, args) 参数
            args: 传递给处理函数的额外参数
            process_name: 处理类型名称，用于日志记录
            
        Returns:
            Tuple[int, int, float]: (成功处理的文件数, 失败的文件数, 总处理时间)
        """
        self.stop_requested = False
        self.total_files = len(file_paths)
        self.processed_files = 0
        self.failed_files = []
        
        # 计算总文件大小
        self.total_size = sum(get_file_size(f) for f in file_paths if os.path.isfile(f))
        self.processed_size = 0
        
        logger.info(f"开始{process_name} {self.total_files} 个文件，总大小: {format_size(self.total_size)}")
        
        self.start_time = time.time()
        start_time_total = self.start_time
        
        # 使用线程池并行处理文件
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(self._process_file_wrapper, process_func, file_path, args): file_path
                for file_path in file_paths
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                if self.stop_requested:
                    for f in future_to_file:
                        f.cancel()
                    break
                
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    self.processed_files += 1
                    
                    # 更新进度
                    if os.path.isfile(file_path):
                        self.processed_size += get_file_size(file_path)
                    
                    self._update_progress()
                    
                except Exception as e:
                    logger.error(f"{process_name}文件失败: {file_path}, 错误: {str(e)}")
                    self.failed_files.append((file_path, str(e)))
                    
                    if self.error_callback:
                        self.error_callback(file_path, str(e))
        
        # 计算总时间
        total_time = time.time() - start_time_total
        success_count = self.processed_files - len(self.failed_files)
        
        logger.info(f"{process_name}完成: 成功={success_count}, 失败={len(self.failed_files)}, "
                   f"总时间={total_time:.2f}秒")
        
        # 调用完成回调
        if self.completion_callback and not self.stop_requested:
            self.completion_callback(success_count, len(self.failed_files), total_time)
        
        return success_count, len(self.failed_files), total_time
    
    def _process_file_wrapper(self, process_func, file_path, args):
        """处理单个文件的包装函数，添加错误处理"""
        try:
            return process_func(file_path, args)
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
            raise
    
    def _update_progress(self):
        """更新并报告处理进度"""
        if not self.progress_callback:
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # 计算进度百分比
        if self.total_files > 0:
            percentage = self.processed_files / self.total_files * 100
        else:
            percentage = 0
            
        # 计算处理速度（每秒处理的字节数）
        if elapsed_time > 0:
            speed = self.processed_size / elapsed_time
        else:
            speed = 0
            
        # 估计剩余时间
        if speed > 0 and self.processed_size < self.total_size:
            remaining_size = self.total_size - self.processed_size
            eta = remaining_size / speed
        else:
            eta = 0
            
        # 调用回调函数
        self.progress_callback(
            self.processed_files,
            self.total_files,
            percentage,
            speed,
            eta
        )
    
    def stop(self):
        """请求停止处理"""
        logger.info("请求停止批量处理")
        self.stop_requested = True
        

# 创建全局批处理实例
batch_processor = BatchProcessor() 