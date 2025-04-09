#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
加密算法工厂模块，管理所有加密算法
"""

from typing import Dict, List, Type, Any
from .crypto_base import CryptoBase
from .aes import AESCipher
from .rsa import RSACipher
from .chacha20 import ChaCha20Cipher
from ..utils.logger import logger

class CryptoFactory:
    """加密算法工厂类"""
    
    def __init__(self):
        """初始化加密算法工厂"""
        self.algorithms = {}
        self._register_algorithms()
    
    def _register_algorithms(self):
        """注册内置加密算法"""
        # 注册AES算法，不同密钥大小和模式
        self.register_algorithm("AES-128-CBC", lambda: AESCipher(key_size=128, mode='CBC'))
        self.register_algorithm("AES-192-CBC", lambda: AESCipher(key_size=192, mode='CBC'))
        self.register_algorithm("AES-256-CBC", lambda: AESCipher(key_size=256, mode='CBC'))
        self.register_algorithm("AES-128-CFB", lambda: AESCipher(key_size=128, mode='CFB'))
        self.register_algorithm("AES-192-CFB", lambda: AESCipher(key_size=192, mode='CFB'))
        self.register_algorithm("AES-256-CFB", lambda: AESCipher(key_size=256, mode='CFB'))
        self.register_algorithm("AES-128-CTR", lambda: AESCipher(key_size=128, mode='CTR'))
        self.register_algorithm("AES-192-CTR", lambda: AESCipher(key_size=192, mode='CTR'))
        self.register_algorithm("AES-256-CTR", lambda: AESCipher(key_size=256, mode='CTR'))
        
        # 注册RSA算法，不同密钥大小
        self.register_algorithm("RSA-1024", lambda: RSACipher(key_size=1024))
        self.register_algorithm("RSA-2048", lambda: RSACipher(key_size=2048))
        self.register_algorithm("RSA-4096", lambda: RSACipher(key_size=4096))
        
        # 注册ChaCha20算法
        self.register_algorithm("ChaCha20-Poly1305", lambda: ChaCha20Cipher())
        
        logger.info(f"已注册 {len(self.algorithms)} 种加密算法")
    
    def register_algorithm(self, name: str, factory_func):
        """
        注册加密算法
        
        Args:
            name: 算法名称
            factory_func: 创建算法实例的工厂函数
        """
        self.algorithms[name] = factory_func
        logger.debug(f"注册加密算法: {name}")
    
    def create_algorithm(self, name: str) -> CryptoBase:
        """
        创建加密算法实例
        
        Args:
            name: 算法名称
            
        Returns:
            CryptoBase: 加密算法实例
            
        Raises:
            ValueError: 如果算法不存在
        """
        if name not in self.algorithms:
            raise ValueError(f"不支持的加密算法: {name}")
        
        return self.algorithms[name]()
    
    def get_all_algorithms(self) -> List[str]:
        """
        获取所有支持的加密算法名称
        
        Returns:
            List[str]: 算法名称列表
        """
        return list(self.algorithms.keys())
    
    def get_algorithm_by_category(self) -> Dict[str, List[str]]:
        """
        按类别获取算法
        
        Returns:
            Dict[str, List[str]]: 按类别分组的算法名称
        """
        categories = {
            "对称加密": [],
            "非对称加密": [],
            "其他": []
        }
        
        for algo_name in self.algorithms.keys():
            if algo_name.startswith("AES"):
                categories["对称加密"].append(algo_name)
            elif algo_name.startswith("RSA"):
                categories["非对称加密"].append(algo_name)
            else:
                categories["其他"].append(algo_name)
        
        return categories

    def get_crypto_by_name(self, name: str) -> CryptoBase:
        """
        根据名称获取加密算法实例
        
        Args:
            name: 算法名称
            
        Returns:
            CryptoBase: 加密算法实例，如果不存在则返回None
        """
        try:
            return self.create_algorithm(name)
        except ValueError:
            logger.error(f"不支持的加密算法: {name}")
            return None

# 全局加密算法工厂实例
crypto_factory = CryptoFactory() 