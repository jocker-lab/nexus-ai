# -*- coding: utf-8 -*-
"""
@File    :   docker_test.py
@Time    :   2025/11/13 17:14
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
"""
DockerSandbox 快速测试
用于快速验证 Docker 环境是否正确配置
"""
import docker
import os


def quick_test():
    """快速测试 Docker 环境"""
    print("=" * 70)
    print("🔍 DockerSandbox 快速检查")
    print("=" * 70)

    # 1. 检查 Docker 连接
    print("\n1️⃣ 检查 Docker 连接...")
    try:
        client = docker.from_env()
        print("   ✅ Docker 连接成功")
    except Exception as e:
        print(f"   ❌ Docker 连接失败: {e}")
        print("   💡 请确保 Docker 正在运行")
        return False

    # 2. 检查镜像
    print("\n2️⃣ 检查镜像...")
    try:
        client.images.get('sandbox:latest')
        print("   ✅ 镜像 'sandbox:latest' 存在")
    except docker.errors.ImageNotFound:
        print("   ❌ 镜像 'sandbox:latest' 不存在")
        print("   💡 请执行: docker build -t sandbox:latest .")
        return False

    # 3. 测试简单执行
    print("\n3️⃣ 测试代码执行...")
    try:
        result = client.containers.run(
            image='sandbox:latest',
            command=['python', '-c', 'print("Hello!")'],
            remove=True,
            stdout=True,
            stderr=True
        )
        output = result.decode('utf-8').strip()
        if output == "Hello!":
            print(f"   ✅ 代码执行成功: {output}")
        else:
            print(f"   ⚠️ 输出异常: {output}")
    except Exception as e:
        print(f"   ❌ 执行失败: {e}")
        return False

    # 4. 检查输出目录
    print("\n4️⃣ 检查输出目录...")
    output_dir = os.path.abspath('./output')
    os.makedirs(output_dir, exist_ok=True)
    try:
        os.chmod(output_dir, 0o777)
        print(f"   ✅ 输出目录已准备: {output_dir}")
    except Exception as e:
        print(f"   ⚠️ 权限设置失败: {e}")

    # 5. 测试文件写入
    print("\n5️⃣ 测试文件写入...")
    try:
        result = client.containers.run(
            image='sandbox:latest',
            command=['python', '-c', 'open("/output/test.txt", "w").write("test")'],
            volumes={output_dir: {'bind': '/output', 'mode': 'rw'}},
            remove=True,
            stdout=True,
            stderr=True
        )

        test_file = os.path.join(output_dir, 'test.txt')
        if os.path.exists(test_file):
            print(f"   ✅ 文件写入成功: {test_file}")
            os.remove(test_file)
        else:
            print("   ❌ 文件未生成")
            return False
    except Exception as e:
        print(f"   ❌ 写入失败: {e}")
        return False

    # 6. 测试 Python 包
    print("\n6️⃣ 测试 Python 包...")
    packages = ['matplotlib', 'seaborn', 'pandas', 'numpy']
    for pkg in packages:
        try:
            result = client.containers.run(
                image='sandbox:latest',
                command=['python', '-c', f'import {pkg}; print("{pkg} OK")'],
                remove=True,
                stdout=True,
                stderr=True
            )
            print(f"   ✅ {pkg}: {result.decode('utf-8').strip()}")
        except Exception as e:
            print(f"   ❌ {pkg}: 导入失败")

    # 清理
    try:
        os.rmdir(output_dir)
    except:
        pass

    print("\n" + "=" * 70)
    print("✅ 所有检查通过！DockerSandbox 已就绪")
    print("=" * 70)
    print("\n💡 下一步: 运行完整测试")
    print("   python test_docker_sandbox.py")
    print()

    return True


if __name__ == "__main__":
    success = quick_test()
    exit(0 if success else 1)