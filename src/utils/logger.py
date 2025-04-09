#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志记录工具模块
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import time

# 日志文件目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger(log_level=logging.INFO):
    """
    设置和配置日志记录器
    
    Args:
        log_level: 日志级别，默认为INFO
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建logger
    logger = logging.getLogger('file_encrypter')
    logger.setLevel(log_level)
    
    # 避免重复添加handler
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # 创建控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 创建文件handler
    log_file = os.path.join(LOG_DIR, f'app_{time.strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    # 创建formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # 设置formatter
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 全局logger实例
logger = setup_logger() 