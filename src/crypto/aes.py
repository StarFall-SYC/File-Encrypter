#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AES加密算法实现
"""

import os
import base64
from typing import Dict, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from .crypto_base import CryptoBase
from ..utils.logger import logger

class AESCipher(CryptoBase):
    """AES加密算法实现类"""
    
    def __init__(self, key_size: int = 256, mode: str = 'CBC'):
        """
        初始化AES加密算法
        
        Args:
            key_size: 密钥大小，支持128、192、256位
            mode: 加密模式，支持CBC、CFB、OFB、CTR等
        """
        super().__init__(name=f"AES-{key_size}-{mode}", 
                        description=f"高级加密标准算法，密钥大小{key_size}位，{mode}模式")
        
        self.key_size = key_size
        self.mode = mode
        self.block_size = 128  # AES固定块大小为128位(16字节)
        
        # 校验参数
        if key_size not in (128, 192, 256):
            raise ValueError("AES密钥大小必须为128、192或256位")
        
        if mode not in ('CBC', 'CFB', 'OFB', 'CTR'):
            raise ValueError("不支持的加密模式")
    
    def generate_key(self, **kwargs) -> Dict[str, Any]:
        """
        生成AES密钥
        
        Returns:
            Dict[str, Any]: 包含密钥和初始化向量的字典
        """
        key = os.urandom(self.key_size // 8)  # 转换为字节数
        iv = os.urandom(16)  # AES需要16字节的初始化向量
        
        key_dict = {
            'key': key,
            'iv': iv,
            'key_b64': base64.b64encode(key).decode('utf-8'),
            'iv_b64': base64.b64encode(iv).decode('utf-8'),
            'algorithm': self.name,
            'key_size': self.key_size,
            'mode': self.mode
        }
        
        logger.info(f"生成{self.name}密钥")
        return key_dict
    
    def _get_cipher(self, key: bytes, iv: bytes) -> Cipher:
        """
        获取加密器实例
        
        Args:
            key: 密钥
            iv: 初始化向量
            
        Returns:
            Cipher: 加密器实例
        """
        if len(key) * 8 != self.key_size:
            raise ValueError(f"密钥长度不匹配，需要{self.key_size}位，实际为{len(key) * 8}位")
        
        if self.mode == 'CBC':
            return Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
        elif self.mode == 'CFB':
            return Cipher(
                algorithms.AES(key),
                modes.CFB(iv),
                backend=default_backend()
            )
        elif self.mode == 'OFB':
            return Cipher(
                algorithms.AES(key),
                modes.OFB(iv),
                backend=default_backend()
            )
        elif self.mode == 'CTR':
            return Cipher(
                algorithms.AES(key),
                modes.CTR(iv),
                backend=default_backend()
            )
    
    def encrypt_data(self, data: bytes, key: bytes, **kwargs) -> bytes:
        """
        加密数据
        
        Args:
            data: 待加密的数据
            key: 加密密钥
            **kwargs: 其他参数，包括iv(初始化向量)
            
        Returns:
            bytes: 加密后的数据
        """
        iv = kwargs.get('iv')
        if not iv:
            raise ValueError("缺少初始化向量(iv)")
        
        try:
            cipher = self._get_cipher(key, iv)
            encryptor = cipher.encryptor()
            
            # 如果是CBC模式，需要填充
            if self.mode == 'CBC':
                padder = padding.PKCS7(self.block_size).padder()
                padded_data = padder.update(data) + padder.finalize()
                encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            else:
                encrypted_data = encryptor.update(data) + encryptor.finalize()
            
            return encrypted_data
        except Exception as e:
            logger.error(f"AES加密数据失败: {str(e)}")
            raise
    
    def decrypt_data(self, data: bytes, key: bytes, **kwargs) -> bytes:
        """
        解密数据
        
        Args:
            data: 待解密的数据
            key: 解密密钥
            **kwargs: 其他参数，包括iv(初始化向量)
            
        Returns:
            bytes: 解密后的数据
        """
        iv = kwargs.get('iv')
        if not iv:
            raise ValueError("缺少初始化向量(iv)")
        
        try:
            cipher = self._get_cipher(key, iv)
            decryptor = cipher.decryptor()
            
            if self.mode == 'CBC':
                # 先解密，再去除填充
                decrypted_padded_data = decryptor.update(data) + decryptor.finalize()
                unpadder = padding.PKCS7(self.block_size).unpadder()
                decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
            else:
                decrypted_data = decryptor.update(data) + decryptor.finalize()
            
            return decrypted_data
        except Exception as e:
            logger.error(f"AES解密数据失败: {str(e)}")
            raise 