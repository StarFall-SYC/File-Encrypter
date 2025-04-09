#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
哈希算法实现模块
"""

import os
import hashlib
from typing import Dict, Any, Callable
from ..utils.logger import logger

class HashFunction:
    """哈希函数类"""
    
    def __init__(self, name: str, hash_func: Callable, description: str = ""):
        """
        初始化哈希函数
        
        Args:
            name: 哈希函数名称
            hash_func: 哈希函数
            description: 哈希函数描述
        """
        self.name = name
        self.hash_func = hash_func
        self.description = description
    
    def hash_data(self, data: bytes) -> str:
        """
        计算数据的哈希值
        
        Args:
            data: 待哈希的数据
            
        Returns:
            str: 十六进制表示的哈希值
        """
        try:
            hash_obj = self.hash_func()
            hash_obj.update(data)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"计算哈希值失败: {str(e)}")
            raise
    
    def hash_file(self, file_path: str, chunk_size: int = 4096, callback=None) -> str:
        """
        计算文件的哈希值
        
        Args:
            file_path: 文件路径
            chunk_size: 分块大小
            callback: 进度回调函数
            
        Returns:
            str: 十六进制表示的哈希值
        """
        try:
            hash_obj = self.hash_func()
            
            total_size = os.path.getsize(file_path)
            processed_size = 0
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    hash_obj.update(chunk)
                    
                    processed_size += len(chunk)
                    if callback:
                        progress = processed_size / total_size * 100
                        callback(progress)
            
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希值失败: {str(e)}")
            raise

class HashAlgorithms:
    """哈希算法管理类"""
    
    def __init__(self):
        """初始化哈希算法管理类"""
        self.algorithms = {}
        self._register_algorithms()
    
    def _register_algorithms(self):
        """注册内置哈希算法"""
        # MD5 (不推荐用于安全用途)
        self.register_algorithm(
            "MD5",
            hashlib.md5,
            "消息摘要算法5，输出128位哈希值，不推荐用于安全用途"
        )
        
        # SHA家族
        self.register_algorithm(
            "SHA1",
            hashlib.sha1,
            "安全哈希算法1，输出160位哈希值，不推荐用于安全用途"
        )
        
        self.register_algorithm(
            "SHA256",
            hashlib.sha256,
            "安全哈希算法2，输出256位哈希值，SHA-2家族成员"
        )
        
        self.register_algorithm(
            "SHA384",
            hashlib.sha384,
            "安全哈希算法2，输出384位哈希值，SHA-2家族成员"
        )
        
        self.register_algorithm(
            "SHA512",
            hashlib.sha512,
            "安全哈希算法2，输出512位哈希值，SHA-2家族成员"
        )
        
        # SHA-3家族
        if hasattr(hashlib, 'sha3_256'):
            self.register_algorithm(
                "SHA3-256",
                hashlib.sha3_256,
                "安全哈希算法3，输出256位哈希值，SHA-3家族成员"
            )
            
            self.register_algorithm(
                "SHA3-384",
                hashlib.sha3_384,
                "安全哈希算法3，输出384位哈希值，SHA-3家族成员"
            )
            
            self.register_algorithm(
                "SHA3-512",
                hashlib.sha3_512,
                "安全哈希算法3，输出512位哈希值，SHA-3家族成员"
            )
        
        # BLAKE2哈希
        if hasattr(hashlib, 'blake2b'):
            self.register_algorithm(
                "BLAKE2b",
                hashlib.blake2b,
                "BLAKE2b哈希函数，默认输出512位哈希值，高性能加密哈希函数"
            )
            
            self.register_algorithm(
                "BLAKE2s",
                hashlib.blake2s,
                "BLAKE2s哈希函数，默认输出256位哈希值，为32位平台优化的BLAKE2版本"
            )
        
        logger.info(f"已注册 {len(self.algorithms)} 种哈希算法")
    
    def register_algorithm(self, name: str, hash_func: Callable, description: str = ""):
        """
        注册哈希算法
        
        Args:
            name: 算法名称
            hash_func: 哈希函数
            description: 算法描述
        """
        self.algorithms[name] = HashFunction(name, hash_func, description)
        logger.debug(f"注册哈希算法: {name}")
    
    def get_algorithm(self, name: str) -> HashFunction:
        """
        获取哈希算法
        
        Args:
            name: 算法名称
            
        Returns:
            HashFunction: 哈希函数对象
            
        Raises:
            ValueError: 如果算法不存在
        """
        if name not in self.algorithms:
            raise ValueError(f"不支持的哈希算法: {name}")
        
        return self.algorithms[name]
    
    def get_all_algorithms(self) -> Dict[str, HashFunction]:
        """
        获取所有哈希算法
        
        Returns:
            Dict[str, HashFunction]: 算法名称到哈希函数对象的映射
        """
        return self.algorithms.copy()
    
    def verify_file_hash(self, file_path: str, expected_hash: str, 
                       algorithm_name: str = "SHA256", chunk_size: int = 4096,
                       callback=None) -> bool:
        """
        验证文件哈希值
        
        Args:
            file_path: 文件路径
            expected_hash: 期望的哈希值（十六进制字符串）
            algorithm_name: 哈希算法名称
            chunk_size: 分块大小
            callback: 进度回调函数
            
        Returns:
            bool: 哈希值是否匹配
        """
        try:
            algorithm = self.get_algorithm(algorithm_name)
            actual_hash = algorithm.hash_file(file_path, chunk_size, callback)
            
            # 比较时不区分大小写
            return actual_hash.lower() == expected_hash.lower()
        except Exception as e:
            logger.error(f"验证文件哈希值失败: {str(e)}")
            return False

# 全局哈希算法管理实例
hash_algorithms = HashAlgorithms() 