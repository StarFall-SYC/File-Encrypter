#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
命令行界面模块
"""

import sys
import argparse
import os
from ..crypto.crypto_factory import crypto_factory
from ..crypto.key_manager import key_manager
from ..utils.logger import setup_logger

def main(args=None):
    """命令行应用程序入口点"""
    # 设置日志记录
    logger = setup_logger()
    logger.info("命令行应用程序启动")
    
    try:
        # 如果没有提供args参数，则解析命令行参数
        if args is None:
            # 创建参数解析器
            parser = argparse.ArgumentParser(description="文件加密工具命令行界面")
            
            # 添加子命令
            subparsers = parser.add_subparsers(dest="command", help="可用命令")
            
            # 加密命令
            encrypt_parser = subparsers.add_parser("encrypt", help="加密文件")
            encrypt_parser.add_argument("file", help="要加密的文件路径")
            encrypt_parser.add_argument("-o", "--output", help="输出文件路径")
            encrypt_parser.add_argument("-k", "--key", help="使用的密钥名称")
            encrypt_parser.add_argument("-a", "--algorithm", default="AES-256-CBC", 
                                      help="使用的加密算法")
            encrypt_parser.add_argument("-d", "--delete", action="store_true", 
                                      help="加密后删除原文件")
            
            # 解密命令
            decrypt_parser = subparsers.add_parser("decrypt", help="解密文件")
            decrypt_parser.add_argument("file", help="要解密的文件路径")
            decrypt_parser.add_argument("-o", "--output", help="输出文件路径")
            decrypt_parser.add_argument("-k", "--key", help="使用的密钥名称")
            decrypt_parser.add_argument("-d", "--delete", action="store_true", 
                                      help="解密后删除原文件")
            
            # 密钥管理命令
            key_parser = subparsers.add_parser("key", help="密钥管理")
            key_subparsers = key_parser.add_subparsers(dest="key_command", help="密钥命令")
            
            # 生成密钥
            gen_parser = key_subparsers.add_parser("generate", help="生成新密钥")
            gen_parser.add_argument("name", help="密钥名称")
            gen_parser.add_argument("-a", "--algorithm", default="AES-256-CBC", 
                                  help="加密算法")
            gen_parser.add_argument("-p", "--password", help="保护密码（可选）")
            
            # 列出密钥
            list_parser = key_subparsers.add_parser("list", help="列出所有密钥")
            
            # 删除密钥
            del_parser = key_subparsers.add_parser("delete", help="删除密钥")
            del_parser.add_argument("name", help="要删除的密钥名称")
            
            # 解析命令行参数
            args = parser.parse_args()
        
        # 如果没有指定命令，显示帮助信息
        if not args.command:
            if 'parser' in locals():
                parser.print_help()
            else:
                print("使用: encrypt|decrypt|key [选项]")
            return 0
        
        # 处理各种命令
        if args.command == "encrypt":
            # 实现加密逻辑
            success = encrypt_file(args)
            return 0 if success else 1
        elif args.command == "decrypt":
            # 实现解密逻辑
            success = decrypt_file(args)
            return 0 if success else 1
        elif args.command == "key":
            if not args.key_command:
                key_parser.print_help()
                return 0
                
            if args.key_command == "generate":
                # 实现生成密钥逻辑
                success = generate_key(args)
                return 0 if success else 1
            elif args.key_command == "list":
                # 实现列出密钥逻辑
                list_keys()
                return 0
            elif args.key_command == "delete":
                # 实现删除密钥逻辑
                success = delete_key(args)
                return 0 if success else 1
        
        return 0
    except Exception as e:
        logger.error(f"命令行应用程序错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    finally:
        logger.info("命令行应用程序关闭")


def encrypt_file(args):
    """
    加密文件
    
    Args:
        args: 命令行参数
        
    Returns:
        bool: 加密是否成功
    """
    logger = setup_logger()
    input_file = args.file
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        logger.error(f"输入文件不存在: {input_file}")
        return False
    
    # 确定输出文件路径
    if args.output:
        output_file = args.output
    else:
        output_file = f"{input_file}.enc"
    
    # 获取加密算法
    algorithm = args.algorithm
    crypto = crypto_factory.create_algorithm(algorithm)
    if not crypto:
        logger.error(f"不支持的加密算法: {algorithm}")
        return False
    
    try:
        # 获取密钥
        if args.key:
            # 使用已保存的密钥
            key_data = key_manager.load_key(args.key)
            if not key_data:
                logger.error(f"无法加载密钥: {args.key}")
                return False
            
            if 'key' in key_data:
                key = key_data['key']
                iv = key_data.get('iv')
            else:
                logger.error(f"密钥格式无效: {args.key}")
                return False
        else:
            # 生成临时密钥
            key_data = crypto.generate_key()
            key = key_data['key']
            iv = key_data.get('iv')
            
            # 保存生成的密钥
            key_name = f"temp_{os.path.basename(input_file)}"
            key_manager.save_key(key_data, key_name)
            logger.info(f"已生成临时密钥: {key_name}")
            print(f"已生成临时密钥: {key_name}")
        
        # 加密文件
        logger.info(f"开始加密文件: {input_file} -> {output_file}")
        print(f"开始加密文件: {input_file} -> {output_file}")
        
        kwargs = {}
        if iv:
            kwargs['iv'] = iv
        
        success = crypto.encrypt_file(input_file, output_file, key, **kwargs)
        
        if success:
            logger.info(f"文件加密成功: {output_file}")
            print(f"文件加密成功: {output_file}")
            
            # 如果指定了删除原文件
            if args.delete and success:
                try:
                    os.remove(input_file)
                    logger.info(f"已删除原文件: {input_file}")
                    print(f"已删除原文件: {input_file}")
                except Exception as e:
                    logger.warning(f"无法删除原文件: {str(e)}")
                    print(f"警告: 无法删除原文件: {str(e)}")
        
        return success
    
    except Exception as e:
        logger.error(f"加密过程出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def decrypt_file(args):
    """
    解密文件
    
    Args:
        args: 命令行参数
        
    Returns:
        bool: 解密是否成功
    """
    logger = setup_logger()
    input_file = args.file
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        logger.error(f"输入文件不存在: {input_file}")
        return False
    
    # 确定输出文件路径
    if args.output:
        output_file = args.output
    else:
        # 默认去掉.enc后缀
        output_file = input_file
        if output_file.endswith('.enc'):
            output_file = output_file[:-4]
        else:
            output_file = f"{output_file}.dec"
    
    # 获取密钥
    if not args.key:
        logger.error("解密需要提供密钥名称")
        print("错误: 解密需要提供密钥名称，请使用-k或--key参数")
        return False
    
    key_data = key_manager.load_key(args.key)
    if not key_data:
        logger.error(f"无法加载密钥: {args.key}")
        return False
    
    # 获取加密算法
    algorithm = key_data.get('algorithm', 'AES-256-CBC')
    crypto = crypto_factory.create_algorithm(algorithm)
    if not crypto:
        logger.error(f"不支持的加密算法: {algorithm}")
        return False
    
    try:
        # 准备解密数据
        if 'key' in key_data:
            key = key_data['key']
        else:
            logger.error(f"密钥格式无效: {args.key}")
            return False
        
        kwargs = {}
        if 'iv' in key_data:
            kwargs['iv'] = key_data['iv']
        
        # 解密文件
        logger.info(f"开始解密文件: {input_file} -> {output_file}")
        print(f"开始解密文件: {input_file} -> {output_file}")
        
        success = crypto.decrypt_file(input_file, output_file, key, **kwargs)
        
        if success:
            logger.info(f"文件解密成功: {output_file}")
            print(f"文件解密成功: {output_file}")
            
            # 如果指定了删除原文件
            if args.delete and success:
                try:
                    os.remove(input_file)
                    logger.info(f"已删除加密文件: {input_file}")
                    print(f"已删除加密文件: {input_file}")
                except Exception as e:
                    logger.warning(f"无法删除加密文件: {str(e)}")
                    print(f"警告: 无法删除加密文件: {str(e)}")
        
        return success
    
    except Exception as e:
        logger.error(f"解密过程出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def generate_key(args):
    """
    生成新密钥
    
    Args:
        args: 命令行参数
        
    Returns:
        bool: 是否成功
    """
    logger = setup_logger()
    key_name = args.name
    algorithm = args.algorithm
    password = args.password
    
    try:
        # 创建加密算法实例
        crypto = crypto_factory.create_algorithm(algorithm)
        if not crypto:
            logger.error(f"不支持的加密算法: {algorithm}")
            print(f"错误: 不支持的加密算法: {algorithm}")
            return False
        
        # 生成密钥
        key_data = crypto.generate_key()
        
        # 保存密钥
        key_file = key_manager.save_key(key_data, key_name, password)
        
        logger.info(f"密钥已生成并保存: {key_file}")
        print(f"密钥 '{key_name}' 已生成并保存至 {key_file}")
        
        if password:
            print("密钥已使用密码加密保护")
        
        return True
    
    except Exception as e:
        logger.error(f"生成密钥出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def list_keys():
    """列出所有可用密钥"""
    logger = setup_logger()
    
    try:
        keys = key_manager.list_keys()
        
        if not keys:
            print("没有找到密钥")
            return
        
        print("\n可用密钥:")
        print("=" * 50)
        print(f"{'名称':<20} {'算法':<15} {'加密保护':<10}")
        print("-" * 50)
        
        for name, info in keys.items():
            encrypted = "是" if info.get("is_encrypted") else "否"
            algorithm = info.get("algorithm", "未知")
            print(f"{name:<20} {algorithm:<15} {encrypted:<10}")
        
        print("=" * 50)
        print(f"共找到 {len(keys)} 个密钥")
        
    except Exception as e:
        logger.error(f"列出密钥出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def delete_key(args):
    """
    删除密钥
    
    Args:
        args: 命令行参数
        
    Returns:
        bool: 是否成功
    """
    logger = setup_logger()
    key_name = args.name
    
    try:
        # 确认密钥存在
        keys = key_manager.list_keys()
        if key_name not in keys:
            logger.error(f"密钥不存在: {key_name}")
            print(f"错误: 密钥 '{key_name}' 不存在")
            return False
        
        # 删除密钥
        success = key_manager.delete_key(key_name)
        
        if success:
            logger.info(f"密钥已删除: {key_name}")
            print(f"密钥 '{key_name}' 已成功删除")
        else:
            logger.error(f"无法删除密钥: {key_name}")
            print(f"错误: 无法删除密钥 '{key_name}'")
        
        return success
    
    except Exception as e:
        logger.error(f"删除密钥出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False 