#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ChaCha20加密模块
"""

import os
import base64
import json
from typing import Tuple, Dict, Any, Union, Optional

# 使用cryptography库实现ChaCha20加密
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.exceptions import InvalidTag

from .crypto_base import CryptoBase
from ..utils.logger import logger


class ChaCha20Cipher(CryptoBase):
    """ChaCha20-Poly1305 AEAD加密算法实现"""
    
    def __init__(self):
        """初始化ChaCha20-Poly1305加密算法"""
        super().__init__("ChaCha20-Poly1305", "ChaCha20-Poly1305 AEAD高性能加密算法")
        self.key_size = 256  # ChaCha20-Poly1305使用256位密钥
    
    def encrypt_data(self, data: bytes, key: bytes, **kwargs) -> bytes:
        """
        加密数据
        
        Args:
            data: 待加密的数据
            key: 加密密钥
            **kwargs: 其他参数
            
        Returns:
            bytes: 加密后的数据
        """
        try:
            # 创建加密器
            cipher = ChaCha20Poly1305(key)
            
            # 生成随机nonce (12字节)
            nonce = os.urandom(12)
            
            # 获取关联数据（如果提供）
            associated_data = kwargs.get('associated_data')
            
            # 加密数据
            ciphertext = cipher.encrypt(nonce, data, associated_data)
            
            # 组合nonce和密文
            encrypted_data = nonce + ciphertext
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"ChaCha20加密错误: {str(e)}")
            raise RuntimeError(f"加密失败: {str(e)}")
    
    def decrypt_data(self, data: bytes, key: bytes, **kwargs) -> bytes:
        """
        解密数据
        
        Args:
            data: 待解密的数据
            key: 解密密钥
            **kwargs: 其他参数
            
        Returns:
            bytes: 解密后的数据
        """
        try:
            # 创建解密器
            cipher = ChaCha20Poly1305(key)
            
            # 从密文中提取nonce (前12字节)
            nonce = data[:12]
            ciphertext = data[12:]
            
            # 获取关联数据（如果提供）
            associated_data = kwargs.get('associated_data')
            
            # 解密数据
            plaintext = cipher.decrypt(nonce, ciphertext, associated_data)
            
            return plaintext
            
        except InvalidTag:
            logger.error("ChaCha20解密失败: 认证标签验证失败")
            raise ValueError("解密失败: 文件可能已损坏或使用了错误的密钥")
        except Exception as e:
            logger.error(f"ChaCha20解密错误: {str(e)}")
            raise RuntimeError(f"解密失败: {str(e)}")
    
    def generate_key(self, **kwargs) -> Dict[str, Any]:
        """
        生成新的ChaCha20-Poly1305密钥
        
        Returns:
            Dict[str, Any]: 包含密钥信息的字典
        """
        # ChaCha20-Poly1305需要32字节密钥
        key = os.urandom(32)
        
        # 返回密钥信息
        return {
            'algorithm': self.name,
            'key': key,
            'key_b64': base64.b64encode(key).decode('utf-8'),
            'key_format': 'base64',
            'meta': {
                'key_size': self.key_size,
            }
        }
    
    def get_meta(self) -> Dict[str, Any]:
        """
        获取算法元数据
        
        Returns:
            Dict[str, Any]: 算法元数据
        """
        return {
            'name': self.name,
            'description': self.description,
            'type': 'symmetric',
            'key_size': self.key_size,
            'security_level': 'very_high'
        } 