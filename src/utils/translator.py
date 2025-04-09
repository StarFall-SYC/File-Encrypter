#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
翻译管理器模块 - 提供多语言支持
"""

import os
import importlib
import locale
from typing import Dict, Any, List, Optional
from ..utils.logger import logger

class Translator:
    """翻译管理器类，用于处理多语言支持"""
    
    def __init__(self):
        """初始化翻译管理器"""
        self.available_languages = {}  # 可用语言列表
        self.current_language = None   # 当前语言代码
        self.translations = {}         # 当前语言的翻译字典
        self.default_language = "zh_CN"  # 默认语言
        
        # 加载可用语言
        self._load_available_languages()
        
        # 初始化当前语言
        self._initialize_language()
    
    def _load_available_languages(self):
        """加载所有可用语言"""
        try:
            # 翻译文件目录
            translation_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "resources", "translations")
            
            if not os.path.exists(translation_dir):
                logger.warning(f"翻译目录不存在: {translation_dir}")
                return
            
            # 遍历目录查找语言文件
            for filename in os.listdir(translation_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    lang_code = os.path.splitext(filename)[0]
                    self.available_languages[lang_code] = lang_code
                    logger.debug(f"发现语言: {lang_code}")
            
            logger.info(f"加载了 {len(self.available_languages)} 种语言")
        except Exception as e:
            logger.error(f"加载可用语言失败: {str(e)}")
    
    def _initialize_language(self):
        """初始化当前语言"""
        # 尝试获取系统语言
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                system_lang = system_locale.split('_')[0] + "_" + system_locale.split('_')[1]
                if system_lang in self.available_languages:
                    self.switch_language(system_lang)
                    logger.info(f"根据系统设置选择语言: {system_lang}")
                    return
        except Exception as e:
            logger.warning(f"获取系统语言失败: {str(e)}")
        
        # 如果系统语言不可用，使用默认语言
        self.switch_language(self.default_language)
    
    def switch_language(self, lang_code: str) -> bool:
        """
        切换当前语言
        
        Args:
            lang_code: 语言代码 (如 'zh_CN', 'en_US')
            
        Returns:
            bool: 切换是否成功
        """
        if lang_code not in self.available_languages:
            logger.warning(f"不支持的语言: {lang_code}")
            return False
        
        try:
            # 导入语言模块
            module_path = f"src.resources.translations.{lang_code}"
            lang_module = importlib.import_module(module_path)
            
            # 获取翻译字典
            if hasattr(lang_module, 'translations'):
                self.translations = lang_module.translations
                self.current_language = lang_code
                logger.info(f"切换语言到: {lang_code}")
                return True
            else:
                logger.warning(f"语言模块 {lang_code} 缺少翻译字典")
                return False
                
        except ImportError as e:
            logger.error(f"导入语言模块失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"切换语言失败: {str(e)}")
            return False
    
    def get_text(self, key: str, *args, default: Optional[str] = None) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键名
            *args: 格式化参数
            default: 如果键不存在，返回的默认值
            
        Returns:
            str: 翻译后的文本
        """
        if not self.translations:
            logger.warning("翻译字典为空")
            return default or key
        
        # 获取翻译
        text = self.translations.get(key)
        if text is None:
            logger.debug(f"翻译键不存在: {key}")
            return default or key
        
        # 如果有格式化参数，应用格式化
        if args:
            try:
                return text.format(*args)
            except Exception as e:
                logger.warning(f"格式化翻译文本失败: {str(e)}")
                return text
        
        return text
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        获取所有可用语言
        
        Returns:
            Dict[str, str]: 语言代码到语言名称的映射
        """
        result = {}
        for lang_code in self.available_languages:
            # 获取该语言下的本地语言名称
            current_lang = self.current_language
            self.switch_language(lang_code)
            lang_name = self.get_text(f"lang_{lang_code}", default=lang_code)
            result[lang_code] = lang_name
            # 恢复原来的语言
            self.switch_language(current_lang)
        
        return result
    
    def get_current_language(self) -> str:
        """
        获取当前语言代码
        
        Returns:
            str: 当前语言代码
        """
        return self.current_language or self.default_language

# 创建全局翻译器实例
translator = Translator() 