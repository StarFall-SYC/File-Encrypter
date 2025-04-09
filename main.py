#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
通用文件加密工具主程序
"""

import os
import sys
import argparse
from src.utils.logger import setup_logger
from src.gui.qt_main_window import MainWindow
from src.utils.theme_manager import theme_manager
from src.utils.translator import translator
from src.utils.app_updater import app_updater
from src.config.app_settings import settings
from PyQt5.QtWidgets import QApplication

def main():
    """
    应用程序主入口函数
    """
    # 设置日志记录
    logger = setup_logger()
    logger.info("应用程序启动")
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="文件加密工具")
    parser.add_argument('--cli', action='store_true', help='使用命令行界面')
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    
    # 为CLI模式添加命令
    subparsers = parser.add_subparsers(dest="command", help="CLI命令")
    
    # 加密命令
    encrypt_parser = subparsers.add_parser("encrypt", help="加密文件")
    encrypt_parser.add_argument("file", nargs='?', help="要加密的文件路径")
    encrypt_parser.add_argument("-o", "--output", help="输出文件路径")
    encrypt_parser.add_argument("-k", "--key", help="使用的密钥名称")
    encrypt_parser.add_argument("-a", "--algorithm", default="AES-256-CBC", help="使用的加密算法")
    encrypt_parser.add_argument("-d", "--delete", action="store_true", help="加密后删除原文件")
    
    # 解密命令
    decrypt_parser = subparsers.add_parser("decrypt", help="解密文件")
    decrypt_parser.add_argument("file", nargs='?', help="要解密的文件路径")
    decrypt_parser.add_argument("-o", "--output", help="输出文件路径")
    decrypt_parser.add_argument("-k", "--key", help="使用的密钥名称")
    decrypt_parser.add_argument("-d", "--delete", action="store_true", help="解密后删除原文件")
    
    # 密钥管理命令
    key_parser = subparsers.add_parser("key", help="密钥管理")
    key_subparsers = key_parser.add_subparsers(dest="key_command", help="密钥命令")
    
    # 生成密钥
    gen_parser = key_subparsers.add_parser("generate", help="生成新密钥")
    gen_parser.add_argument("name", nargs='?', help="密钥名称")
    gen_parser.add_argument("-a", "--algorithm", default="AES-256-CBC", help="加密算法")
    gen_parser.add_argument("-p", "--password", help="保护密码（可选）")
    
    # 列出密钥
    key_subparsers.add_parser("list", help="列出所有密钥")
    
    # 删除密钥
    del_parser = key_subparsers.add_parser("delete", help="删除密钥")
    del_parser.add_argument("name", nargs='?', help="要删除的密钥名称")
    
    # 解析命令行参数
    args, remaining_args = parser.parse_known_args()
    
    # 显示版本信息
    if args.version:
        from src import __version__
        print(f"文件加密工具 v{__version__}")
        return 0
    
    # 命令行模式
    if args.cli or args.command:
        # 导入CLI功能
        from src.cli import main as cli_main
        return cli_main(args)
    
    # 图形界面模式
    try:
        # 创建应用程序实例
        app = QApplication(sys.argv)
        
        # 设置应用程序样式
        app.setStyle("Fusion")
        
        # 注册应用实例到更新器
        app_updater.register_app(app)
        
        # 获取语言设置
        language = settings.get("ui", "language", "zh_CN")
        translator.switch_language(language)
        logger.info(f"应用语言设置为: {language}")
        
        # 获取主题设置
        theme_name = settings.get("ui", "theme", "light")
        # 确保主题存在，如果不存在则使用light主题
        if theme_name not in theme_manager.get_available_themes():
            theme_name = "light"
            settings.set("ui", "theme", theme_name)
            settings.save_all()
            logger.warning(f"指定的主题不存在，使用默认主题: {theme_name}")
        
        # 直接应用主题，不经过更新器
        theme_manager.apply_theme(theme_name, app)
        logger.info(f"应用主题设置为: {theme_name}")
        
        # 创建并显示主窗口
        window = MainWindow()
        
        # 注册主窗口到更新器
        app_updater.register_widget(window)
        
        # 显示主窗口
        window.show()
        
        # 运行应用程序
        return app.exec_()
    except Exception as e:
        logger.error(f"应用程序运行错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        logger.info("应用程序关闭")

if __name__ == "__main__":
    sys.exit(main()) 