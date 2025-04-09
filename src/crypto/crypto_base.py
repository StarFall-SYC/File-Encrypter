#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
加密模块基础类，定义加密解密接口
"""

from abc import ABC, abstractmethod
import os
from typing import Union, BinaryIO, Tuple, Dict, Any, Optional
from ..utils.logger import logger

class CryptoBase(ABC):
    """加密算法基础抽象类"""
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化加密算法基础类
        
        Args:
            name: 算法名称
            description: 算法描述
        """
        self.name = name
        self.description = description
        logger.info(f"初始化加密算法: {name}")
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def generate_key(self, **kwargs) -> Dict[str, Any]:
        """
        生成密钥
        
        Args:
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 包含密钥及相关信息的字典
        """
        pass
    
    def encrypt_file(self, input_file: str, output_file: str, key: bytes, 
                    chunk_size: int = 4096, callback=None, **kwargs) -> bool:
        """
        加密文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            key: 加密密钥
            chunk_size: 分块大小
            callback: 进度回调函数
            **kwargs: 其他参数
            
        Returns:
            bool: 加密是否成功
        """
        try:
            total_size = os.path.getsize(input_file)
            processed_size = 0
            
            with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    
                    encrypted_chunk = self.encrypt_data(chunk, key, **kwargs)
                    outfile.write(encrypted_chunk)
                    
                    processed_size += len(chunk)
                    if callback:
                        progress = processed_size / total_size * 100
                        callback(progress)
            
            logger.info(f"文件加密成功: {input_file} -> {output_file}")
            return True
        except Exception as e:
            logger.error(f"文件加密失败: {str(e)}")
            return False
    
    def decrypt_file(self, input_file: str, output_file: str, key: bytes,
                    chunk_size: int = 4096, callback=None, **kwargs) -> bool:
        """
        解密文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            key: 解密密钥
            chunk_size: 分块大小
            callback: 进度回调函数
            **kwargs: 其他参数
            
        Returns:
            bool: 解密是否成功
        """
        try:
            total_size = os.path.getsize(input_file)
            processed_size = 0
            
            with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    
                    decrypted_chunk = self.decrypt_data(chunk, key, **kwargs)
                    outfile.write(decrypted_chunk)
                    
                    processed_size += len(chunk)
                    if callback:
                        progress = processed_size / total_size * 100
                        callback(progress)
            
            logger.info(f"文件解密成功: {input_file} -> {output_file}")
            return True
        except Exception as e:
            logger.error(f"文件解密失败: {str(e)}")
            return False 