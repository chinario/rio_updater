# CNB 平台安装脚本快速参考

## 文件清单

| 文件 | 功能 | 行数 |
|------|------|------|
| `install-cnb-uv.sh` | 安装脚本 | 570+ |
| `test_cnb_platform.py` | 测试套件 | 350+ |
| `CNB_INSTALLER_GUIDE.md` | 完整文档 | 本文件 |

## 快速命令

### 安装 uv（最简单的方式）

```bash
sh /workspaces/rio_updater/install-cnb-uv.sh
```

**输出:**
```
✅ uv 已安装到 ~/.local/bin/uv
```

### 验证 CNB 平台

```bash
python3 /workspaces/rio_updater/test_cnb_platform.py
```

**预期:**
```
总体: 10/10 通过 ✅
```

## 环境变量速查

```bash
# 安装到自定义位置
CNB_INSTALL_DIR=/opt/tools sh install-cnb-uv.sh

# 启用详细输出
CNB_VERBOSE=1 sh install-cnb-uv.sh

# 不修改 PATH
CNB_NO_MODIFY_PATH=1 sh install-cnb-uv.sh

# 使用不同的 CNB 实例
CNB_BASE_URL=https://internal-cnb.com sh install-cnb-uv.sh
```

## 10 项测试说明

| # | 测试 | 检查内容 |
|----|------|---------|
| 1 | CNB 连接 | 服务器是否可访问 |
| 2 | 仓库页面 | 仓库页面能否打开 |
| 3 | 发布页面 | 发布列表能否加载 |
| 4 | API 端点 | API 能否返回 JSON |
| 5 | 脚本语法 | 脚本是否有效 |
| 6 | 环境变量 | 脚本是否支持 5 个环境变量 |
| 7 | Rust 集成 | Rust 单元测试是否通过 |
| 8 | 脚本权限 | 脚本是否可执行 |
| 9 | 下载工具 | curl/wget 是否可用 |
| 10 | tar 工具 | tar 是否可用 |

## 常见任务

### 任务 1: 为团队部署安装脚本

```bash
# 1. 验证脚本
python3 test_cnb_platform.py -v

# 2. 部署脚本
cp install-cnb-uv.sh /usr/local/bin/
chmod 755 /usr/local/bin/install-cnb-uv.sh

# 3. 创建文档
cp CNB_INSTALLER_GUIDE.md /usr/local/share/doc/

# 4. 测试部署
sh /usr/local/bin/install-cnb-uv.sh --version
```

### 任务 2: 设置 CI/CD 集成

```bash
# GitHub Actions 示例
name: Verify CNB uv Installer
on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test CNB installer
        run: python3 test_cnb_platform.py
      - name: Test uv installation
        run: sh install-cnb-uv.sh && uv --version
```

### 任务 3: 监控 CNB 平台

```bash
# 创建监控脚本
#!/bin/bash
python3 test_cnb_platform.py > /tmp/cnb-test.log 2>&1
if [ $? -ne 0 ]; then
    # 发送告警
    echo "CNB platform test failed!" | mail -s "Alert" admin@example.com
fi
```

### 任务 4: 调试安装问题

```bash
# 启用详细输出
CNB_VERBOSE=1 sh install-cnb-uv.sh

# 保存日志
sh install-cnb-uv.sh 2>&1 | tee install.log

# 检查临时文件
ls -la /tmp/ | grep -i uv

# 验证安装
type uv
uv --version
```

## 系统要求

| 要求 | 版本/说明 |
|------|----------|
| Shell | POSIX sh (bash, zsh, dash, ksh) |
| 下载工具 | curl 或 wget |
| 压缩工具 | tar (GNU 或 BSD) |
| 操作系统 | Linux 或 macOS |
| 架构 | x86_64 或 aarch64 |
| Python (测试) | 3.6+ |

## 诊断命令

```bash
# 检查 shell 兼容性
sh -n install-cnb-uv.sh

# 检查网络连接
curl -I https://cnb.cool

# 检查 API 端点
curl https://cnb.cool/astral-sh/uv/-/releases/latest

# 检查工具可用性
which curl wget tar

# 检查系统信息
uname -s -m
```

## 性能提示

- 脚本平均执行时间: < 5 分钟
- 测试套件平均执行时间: < 1 分钟
- 网络延迟影响最大

## 许可证和致谢

- 参照设计: [astral-sh/uv/install.sh](https://astral.sh/uv/install.sh)
- 平台: [CNB.cool](https://cnb.cool)
- 项目: rio_updater

## 获取帮助

### 查看脚本文档

```bash
# 脚本顶部注释
head -n 50 install-cnb-uv.sh

# 函数说明
grep -A 5 "^.*().*{" install-cnb-uv.sh
```

### 运行测试获取详细信息

```bash
# 详细输出
python3 test_cnb_platform.py -v

# 显示每个测试的详细信息
python3 test_cnb_platform.py --verbose
```

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `curl: command not found` | curl 未安装 | `apt install curl` |
| `tar: command not found` | tar 未安装 | `apt install tar` |
| `Permission denied` | 目录权限不足 | 使用 `CNB_INSTALL_DIR=$HOME/bin` |
| `Network error` | 网络问题 | 检查网络连接和防火墙 |
| `API failed` | API 不可用 | 脚本会自动使用备用方法 |

## 更新日志

### v1.0.0 (2025-01-11)
- 初始版本
- 10 项 CNB 平台测试
- 完整安装脚本
- 详细文档

---

**快速链接:**
- [完整使用指南](CNB_INSTALLER_GUIDE.md)
- [GitHub 项目](https://github.com/user/rio_updater)
- [问题报告](https://github.com/user/rio_updater/issues)
