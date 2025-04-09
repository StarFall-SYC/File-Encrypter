#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RSA非对称加密算法实现
"""

import os
import base64
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from .crypto_base import CryptoBase
from ..utils.logger import logger

class RSACipher(CryptoBase):
    """RSA非对称加密算法实现类"""
    
    def __init__(self, key_size: int = 2048):
        """
        初始化RSA加密算法
        
        Args:
            key_size: 密钥大小，推荐2048位或4096位
        """
        super().__init__(name=f"RSA-{key_size}", 
                        description=f"RSA非对称加密算法，密钥大小{key_size}位")
        
        self.key_size = key_size
        
        # 校验参数
        if key_size < 1024:
            raise ValueError("RSA密钥大小至少需要1024位才能保证安全")
    
    def generate_key(self, **kwargs) -> Dict[str, Any]:
        """
        生成RSA密钥对
        
        Args:
            **kwargs: 其他参数，包括passphrase(密钥密码)
            
        Returns:
            Dict[str, Any]: 包含公钥和私钥的字典
        """
        passphrase = kwargs.get('passphrase', None)
        
        # 生成RSA私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,  # 标准RSA公共指数
            key_size=self.key_size,
            backend=default_backend()
        )
        
        # 获取对应的公钥
        public_key = private_key.public_key()
        
        # 私钥PEM格式序列化
        if passphrase:
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode('utf-8'))
            )
        else:
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        
        # 公钥PEM格式序列化
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        key_dict = {
            'private_key': private_key,
            'public_key': public_key,
            'private_pem': private_pem,
            'public_pem': public_pem,
            'algorithm': self.name,
            'key_size': self.key_size
        }
        
        logger.info(f"生成{self.name}密钥对")
        return key_dict
    
    def load_key(self, public_pem: bytes = None, private_pem: bytes = None, 
                passphrase: str = None) -> Dict[str, Any]:
        """
        从PEM格式字符串加载密钥
        
        Args:
            public_pem: 公钥PEM格式
            private_pem: 私钥PEM格式
            passphrase: 私钥密码
            
        Returns:
            Dict[str, Any]: 包含加载的密钥的字典
        """
        key_dict = {
            'algorithm': self.name,
            'key_size': self.key_size
        }
        
        if private_pem:
            try:
                if passphrase:
                    private_key = serialization.load_pem_private_key(
                        private_pem,
                        password=passphrase.encode('utf-8'),
                        backend=default_backend()
                    )
                else:
                    private_key = serialization.load_pem_private_key(
                        private_pem,
                        password=None,
                        backend=default_backend()
                    )
                key_dict['private_key'] = private_key
                key_dict['private_pem'] = private_pem
                
                # 从私钥获取公钥
                public_key = private_key.public_key()
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                key_dict['public_key'] = public_key
                key_dict['public_pem'] = public_pem
            except Exception as e:
                logger.error(f"加载RSA私钥失败: {str(e)}")
                raise
        
        elif public_pem:
            try:
                public_key = serialization.load_pem_public_key(
                    public_pem,
                    backend=default_backend()
                )
                key_dict['public_key'] = public_key
                key_dict['public_pem'] = public_pem
            except Exception as e:
                logger.error(f"加载RSA公钥失败: {str(e)}")
                raise
        
        return key_dict
    
    def encrypt_data(self, data: bytes, key: bytes, **kwargs) -> bytes:
        """
        使用RSA公钥加密数据
        注意：RSA加密的数据大小有限制，通常不能超过密钥大小减去padding大小
        
        Args:
            data: 待加密的数据
            key: 未使用，应该使用kwargs中的public_key
            **kwargs: 其他参数，包括public_key(公钥对象)或public_pem(公钥PEM格式)
            
        Returns:
            bytes: 加密后的数据
        """
        public_key = kwargs.get('public_key')
        public_pem = kwargs.get('public_pem')
        
        if not public_key and not public_pem:
            raise ValueError("缺少RSA公钥")
        
        try:
            if not public_key and public_pem:
                public_key = serialization.load_pem_public_key(
                    public_pem,
                    backend=default_backend()
                )
            
            # RSA加密数据大小限制 = 密钥大小(字节) - padding开销
            # OAEP padding的开销大约是 2 * hash_size + 2
            max_data_length = self.key_size // 8 - 2 * 32 - 2  # 使用SHA-256哈希
            
            if len(data) > max_data_length:
                raise ValueError(f"数据太大，无法使用RSA直接加密。最大支持{max_data_length}字节")
            
            encrypted_data = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return encrypted_data
        except Exception as e:
            logger.error(f"RSA加密数据失败: {str(e)}")
            raise
    
    def decrypt_data(self, data: bytes, key: bytes, **kwargs) -> bytes:
        """
        使用RSA私钥解密数据
        
        Args:
            data: 待解密的数据
            key: 未使用，应该使用kwargs中的private_key
            **kwargs: 其他参数，包括private_key(私钥对象)或private_pem(私钥PEM格式)和passphrase(密码)
            
        Returns:
            bytes: 解密后的数据
        """
        private_key = kwargs.get('private_key')
        private_pem = kwargs.get('private_pem')
        passphrase = kwargs.get('passphrase')
        
        if not private_key and not private_pem:
            raise ValueError("缺少RSA私钥")
        
        try:
            if not private_key and private_pem:
                if passphrase:
                    private_key = serialization.load_pem_private_key(
                        private_pem,
                        password=passphrase.encode('utf-8') if passphrase else None,
                        backend=default_backend()
                    )
                else:
                    private_key = serialization.load_pem_private_key(
                        private_pem,
                        password=None,
                        backend=default_backend()
                    )
            
            decrypted_data = private_key.decrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted_data
        except Exception as e:
            logger.error(f"RSA解密数据失败: {str(e)}")
            raise
    
    def encrypt_file(self, input_file: str, output_file: str, key: bytes,
                   chunk_size: int = 4096, callback=None, **kwargs) -> bool:
        """
        加密文件（结合AES和RSA）
        由于RSA不适合直接加密大文件，这里采用混合加密：
        1. 生成随机AES密钥
        2. 使用AES加密文件内容
        3. 使用RSA加密AES密钥
        4. 将加密的AES密钥和加密的文件内容一起保存
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            key: 未使用，应该使用kwargs中的public_key
            **kwargs: 其他参数
            
        Returns:
            bool: 加密是否成功
        """
        from .aes import AESCipher
        
        public_key = kwargs.get('public_key')
        public_pem = kwargs.get('public_pem')
        
        if not public_key and not public_pem:
            raise ValueError("缺少RSA公钥")
        
        try:
            # 加载公钥
            if not public_key and public_pem:
                public_key = serialization.load_pem_public_key(
                    public_pem,
                    backend=default_backend()
                )
            
            # 创建AES加密器
            aes = AESCipher(key_size=256, mode='CBC')
            aes_key_dict = aes.generate_key()
            
            # 使用AES加密文件内容
            temp_file = output_file + ".temp"
            aes.encrypt_file(
                input_file, 
                temp_file, 
                aes_key_dict['key'], 
                iv=aes_key_dict['iv'],
                chunk_size=chunk_size,
                callback=callback
            )
            
            # 使用RSA加密AES密钥和IV
            key_data = aes_key_dict['key'] + aes_key_dict['iv']
            encrypted_key = public_key.encrypt(
                key_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # 写入最终加密文件: [RSA加密密钥长度(4字节)][RSA加密的AES密钥数据][AES加密的文件数据]
            with open(output_file, 'wb') as outfile:
                # 写入RSA加密密钥的长度
                outfile.write(len(encrypted_key).to_bytes(4, byteorder='big'))
                # 写入RSA加密的AES密钥
                outfile.write(encrypted_key)
                
                # 写入AES加密的文件内容
                with open(temp_file, 'rb') as tempfile:
                    while True:
                        chunk = tempfile.read(chunk_size)
                        if not chunk:
                            break
                        outfile.write(chunk)
            
            # 删除临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            logger.info(f"使用RSA+AES混合加密文件成功: {input_file} -> {output_file}")
            return True
        except Exception as e:
            logger.error(f"RSA混合加密文件失败: {str(e)}")
            if os.path.exists(output_file + ".temp"):
                os.remove(output_file + ".temp")
            return False
    
    def decrypt_file(self, input_file: str, output_file: str, key: bytes,
                   chunk_size: int = 4096, callback=None, **kwargs) -> bool:
        """
        解密文件（结合AES和RSA）
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            key: 未使用，应该使用kwargs中的private_key
            **kwargs: 其他参数
            
        Returns:
            bool: 解密是否成功
        """
        from .aes import AESCipher
        
        private_key = kwargs.get('private_key')
        private_pem = kwargs.get('private_pem')
        passphrase = kwargs.get('passphrase')
        
        if not private_key and not private_pem:
            raise ValueError("缺少RSA私钥")
        
        try:
            # 加载私钥
            if not private_key and private_pem:
                if passphrase:
                    private_key = serialization.load_pem_private_key(
                        private_pem,
                        password=passphrase.encode('utf-8'),
                        backend=default_backend()
                    )
                else:
                    private_key = serialization.load_pem_private_key(
                        private_pem,
                        password=None,
                        backend=default_backend()
                    )
            
            # 读取加密文件的头部信息
            with open(input_file, 'rb') as infile:
                # 读取RSA加密密钥的长度
                key_length_bytes = infile.read(4)
                if len(key_length_bytes) != 4:
                    raise ValueError("无效的加密文件格式")
                
                key_length = int.from_bytes(key_length_bytes, byteorder='big')
                
                # 读取RSA加密的AES密钥
                encrypted_key = infile.read(key_length)
                if len(encrypted_key) != key_length:
                    raise ValueError("无效的加密文件格式或文件已损坏")
                
                # 使用RSA解密AES密钥和IV
                decrypted_key_data = private_key.decrypt(
                    encrypted_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                # 分离AES密钥和IV
                aes_key = decrypted_key_data[:-16]  # 密钥部分
                aes_iv = decrypted_key_data[-16:]   # IV部分
                
                # 创建AES解密器
                aes = AESCipher(key_size=len(aes_key) * 8, mode='CBC')
                
                # 将剩余的数据写入临时文件
                temp_file = input_file + ".temp"
                with open(temp_file, 'wb') as tempfile:
                    while True:
                        chunk = infile.read(chunk_size)
                        if not chunk:
                            break
                        tempfile.write(chunk)
            
            # 使用AES解密文件内容
            aes.decrypt_file(
                temp_file,
                output_file,
                aes_key,
                iv=aes_iv,
                chunk_size=chunk_size,
                callback=callback
            )
            
            # 删除临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            logger.info(f"使用RSA+AES混合解密文件成功: {input_file} -> {output_file}")
            return True
        except Exception as e:
            logger.error(f"RSA混合解密文件失败: {str(e)}")
            if os.path.exists(input_file + ".temp"):
                os.remove(input_file + ".temp")
            return False 