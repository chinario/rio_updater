# CNB 平台 uv 安装脚本和测试套件

## 概述

本文档介绍了两个用于 CNB 平台的工具：

1. **install-cnb-uv.sh** - CNB 平台 uv 安装脚本
2. **test_cnb_platform.py** - CNB 平台集成测试套件

这些工具参照官方 `astral.sh/uv/install.sh` 的设计，专门为 CNB.cool 平台优化。

## 工具 1: CNB uv 安装脚本

### 文件位置
```
/workspaces/rio_updater/install-cnb-uv.sh
```

### 功能特性

- ✅ 自动检测系统架构和操作系统
- ✅ 从 CNB 平台获取最新发布信息
- ✅ 下载并验证二进制文件
- ✅ 安装到指定目录
- ✅ 支持 PATH 配置
- ✅ 详细的进度输出
- ✅ 环境变量控制

### 支持的操作系统和架构

**操作系统:**
- Linux
- macOS (Darwin)

**架构:**
- x86_64
- aarch64 (ARM64)

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `CNB_BASE_URL` | CNB 平台基础 URL | `https://cnb.cool` |
| `CNB_REPO` | CNB 上的仓库名 | `astral-sh/uv` |
| `CNB_VERBOSE` | 详细输出 (1=启用) | `0` |
| `CNB_INSTALL_DIR` | 安装目录 | `$HOME/.local/bin` |
| `CNB_NO_MODIFY_PATH` | 不修改 PATH (1=禁用) | `0` |

### 使用方法

#### 基础安装

```bash
# 直接运行本地脚本
sh /workspaces/rio_updater/install-cnb-uv.sh

# 或从网络安装（如果部署到服务器）
curl -fsSL https://your-server/install-cnb-uv.sh | sh
```

#### 自定义安装

```bash
# 设置自定义安装目录
CNB_INSTALL_DIR=$HOME/tools sh install-cnb-uv.sh

# 启用详细输出
CNB_VERBOSE=1 sh install-cnb-uv.sh

# 不修改 PATH
CNB_NO_MODIFY_PATH=1 sh install-cnb-uv.sh

# 使用自定义 CNB 实例
CNB_BASE_URL=https://internal-cnb.company.com sh install-cnb-uv.sh
```

### 脚本结构

脚本分为以下主要部分：

```
1. 配置和初始化
   - 读取环境变量
   - 设置默认值
   - 初始化日志函数

2. 工具函数
   - get_arch() - 获取系统架构
   - get_os() - 获取操作系统
   - get_home() - 获取主目录

3. 网络函数
   - check_network() - 检查网络连接
   - get_cnb_release_info() - 获取发布信息
   - get_download_url() - 获取下载 URL

4. 安装函数
   - download_file() - 下载文件
   - verify_file() - 验证文件
   - extract_archive() - 提取存档
   - install_binary() - 安装二进制
   - modify_path() - 修改 PATH

5. 主安装流程
   - 9 个步骤的完整安装流程
```

### 安装步骤详解

1. **初始化** - 创建临时目录，检查环境
2. **网络检查** - 验证网络连接
3. **获取信息** - 从 CNB API 获取发布信息
4. **下载文件** - 下载二进制存档
5. **提取文件** - 解压缩存档
6. **定位二进制** - 查找 uv 可执行文件
7. **安装** - 复制到目标目录，设置权限
8. **配置环境** - 更新 PATH（可选）
9. **验证** - 测试安装是否成功

---

## 工具 2: CNB 平台集成测试套件

### 文件位置
```
/workspaces/rio_updater/test_cnb_platform.py
```

### 功能特性

- ✅ 10 项全面的测试
- ✅ 测试 CNB 平台连接性
- ✅ 验证 API 端点
- ✅ 检查脚本完整性
- ✅ 验证环境支持
- ✅ 详细的测试报告
- ✅ 彩色输出

### 测试清单

| # | 测试项 | 说明 |
|----|--------|------|
| 1 | CNB 平台连接性 | 验证 CNB 服务器可访问 |
| 2 | CNB 仓库页面 | 检查仓库页面是否可访问 |
| 3 | CNB 发布页面 | 检查发布列表是否可访问 |
| 4 | CNB API 端点 | 验证 API 能否返回 JSON 数据 |
| 5 | 安装脚本 | 检查脚本语法和结构 |
| 6 | 环境变量 | 验证脚本支持的环境变量 |
| 7 | Rust 集成 | 运行 Rust 单元测试 |
| 8 | 脚本权限 | 验证脚本可执行性 |
| 9 | 下载工具 | 检查 curl/wget 可用性 |
| 10 | tar 工具 | 验证 tar 命令可用性 |

### 使用方法

#### 基础运行

```bash
# 运行所有测试
python3 test_cnb_platform.py

# 详细输出
python3 test_cnb_platform.py -v

# 详细输出（缩写）
python3 test_cnb_platform.py --verbose
```

#### 自定义配置

```bash
# 使用自定义 CNB URL
python3 test_cnb_platform.py --cnb-url https://internal-cnb.example.com

# 使用不同的仓库
python3 test_cnb_platform.py --cnb-repo myorg/myapp

# 组合选项
python3 test_cnb_platform.py -v --cnb-url https://cnb.cool --cnb-repo astral-sh/uv
```

### 测试输出示例

```
======================================================================
CNB 平台集成测试套件
======================================================================

【测试】CNB 平台连接性
----------------------------------------------------------------------
连接 CNB 平台: https://cnb.cool
ℹ️  HTTP 状态码: 200
✅ CNB 平台连接性 通过

... (其他测试) ...

======================================================================
测试报告
======================================================================

总体: 10/10 通过
✅ 所有测试通过！
```

### 测试结果解释

**通过 (✅)**
- 绿色输出
- 功能正常工作
- 无需进一步操作

**失败 (❌)**
- 红色输出
- 包含错误信息
- 需要检查和修复

**警告 (⚠️)**
- 黄色输出
- 功能可用但不完美
- 可能需要关注

---

## 完整工作流

### 1. 验证 CNB 平台

```bash
# 首先运行测试，确保平台功能正常
python3 test_cnb_platform.py -v
```

预期结果：所有 10 项测试都应通过。

### 2. 安装 uv

```bash
# 运行安装脚本
sh install-cnb-uv.sh

# 或使用自定义选项
CNB_VERBOSE=1 sh install-cnb-uv.sh
```

预期结果：uv 被安装到 `~/.local/bin/uv`

### 3. 验证安装

```bash
# 检查版本
uv --version

# 查看帮助
uv --help

# 验证 uvx
uvx --version
```

---

## 故障排除

### 问题 1: "CNB 平台连接失败"

**原因:** 网络问题或 CNB 服务不可用

**解决方案:**
```bash
# 测试网络连接
ping cnb.cool

# 使用浏览器手动访问
open https://cnb.cool

# 检查防火墙
curl -v https://cnb.cool
```

### 问题 2: "API 需要认证"

**原因:** CNB API 端点返回 401 Unauthorized

**解决方案:**
```bash
# 这是预期的行为
# 脚本会自动使用备用方法（从网页解析）

# 或使用 API Token（如果 CNB 支持）
export CNB_API_TOKEN="your-token"
sh install-cnb-uv.sh
```

### 问题 3: "找不到二进制文件"

**原因:** 提取后找不到 uv 可执行文件

**解决方案:**
```bash
# 启用详细输出
CNB_VERBOSE=1 sh install-cnb-uv.sh

# 检查临时目录
ls -la /tmp/

# 手动检查下载的文件
tar -tzf /tmp/uv.tar.gz | grep -i uv
```

### 问题 4: "权限被拒绝"

**原因:** 安装目录无写权限

**解决方案:**
```bash
# 使用可写目录
CNB_INSTALL_DIR=$HOME/bin sh install-cnb-uv.sh

# 或创建目录
mkdir -p $HOME/.local/bin
chmod 755 $HOME/.local/bin
sh install-cnb-uv.sh
```

---

## 最佳实践

### 1. 在生产环境部署

```bash
# 步骤 1: 验证平台
python3 test_cnb_platform.py

# 步骤 2: 验证脚本
sh -n install-cnb-uv.sh

# 步骤 3: 部署脚本
cp install-cnb-uv.sh /usr/local/bin/
chmod 755 /usr/local/bin/install-cnb-uv.sh

# 步骤 4: 测试安装
CNB_INSTALL_DIR=/opt/tools sh /usr/local/bin/install-cnb-uv.sh
```

### 2. 创建安装说明

```bash
# 为团队创建安装指南
cat > INSTALL-UV.md << 'EOF'
# 安装 uv

## 快速安装
sh install-cnb-uv.sh

## 自定义安装
CNB_INSTALL_DIR=/path/to/bin sh install-cnb-uv.sh
EOF
```

### 3. 定期验证

```bash
# 创建 cron 任务
0 0 * * * python3 test_cnb_platform.py >> /var/log/cnb-test.log 2>&1
```

### 4. 文档和版本控制

```bash
# 添加到版本控制
git add install-cnb-uv.sh test_cnb_platform.py
git commit -m "Add CNB platform uv installer and test suite"

# 记录部署日期
sh install-cnb-uv.sh 2>&1 | tee uv-install-$(date +%Y%m%d).log
```

---

## 技术细节

### 脚本设计决策

1. **使用 POSIX sh 而不是 bash**
   - 更好的兼容性
   - 支持更多系统

2. **备用方法机制**
   - API 不可用时从网页解析
   - 确保可靠性

3. **环境变量优先级**
   - 高度可定制
   - 支持企业需求

4. **详细的错误处理**
   - 清晰的错误消息
   - 便于故障排除

### 测试设计

1. **多层测试**
   - 网络层（连接性）
   - API 层（端点）
   - 集成层（Rust 代码）
   - 环境层（工具可用性）

2. **自动化验证**
   - 脚本语法检查
   - 函数可用性检查
   - 权限验证

3. **详细报告**
   - 测试进度
   - 详细结果
   - 失败原因

---

## 参考资源

### 官方文档
- [CNB.cool](https://cnb.cool)
- [uv 官方](https://astral.sh/uv)
- [官方安装脚本](https://astral.sh/uv/install.sh)

### 本项目文档
- [Phase 2 完成报告](../PHASE2_COMPLETION_SUMMARY.md)
- [项目状态报告](../docs/PROJECT_STATUS.md)
- [快速参考卡片](../QUICKREF.md)

---

## 常见问题

**Q: 为什么要在 sh 中使用 local？**
A: `local` 是 POSIX 扩展，让变量作用域更清晰。脚本处理了不支持 `local` 的系统。

**Q: 脚本支持代理吗？**
A: 继承 curl/wget 的代理设置。设置：
```bash
export http_proxy=http://proxy:8080
sh install-cnb-uv.sh
```

**Q: 可以离线安装吗？**
A: 可以，预先下载文件，然后：
```bash
# 手动下载 uv 二进制
# 然后手动解压和安装
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
cp uv ~/.local/bin/
chmod +x ~/.local/bin/uv
```

**Q: 如何验证下载的文件？**
A: 脚本支持 SHA256 验证。如果 CNB 提供校验和：
```bash
sha256sum uv.tar.gz
```

---

**版本**: 1.0.0  
**最后更新**: 2025-01-11  
**维护者**: CNB 项目团队
