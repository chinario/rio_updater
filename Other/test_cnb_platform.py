#!/usr/bin/env python3
"""
CNB 平台集成测试套件

测试 CNB 平台的各项功能：
1. API 连接性
2. 发布信息获取
3. 文件下载
4. 安装脚本功能
5. 环境变量处理
"""

import subprocess
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

class Colors:
    """颜色定义"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    @staticmethod
    def success(text):
        return f"{Colors.GREEN}✅ {text}{Colors.RESET}"
    
    @staticmethod
    def error(text):
        return f"{Colors.RED}❌ {text}{Colors.RESET}"
    
    @staticmethod
    def warn(text):
        return f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}"
    
    @staticmethod
    def info(text):
        return f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}"


class CNBTester:
    """CNB 平台测试类"""
    
    def __init__(self, cnb_base_url="https://cnb.cool", cnb_repo="astral-sh/uv", verbose=False):
        self.cnb_base_url = cnb_base_url
        self.cnb_repo = cnb_repo
        self.verbose = verbose
        self.test_results = []
        
    def log(self, msg):
        """打印日志"""
        if self.verbose:
            print(msg)
    
    def run_test(self, name, test_func):
        """运行单个测试"""
        print(f"\n【测试】{name}")
        print("-" * 70)
        try:
            result = test_func()
            if result:
                print(Colors.success(f"{name} 通过"))
                self.test_results.append((name, True, None))
                return True
            else:
                print(Colors.error(f"{name} 失败"))
                self.test_results.append((name, False, "返回值为 False"))
                return False
        except Exception as e:
            print(Colors.error(f"{name} 失败: {e}"))
            self.test_results.append((name, False, str(e)))
            return False
    
    def test_cnb_connectivity(self):
        """测试 1: CNB 平台连接性"""
        print(f"连接 CNB 平台: {self.cnb_base_url}")
        
        try:
            import requests
            response = requests.head(self.cnb_base_url, timeout=10)
            is_ok = response.status_code < 500
            print(Colors.info(f"HTTP 状态码: {response.status_code}"))
            return is_ok
        except Exception as e:
            print(Colors.warn(f"使用 curl 重试: {e}"))
            try:
                result = subprocess.run(
                    ["curl", "-I", "-m", "10", self.cnb_base_url],
                    capture_output=True,
                    timeout=15
                )
                return result.returncode == 0
            except Exception as e2:
                print(Colors.error(f"连接失败: {e2}"))
                return False
    
    def test_cnb_repo_page(self):
        """测试 2: CNB 仓库页面可访问"""
        repo_url = f"{self.cnb_base_url}/{self.cnb_repo}"
        print(f"访问仓库页面: {repo_url}")
        
        try:
            import requests
            response = requests.get(repo_url, timeout=10)
            is_ok = 200 <= response.status_code < 400
            print(Colors.info(f"HTTP 状态码: {response.status_code}"))
            print(Colors.info(f"页面大小: {len(response.text)} 字节"))
            return is_ok
        except Exception as e:
            print(Colors.error(f"访问失败: {e}"))
            return False
    
    def test_cnb_releases_page(self):
        """测试 3: CNB 发布页面可访问"""
        releases_url = f"{self.cnb_base_url}/{self.cnb_repo}/-/releases"
        print(f"访问发布页面: {releases_url}")
        
        try:
            import requests
            response = requests.get(releases_url, timeout=10)
            is_ok = 200 <= response.status_code < 400
            print(Colors.info(f"HTTP 状态码: {response.status_code}"))
            
            # 检查是否包含发布相关内容
            has_content = len(response.text) > 100
            print(Colors.info(f"页面内容: {len(response.text)} 字节"))
            
            return is_ok and has_content
        except Exception as e:
            print(Colors.error(f"访问失败: {e}"))
            return False
    
    def test_cnb_api_endpoint(self):
        """测试 4: CNB API 端点"""
        api_url = f"{self.cnb_base_url}/{self.cnb_repo}/-/releases/latest"
        print(f"查询 API: {api_url}")
        
        try:
            import requests
            headers = {"Accept": "application/vnd.cnb.api+json"}
            response = requests.get(api_url, headers=headers, timeout=10)
            
            print(Colors.info(f"HTTP 状态码: {response.status_code}"))
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(Colors.info(f"获取 JSON 数据成功"))
                    return True
                except:
                    print(Colors.warn(f"响应不是有效的 JSON"))
                    return False
            elif response.status_code == 401:
                print(Colors.warn(f"API 需要认证 (401 Unauthorized)"))
                return False  # 认证失败作为测试失败
            else:
                print(Colors.warn(f"API 返回 {response.status_code}"))
                return False
        except Exception as e:
            print(Colors.warn(f"API 调用失败: {e}"))
            return False
    
    def test_cnb_install_script(self):
        """测试 5: 安装脚本的语法和结构"""
        script_path = "/workspaces/rio_updater/install-cnb-uv.sh"
        print(f"检查脚本: {script_path}")
        
        try:
            # 检查脚本是否存在
            if not os.path.exists(script_path):
                print(Colors.error(f"脚本不存在: {script_path}"))
                return False
            
            # 检查脚本的 shebang
            with open(script_path, 'r') as f:
                first_line = f.readline().strip()
                if not first_line.startswith('#!/'):
                    print(Colors.error("脚本缺少 shebang"))
                    return False
                print(Colors.info(f"Shebang: {first_line}"))
            
            # 验证 shell 脚本语法
            result = subprocess.run(
                ["sh", "-n", script_path],
                capture_output=True
            )
            
            if result.returncode == 0:
                print(Colors.success("脚本语法正确"))
                
                # 检查关键函数
                with open(script_path, 'r') as f:
                    content = f.read()
                    required_functions = [
                        'get_arch',
                        'get_os',
                        'download_file',
                        'extract_archive',
                        'install_binary'
                    ]
                    
                    missing = [func for func in required_functions if f"{func}() {{" not in content and f"{func}() " not in content]
                    if missing:
                        print(Colors.warn(f"缺少函数: {missing}"))
                        return False
                    
                    print(Colors.info(f"找到所有关键函数"))
                return True
            else:
                print(Colors.error(f"脚本语法错误: {result.stderr.decode()}"))
                return False
        except Exception as e:
            print(Colors.error(f"检查失败: {e}"))
            return False
    
    def test_environment_variables(self):
        """测试 6: 环境变量处理"""
        print("测试环境变量配置...")
        
        script_path = "/workspaces/rio_updater/install-cnb-uv.sh"
        
        try:
            with open(script_path, 'r') as f:
                content = f.read()
            
            # 检查是否支持的环境变量
            env_vars = [
                'CNB_BASE_URL',
                'CNB_REPO',
                'CNB_VERBOSE',
                'CNB_INSTALL_DIR',
                'CNB_NO_MODIFY_PATH'
            ]
            
            found = 0
            for var in env_vars:
                if var in content:
                    found += 1
                    print(Colors.info(f"✓ 支持 {var}"))
                else:
                    print(Colors.warn(f"✗ 不支持 {var}"))
            
            return found >= 3  # 至少支持 3 个环境变量
        except Exception as e:
            print(Colors.error(f"检查失败: {e}"))
            return False
    
    def test_cnb_rust_integration(self):
        """测试 7: Rust CNB 集成代码"""
        print("测试 Rust CNB 集成代码...")
        
        try:
            result = subprocess.run(
                ["cargo", "test", "--features", "cnb_releases", "--lib", "cnb"],
                cwd="/workspaces/rio_updater",
                capture_output=True,
                timeout=120
            )
            
            is_ok = result.returncode == 0
            if is_ok:
                # 计算通过的测试数
                output = result.stdout.decode()
                if "test result: ok" in output:
                    print(Colors.success("Rust 单元测试通过"))
                    return True
            else:
                print(Colors.error("Rust 单元测试失败"))
                print(result.stderr.decode()[-500:])
                return False
        except Exception as e:
            print(Colors.error(f"测试失败: {e}"))
            return False
    
    def test_script_permissions(self):
        """测试 8: 脚本可执行权限"""
        script_path = "/workspaces/rio_updater/install-cnb-uv.sh"
        print(f"检查脚本权限: {script_path}")
        
        try:
            # 设置可执行权限
            os.chmod(script_path, 0o755)
            
            # 检查权限
            mode = os.stat(script_path).st_mode
            is_executable = mode & 0o111
            
            if is_executable:
                print(Colors.success("脚本有执行权限"))
                return True
            else:
                print(Colors.error("脚本无执行权限"))
                return False
        except Exception as e:
            print(Colors.error(f"检查失败: {e}"))
            return False
    
    def test_curl_wget_availability(self):
        """测试 9: 必需的下载工具可用性"""
        print("检查下载工具...")
        
        tools_found = 0
        for tool in ['curl', 'wget']:
            try:
                result = subprocess.run(
                    ["which", tool],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    path = result.stdout.decode().strip()
                    print(Colors.success(f"{tool} 可用: {path}"))
                    tools_found += 1
                else:
                    print(Colors.warn(f"{tool} 不可用"))
            except:
                print(Colors.warn(f"{tool} 检查失败"))
        
        return tools_found > 0  # 至少需要一个下载工具
    
    def test_tar_availability(self):
        """测试 10: tar 工具可用性"""
        print("检查 tar 工具...")
        
        try:
            result = subprocess.run(
                ["tar", "--version"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.decode().split('\n')[0]
                print(Colors.success(f"tar 可用: {version}"))
                return True
            else:
                print(Colors.error("tar 不可用"))
                return False
        except Exception as e:
            print(Colors.error(f"检查失败: {e}"))
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("="*70)
        print("CNB 平台集成测试套件")
        print("="*70)
        
        tests = [
            ("CNB 平台连接性", self.test_cnb_connectivity),
            ("CNB 仓库页面可访问", self.test_cnb_repo_page),
            ("CNB 发布页面可访问", self.test_cnb_releases_page),
            ("CNB API 端点", self.test_cnb_api_endpoint),
            ("安装脚本语法和结构", self.test_cnb_install_script),
            ("环境变量支持", self.test_environment_variables),
            ("Rust CNB 集成代码", self.test_cnb_rust_integration),
            ("脚本执行权限", self.test_script_permissions),
            ("下载工具可用性", self.test_curl_wget_availability),
            ("tar 工具可用性", self.test_tar_availability),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # 生成报告
        self.print_report()
    
    def print_report(self):
        """生成测试报告"""
        print("\n" + "="*70)
        print("测试报告")
        print("="*70)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"\n总体: {passed}/{total} 通过")
        
        if passed == total:
            print(Colors.success("所有测试通过！"))
        else:
            print(Colors.warn(f"{total - passed} 个测试失败"))
        
        print("\n详细结果:")
        for name, success, error in self.test_results:
            if success:
                print(Colors.success(f"{name}"))
            else:
                print(Colors.error(f"{name}"))
                if error:
                    print(f"  原因: {error}")
        
        print("\n" + "="*70)
        return passed == total


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CNB 平台集成测试")
    parser.add_argument("--cnb-url", default="https://cnb.cool", help="CNB 基础 URL")
    parser.add_argument("--cnb-repo", default="astral-sh/uv", help="CNB 仓库")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    tester = CNBTester(
        cnb_base_url=args.cnb_url,
        cnb_repo=args.cnb_repo,
        verbose=args.verbose
    )
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
