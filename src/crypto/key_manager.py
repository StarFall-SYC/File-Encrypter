#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
密钥管理模块，处理密钥的生成、保存和加载
"""

import os
import json
import base64
import hashlib
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from ..utils.logger import logger

class KeyManager:
    """密钥管理器类"""
    
    def __init__(self, storage_dir: str = None):
        """
        初始化密钥管理器
        
        Args:
            storage_dir: 密钥存储目录，默认为用户主目录下的.file_encrypter/keys
        """
        if storage_dir is None:
            home_dir = os.path.expanduser("~")
            storage_dir = os.path.join(home_dir, ".file_encrypter", "keys")
        
        self.storage_dir = storage_dir
        
        # 确保密钥存储目录存在
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)
        
        logger.info(f"密钥管理器初始化，存储目录: {self.storage_dir}")
    
    def _derive_key_from_password(self, password: str, salt: bytes = None) -> tuple:
        """
        从密码派生加密密钥
        
        Args:
            password: 用户密码
            salt: 盐值，如果为None则生成新的盐值
            
        Returns:
            tuple: (key, salt)，其中key是派生的密钥，salt是使用的盐值
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def save_key(self, key_data: Dict[str, Any], key_name: str, 
                password: str = None) -> str:
        """
        保存密钥数据
        
        Args:
            key_data: 密钥数据字典
            key_name: 密钥名称
            password: 保护密钥的密码，如果提供，将加密保存
            
        Returns:
            str: 保存的密钥文件路径
        """
        # 确保密钥名称有效
        key_name = key_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        key_file = os.path.join(self.storage_dir, f"{key_name}.key")
        
        # 准备要保存的数据
        save_data = {
            "name": key_name,
            "algorithm": key_data.get("algorithm", "unknown"),
            "created_at": key_data.get("created_at", 
                                    import_module("datetime").datetime.now().isoformat())
        }
        
        # 处理密钥数据
        for key, value in key_data.items():
            # 跳过Python对象，只保存可序列化的数据
            if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                save_data[key] = value
            elif isinstance(value, bytes):
                save_data[key] = base64.b64encode(value).decode('utf-8')
        
        # 加密数据（如果提供了密码）
        if password:
            # 生成加密密钥和盐值
            derived_key, salt = self._derive_key_from_password(password)
            fernet = Fernet(derived_key)
            
            # 加密JSON数据
            json_data = json.dumps(save_data).encode('utf-8')
            encrypted_data = fernet.encrypt(json_data)
            
            # 保存加密数据和盐值
            with open(key_file, 'wb') as f:
                f.write(b"ENCRYPTED:")
                f.write(salt)
                f.write(encrypted_data)
        else:
            # 不加密直接保存
            with open(key_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
        
        logger.info(f"密钥保存成功: {key_file}")
        return key_file
    
    def load_key(self, key_name: str, password: str = None) -> Optional[Dict[str, Any]]:
        """
        加载密钥数据
        
        Args:
            key_name: 密钥名称
            password: 保护密钥的密码，如果密钥已加密则需要提供
            
        Returns:
            Optional[Dict[str, Any]]: 密钥数据字典，如果加载失败则返回None
        """
        key_file = os.path.join(self.storage_dir, f"{key_name}.key")
        
        if not os.path.exists(key_file):
            logger.error(f"密钥文件不存在: {key_file}")
            return None
        
        try:
            # 尝试读取文件
            with open(key_file, 'rb') as f:
                file_data = f.read()
            
            # 检查是否加密
            if file_data.startswith(b"ENCRYPTED:"):
                if not password:
                    logger.error("密钥已加密，需要提供密码")
                    return None
                
                # 提取盐值和加密数据
                salt = file_data[10:26]  # 读取16字节的盐值
                encrypted_data = file_data[26:]
                
                # 从密码派生密钥
                derived_key, _ = self._derive_key_from_password(password, salt)
                fernet = Fernet(derived_key)
                
                # 解密数据
                try:
                    decrypted_data = fernet.decrypt(encrypted_data)
                    key_data = json.loads(decrypted_data.decode('utf-8'))
                except Exception as e:
                    logger.error(f"密钥解密失败，可能是密码错误: {str(e)}")
                    return None
            else:
                # 未加密，直接解析JSON
                key_data = json.loads(file_data.decode('utf-8'))
            
            # 处理base64编码的字节数据
            result_data = {}
            for key, value in key_data.items():
                if key.endswith("_b64") or key in ["key", "iv", "private_pem", "public_pem"]:
                    try:
                        # 尝试解码为字节
                        result_data[key] = value
                        if isinstance(value, str):
                            result_data[key.replace("_b64", "")] = base64.b64decode(value)
                    except:
                        # 如果解码失败，保留原值
                        result_data[key] = value
                else:
                    result_data[key] = value
            
            logger.info(f"密钥加载成功: {key_file}")
            return result_data
        
        except Exception as e:
            logger.error(f"加载密钥失败: {str(e)}")
            return None
    
    def list_keys(self) -> Dict[str, Dict[str, Any]]:
        """
        列出所有存储的密钥
        
        Returns:
            Dict[str, Dict[str, Any]]: 密钥名称到密钥元数据的映射
        """
        result = {}
        
        for file_name in os.listdir(self.storage_dir):
            if file_name.endswith(".key"):
                key_name = file_name[:-4]  # 移除.key后缀
                key_file = os.path.join(self.storage_dir, file_name)
                
                # 尝试读取文件头部判断是否加密
                is_encrypted = False
                try:
                    with open(key_file, 'rb') as f:
                        header = f.read(10)
                        is_encrypted = header == b"ENCRYPTED:"
                except:
                    pass
                
                # 如果未加密，获取算法信息
                algorithm = "unknown"
                if not is_encrypted:
                    try:
                        with open(key_file, 'r', encoding='utf-8') as f:
                            key_data = json.load(f)
                            algorithm = key_data.get("algorithm", "unknown")
                    except:
                        pass
                
                result[key_name] = {
                    "name": key_name,
                    "file": key_file,
                    "is_encrypted": is_encrypted,
                    "algorithm": algorithm if not is_encrypted else "encrypted"
                }
        
        return result
    
    def delete_key(self, key_name: str) -> bool:
        """
        删除密钥
        
        Args:
            key_name: 密钥名称
            
        Returns:
            bool: 删除是否成功
        """
        key_file = os.path.join(self.storage_dir, f"{key_name}.key")
        
        if not os.path.exists(key_file):
            logger.error(f"密钥文件不存在: {key_file}")
            return False
        
        try:
            os.remove(key_file)
            logger.info(f"密钥删除成功: {key_file}")
            return True
        except Exception as e:
            logger.error(f"删除密钥失败: {str(e)}")
            return False

# 解决循环导入问题
from importlib import import_module

# 全局密钥管理器实例
key_manager = KeyManager() 