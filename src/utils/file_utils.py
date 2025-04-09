#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件处理工具模块，提供文件操作相关功能
"""

import os
import shutil
import tempfile
from typing import List, Tuple, Callable, Optional
from pathlib import Path
from ..utils.logger import logger

def get_file_size(file_path: str) -> int:
    """
    获取文件大小
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小（字节）
    """
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return os.path.getsize(file_path)
        return 0
    except Exception as e:
        logger.error(f"获取文件大小失败: {str(e)}")
        return 0

def list_files(directory: str, recursive: bool = True, include_pattern: str = None, 
              exclude_pattern: str = None) -> List[str]:
    """
    列出目录中的所有文件
    
    Args:
        directory: 目录路径
        recursive: 是否递归搜索子目录
        include_pattern: 包含的文件模式（如*.txt）
        exclude_pattern: 排除的文件模式
        
    Returns:
        List[str]: 文件路径列表
    """
    from glob import glob
    
    if not os.path.isdir(directory):
        logger.error(f"目录不存在: {directory}")
        return []
    
    # 构建通配符模式
    pattern = "**/*" if recursive else "*"
    if include_pattern:
        pattern = os.path.join(pattern, include_pattern)
    
    # 使用glob获取文件列表
    file_paths = []
    for path in glob(os.path.join(directory, pattern), recursive=recursive):
        if os.path.isfile(path):
            # 检查是否排除
            if exclude_pattern and glob.fnmatch.fnmatch(os.path.basename(path), exclude_pattern):
                continue
            file_paths.append(path)
    
    return file_paths

def secure_delete(file_path: str, passes: int = 3) -> bool:
    """
    安全删除文件（多次覆盖）
    
    Args:
        file_path: 文件路径
        passes: 覆盖次数
        
    Returns:
        bool: 删除是否成功
    """
    if not os.path.isfile(file_path):
        logger.warning(f"文件不存在: {file_path}")
        return False
    
    try:
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 多次覆盖文件内容
        for i in range(passes):
            with open(file_path, 'wb') as f:
                # 第一遍用0覆盖
                if i == 0:
                    f.write(b'\x00' * file_size)
                # 第二遍用1覆盖
                elif i == 1:
                    f.write(b'\xFF' * file_size)
                # 第三遍用随机数据覆盖
                else:
                    f.write(os.urandom(file_size))
            
            # 强制写入磁盘
            os.fsync(f.fileno())
        
        # 最后删除文件
        os.remove(file_path)
        logger.info(f"安全删除文件成功: {file_path}")
        return True
    except Exception as e:
        logger.error(f"安全删除文件失败: {str(e)}")
        return False

def create_temp_file(prefix: str = "temp_", suffix: str = "", dir: str = None) -> str:
    """
    创建临时文件
    
    Args:
        prefix: 文件名前缀
        suffix: 文件名后缀
        dir: 临时文件目录
        
    Returns:
        str: 临时文件路径
    """
    try:
        if dir and not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        
        temp_file = tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, 
                                              dir=dir, delete=False)
        temp_file.close()
        
        logger.debug(f"创建临时文件: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        logger.error(f"创建临时文件失败: {str(e)}")
        return ""

def process_files(source_path: str, output_dir: str, process_func: Callable,
                callback=None, recursive: bool = True, **kwargs) -> Tuple[int, int]:
    """
    批量处理文件
    
    Args:
        source_path: 源文件或目录路径
        output_dir: 输出目录
        process_func: 处理函数，接受(input_file, output_file, **kwargs)参数
        callback: 进度回调函数
        recursive: 如果source_path是目录，是否递归处理
        **kwargs: 传递给process_func的其他参数
        
    Returns:
        Tuple[int, int]: (成功处理文件数, 总文件数)
    """
    try:
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 要处理的文件列表
        files_to_process = []
        
        # 如果是文件，直接添加到处理列表
        if os.path.isfile(source_path):
            files_to_process.append(source_path)
        # 如果是目录，获取所有文件
        elif os.path.isdir(source_path):
            files_to_process = list_files(source_path, recursive)
        else:
            logger.error(f"无效的源路径: {source_path}")
            return 0, 0
        
        # 没有文件要处理
        if not files_to_process:
            logger.warning(f"没有找到要处理的文件: {source_path}")
            return 0, 0
        
        # 开始处理文件
        total_files = len(files_to_process)
        success_count = 0
        
        for i, input_file in enumerate(files_to_process):
            try:
                # 确定输出文件路径
                if os.path.isdir(source_path):
                    rel_path = os.path.relpath(input_file, source_path)
                    output_file = os.path.join(output_dir, rel_path)
                else:
                    output_file = os.path.join(output_dir, os.path.basename(input_file))
                
                # 确保输出文件的目录存在
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                # 执行处理函数
                if process_func(input_file, output_file, **kwargs):
                    success_count += 1
                
                # 更新进度
                if callback:
                    progress = (i + 1) / total_files * 100
                    callback(progress)
            
            except Exception as e:
                logger.error(f"处理文件失败 {input_file}: {str(e)}")
        
        return success_count, total_files
    
    except Exception as e:
        logger.error(f"批量处理文件失败: {str(e)}")
        return 0, 0

def get_file_info(file_path: str) -> dict:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        dict: 文件信息字典
    """
    try:
        if not os.path.exists(file_path):
            return {}
        
        file_stat = os.stat(file_path)
        path = Path(file_path)
        
        return {
            "name": path.name,
            "path": str(path.absolute()),
            "size": file_stat.st_size,
            "size_human": format_size(file_stat.st_size),
            "modified": file_stat.st_mtime,
            "created": file_stat.st_ctime,
            "extension": path.suffix,
            "is_dir": os.path.isdir(file_path)
        }
    except Exception as e:
        logger.error(f"获取文件信息失败: {str(e)}")
        return {}

def format_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化后的大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB" 