#!/usr/bin/env python3
"""
CNB 集成验证脚本

此脚本验证 CNB API 集成的各个方面：
1. HTTP 客户端创建
2. URL 构建
3. 认证头生成
4. 错误处理
5. 发布数据转换
"""

import subprocess
import json
import sys
from pathlib import Path

def run_command(cmd):
    """运行命令并返回结果"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def test_compilation():
    """测试编译"""
    print("\n" + "="*60)
    print("测试 1: 代码编译")
    print("="*60)
    
    code, stdout, stderr = run_command("cd /workspaces/rio_updater && cargo check --features cnb_releases")
    
    if code == 0:
        print("✅ 编译成功")
        return True
    else:
        print("❌ 编译失败")
        print("错误输出:")
        print(stderr)
        return False

def test_unit_tests():
    """运行单元测试"""
    print("\n" + "="*60)
    print("测试 2: 单元测试")
    print("="*60)
    
    code, stdout, stderr = run_command("cd /workspaces/rio_updater && cargo test --features cnb_releases --lib cnb")
    
    if code == 0:
        # 计算通过的测试数
        lines = stdout.split('\n')
        for line in lines:
            if 'test result:' in line:
                print(f"✅ {line}")
                break
        return True
    else:
        print("❌ 测试失败")
        print("错误输出:")
        print(stderr)
        return False

def test_code_format():
    """检查代码格式"""
    print("\n" + "="*60)
    print("测试 3: 代码格式检查")
    print("="*60)
    
    code, stdout, stderr = run_command("cd /workspaces/rio_updater && cargo fmt --check")
    
    if code == 0:
        print("✅ 代码格式符合标准")
        return True
    else:
        print("❌ 代码格式不符合标准")
        if stdout:
            print("详情:")
            print(stdout)
        return False

def test_clippy():
    """运行 clippy 检查"""
    print("\n" + "="*60)
    print("测试 4: Clippy 严格检查")
    print("="*60)
    
    code, stdout, stderr = run_command("cd /workspaces/rio_updater && cargo clippy --features cnb_releases -- -D warnings")
    
    if code == 0:
        print("✅ Clippy 检查通过（零警告）")
        return True
    else:
        print("❌ Clippy 检查失败")
        print("错误输出:")
        print(stderr[-500:])  # 仅显示最后 500 字符
        return False

def test_release_build():
    """构建发布版本"""
    print("\n" + "="*60)
    print("测试 5: 发布版本构建")
    print("="*60)
    
    code, stdout, stderr = run_command("cd /workspaces/rio_updater && cargo build --release --features cnb_releases 2>&1 | tail -5")
    
    if code == 0:
        print("✅ 发布版本构建成功")
        print(stdout)
        return True
    else:
        print("❌ 发布版本构建失败")
        print("错误输出:")
        print(stderr)
        return False

def check_file_modifications():
    """检查文件修改"""
    print("\n" + "="*60)
    print("测试 6: 文件修改检查")
    print("="*60)
    
    files_to_check = [
        "axoupdater/src/release/cnb.rs",
        "axoupdater/src/release/mod.rs",
        "axoupdater/src/lib.rs",
        "axoupdater/Cargo.toml"
    ]
    
    all_exist = True
    for file in files_to_check:
        path = Path(f"/workspaces/rio_updater/{file}")
        if path.exists():
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 不存在")
            all_exist = False
    
    return all_exist

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("CNB 集成验证脚本")
    print("="*60)
    
    tests = [
        ("代码编译", test_compilation),
        ("单元测试", test_unit_tests),
        ("代码格式", test_code_format),
        ("Clippy 检查", test_clippy),
        ("发布构建", test_release_build),
        ("文件检查", check_file_modifications),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 执行出错: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总体: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Phase 2 开发完成。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
