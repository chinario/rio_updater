#!/usr/bin/env python3
"""
CNB 集成测试 - 以 astral-sh/uv 为测试对象

此脚本测试 CNB 平台的 uv 项目发布信息获取和下载功能
"""

import requests
import json
import os
import tarfile
import stat
from pathlib import Path

def test_cnb_uv_release():
    """从 CNB 获取 uv 的最新发布信息"""
    
    print("="*60)
    print("CNB 集成测试 - astral-sh/uv")
    print("="*60)
    
    # CNB API 端点
    api_base = "https://api.cnb.cool"
    repo = "astral-sh/uv"
    
    # 设置请求头
    headers = {
        "Accept": "application/vnd.cnb.api+json",
    }
    
    # 1. 获取最新发布信息
    print("\n1. 从 CNB 获取最新发布信息...")
    latest_url = f"{api_base}/{repo}/-/releases/latest"
    
    try:
        response = requests.get(latest_url, headers=headers, timeout=30)
        response.raise_for_status()
        release_data = response.json()
        
        print(f"✓ 获取成功")
        print(f"  版本: {release_data.get('tag_name', 'N/A')}")
        print(f"  名称: {release_data.get('name', 'N/A')}")
        print(f"  发布时间: {release_data.get('created_at', 'N/A')}")
        
        # 获取发布信息
        tag = release_data.get('tag_name')
        assets = release_data.get('assets', [])
        
    except Exception as e:
        print(f"✗ 获取失败: {e}")
        return False
    
    # 2. 找到 Linux x86_64 的二进制文件
    print(f"\n2. 寻找 Linux x86_64 二进制文件...")
    linux_asset = None
    
    for asset in assets:
        name = asset.get('name', '')
        if 'linux' in name and 'x86_64' in name and not name.endswith('.sha256'):
            linux_asset = asset
            print(f"✓ 找到: {name}")
            print(f"  大小: {asset.get('size', 'N/A')} bytes")
            break
    
    if not linux_asset:
        print(f"✗ 没有找到 Linux x86_64 的二进制文件")
        print(f"  可用的文件:")
        for asset in assets:
            print(f"    - {asset.get('name')}")
        return False
    
    # 3. 下载二进制文件
    print(f"\n3. 下载 uv 二进制文件...")
    
    download_url = linux_asset.get('browser_download_url')
    filename = linux_asset.get('name')
    
    try:
        print(f"  从: {download_url}")
        response = requests.get(download_url, timeout=60)
        response.raise_for_status()
        
        # 保存文件
        download_dir = Path("/tmp/cnb_uv_test")
        download_dir.mkdir(exist_ok=True)
        file_path = download_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ 下载完成: {file_path}")
        print(f"  大小: {len(response.content)} bytes")
        
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return False
    
    # 4. 提取和安装二进制文件
    print(f"\n4. 提取二进制文件...")
    
    try:
        if filename.endswith('.tar.gz'):
            with tarfile.open(file_path, 'r:gz') as tar:
                tar.extractall(path=download_dir)
                print(f"✓ 提取完成")
                
                # 找到 uv 可执行文件
                members = tar.getnames()
                for member in members:
                    if member.endswith('/uv') or member == 'uv':
                        uv_path = download_dir / member
                        print(f"  找到可执行文件: {member}")
                        break
        else:
            print(f"⚠ 未知的文件格式: {filename}")
            return False
            
    except Exception as e:
        print(f"✗ 提取失败: {e}")
        return False
    
    # 5. 安装到系统路径
    print(f"\n5. 安装 uv 到系统...")
    
    try:
        # 找到提取出的 uv 文件
        uv_extracted = None
        for root, dirs, files in os.walk(download_dir):
            if 'uv' in files:
                uv_extracted = os.path.join(root, 'uv')
                break
        
        if uv_extracted:
            # 复制到 /usr/local/bin
            import shutil
            install_path = "/usr/local/bin/uv"
            
            # 检查权限
            if os.access(uv_extracted, os.X_OK):
                shutil.copy2(uv_extracted, install_path)
                # 确保可执行
                os.chmod(install_path, os.stat(install_path).st_mode | stat.S_IEXEC)
                print(f"✓ 安装成功: {install_path}")
            else:
                print(f"⚠ 文件不可执行: {uv_extracted}")
                # 强制设置为可执行
                os.chmod(uv_extracted, 0o755)
                shutil.copy2(uv_extracted, install_path)
                os.chmod(install_path, 0o755)
                print(f"✓ 安装成功（设置了执行权限）")
        else:
            print(f"✗ 没有找到 uv 可执行文件")
            return False
            
    except Exception as e:
        print(f"⚠ 安装到系统路径失败: {e}")
        print(f"  但文件已下载到: {download_dir}")
    
    # 6. 验证安装
    print(f"\n6. 验证 uv 安装...")
    
    try:
        result = os.popen("uv --version 2>&1").read()
        if "error" not in result.lower() and result.strip():
            print(f"✓ 验证成功")
            print(f"  版本信息: {result.strip()}")
            return True
        else:
            print(f"⚠ uv 命令可用但输出异常")
            return False
            
    except Exception as e:
        print(f"⚠ 验证失败: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CNB.cool 平台集成测试")
    print("测试对象: astral-sh/uv 项目")
    print("="*60)
    
    success = test_cnb_uv_release()
    
    print("\n" + "="*60)
    if success:
        print("✓ 测试通过！uv 已成功安装")
    else:
        print("⚠ 测试过程中遇到问题")
    print("="*60 + "\n")
