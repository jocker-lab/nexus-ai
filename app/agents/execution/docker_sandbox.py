# -*- coding: utf-8 -*-
"""
@File    :   DockerSandbox.py
@Time    :   2025/11/13 16:11
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
import docker
import os
import tempfile
from pathlib import Path

class DockerSandbox:
    """Docker 沙箱 - 非 root 用户版本"""

    def __init__(
            self,
            output_dir: str = 'charts',
            image: str = 'sandbox:latest',
            mem_limit: str = '512m',
            cpu_quota: int = 50000
    ):
        self.client = docker.from_env()
        self.image = image
        self.output_dir = os.path.abspath(output_dir)
        self.mem_limit = mem_limit
        self.cpu_quota = cpu_quota

        # 创建输出目录，并设置权限（重要！）
        os.makedirs(self.output_dir, exist_ok=True)
        # 确保 Docker 容器中的 sandbox 用户（UID 1000）可以写入
        try:
            os.chmod(self.output_dir, 0o777)  # 或者 chown 到 1000:1000
        except:
            pass

        self._ensure_image()

    def _ensure_image(self):
        """确保 Docker 镜像存在"""
        try:
            self.client.images.get(self.image)
            print(f"✅ 镜像已存在: {self.image}")
        except docker.errors.ImageNotFound:
            print(f"❌ 镜像不存在: {self.image}")
            print(f"请先构建镜像: docker build -t {self.image} .")
            raise

    def execute(
            self,
            code: str,
            timeout: int = 120,
            enable_network: bool = False
    ) -> str:
        """在 Docker 容器中安全执行代码"""
        temp_dir = Path(tempfile.mkdtemp())
        code_file = temp_dir / "script.py"

        try:
            code_file.write_text(code, encoding='utf-8')

            # ⭐ 关键：容器会以 sandbox 用户（UID 1000）运行
            result = self.client.containers.run(
                image=self.image,
                command=['python', '/workspace/script.py'],
                volumes={
                    str(temp_dir): {'bind': '/workspace', 'mode': 'ro'},
                    self.output_dir: {'bind': '/output', 'mode': 'rw'}
                },
                working_dir='/output',
                remove=True,
                mem_limit=self.mem_limit,
                cpu_period=100000,
                cpu_quota=self.cpu_quota,
                network_disabled=not enable_network,
                stdout=True,
                stderr=True,
                detach=False,
                # 不需要显式指定 user，镜像中已经设置为 sandbox
            )

            return result.decode('utf-8')

        except docker.errors.ContainerError as e:
            return f"❌ 代码执行错误:\n{e.stderr.decode('utf-8')}"
        except Exception as e:
            error_msg = str(e)
            return f"❌ Docker 错误: {error_msg}"
        finally:
            try:
                code_file.unlink()
                temp_dir.rmdir()
            except:
                pass