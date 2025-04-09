#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块，用于管理应用程序的配置
"""

import os
import json
from typing import Dict, Any, Optional
from ..utils.logger import logger

class Config:
    """配置管理类"""
    
    def __init__(self, config_dir: str = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，默认为用户主目录下的.file_encrypter
        """
        if config_dir is None:
            self.config_dir = os.path.join(os.path.expanduser("~"), ".file_encrypter")
        else:
            self.config_dir = config_dir
        
        # 确保配置目录存在
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
        
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.config = self._load_config()
        
        logger.info(f"配置管理器初始化，配置文件: {self.config_file}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            Dict[str, Any]: 配置项字典
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载配置文件失败: {str(e)}")
        
        # 返回默认配置
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置项字典
        """
        return {
            "app": {
                "language": "zh_CN",
                "theme": "default",
                "show_toolbar": True,
                "show_statusbar": True
            },
            "encryption": {
                "default_algorithm": "AES-256-CBC",
                "chunk_size": 4096,
                "verify_after_encryption": True,
                "secure_delete_original": False
            },
            "paths": {
                "temp_dir": os.path.join(self.config_dir, "temp"),
                "keys_dir": os.path.join(self.config_dir, "keys"),
                "last_open_dir": os.path.expanduser("~")
            },
            "advanced": {
                "log_level": "INFO",
                "max_recent_files": 10,
                "file_monitor_interval": 2.0
            }
        }
    
    def get(self, section: str, key: str, default=None) -> Any:
        """
        获取配置项值
        
        Args:
            section: 配置节
            key: 配置项键名
            default: 默认值，当配置项不存在时返回
            
        Returns:
            Any: 配置项值
        """
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """
        设置配置项值
        
        Args:
            section: 配置节
            key: 配置项键名
            value: 配置项值
            
        Returns:
            bool: 是否设置成功
        """
        # 确保节存在
        if section not in self.config:
            self.config[section] = {}
        
        # 设置值
        self.config[section][key] = value
        
        # 保存配置
        return self.save()
    
    def save(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            logger.debug("配置已保存")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            return False
    
    def reset(self, section: Optional[str] = None) -> bool:
        """
        重置配置为默认值
        
        Args:
            section: 要重置的配置节，None表示重置所有配置
            
        Returns:
            bool: 是否重置成功
        """
        default_config = self._get_default_config()
        
        if section:
            if section in default_config:
                self.config[section] = default_config[section]
            else:
                return False
        else:
            self.config = default_config
        
        return self.save()

# 全局配置管理器实例
config = Config() 