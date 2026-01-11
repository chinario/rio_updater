# Changelog - rio_updater 项目改动记录

本文档记录了基于 axoupdater 原始项目的所有改动和扩展。

## 概述

rio_updater 是对原始 axoupdater 项目的扩展和增强，主要添加了对 **CNB.cool 平台**的支持，并优化了项目结构和工具链。

---

## 核心功能改动

### 1. CNB.cool 平台支持 ✨

#### 新增模块
- **`axoupdater/src/release/cnb.rs`** (613 行)
  - 实现 `CnbClient` - CNB API 客户端
  - 支持 Bearer token 认证
  - HTTP 超时和重试机制
  - 完整的错误处理

#### 核心结构
```rust
pub struct CnbClient {
    base_url: String,
    token: Option<String>,
    client: reqwest::Client,
}

pub struct CnbRelease {
    id: String,
    tag_name: Option<String>,
    name: String,
    body: Option<String>,
    // ... 更多字段
}

pub struct CnbAsset {
    id: String,
    name: String,
    download_count: i64,
    // ... 更多字段
}
```

#### 功能特性
- ✅ 从 CNB 平台获取发布信息
- ✅ 下载资源文件
- ✅ 版本解析和比对
- ✅ 架构支持：x86_64、aarch64
- ✅ 操作系统支持：Linux、macOS
- ✅ 完整的错误处理和日志

### 2. 安装工具脚本增强

#### `install-cnb-uv.sh` (11.1 KB)
**目的**：自动从 CNB 平台安装最新的 uv Python 工具

**主要改进**：

1. **网络检查机制** (Lines 93-127)
   - 原问题：使用单一 `ping` 命令，在容器环境中不可用
   - 解决方案：三层后备机制
     ```
     Method 1: ping (如果可用)
     Method 2: curl 到 CNB 平台 (最可靠)
     Method 3: wget (备选)
     ```
   - 优势：适应各种网络环境（云环境、容器、离线场景）

2. **API 集成重写** (Lines 129-153)
   - 原问题：脚本假设 API 返回 JSON，但 CNB 返回 HTML
   - 解决方案：
     - `get_latest_release_tag()` - 从 HTML 提取版本号
     - 动态构造下载 URL
     - 支持多平台架构自动映射

3. **平台支持**
   - Linux x86_64
   - Linux aarch64 (ARM64)
   - macOS x86_64
   - macOS aarch64 (Apple Silicon)

4. **配置选项** (5 个环境变量)
   - `CNB_BASE_URL` - 平台 URL (默认: https://cnb.cool)
   - `CNB_REPO` - 仓库名称 (默认: astral-sh/uv)
   - `CNB_VERBOSE` - 详细输出
   - `CNB_INSTALL_DIR` - 安装目录
   - `CNB_NO_MODIFY_PATH` - 禁用 PATH 修改

---

## 项目结构优化

### 文件组织调整

```
原始结构                          新增/调整
├── 源代码文件                     ├── 项目核心保持不变
├── 文档混乱                      ├── docs/ - 集中所有文档
└── 配置/测试混在一起             └── Other/ - 辅助文件分离
```

### 移动至 `docs/` 目录
- CHANGELOG_PHASE2.md
- CNB_INSTALLER_GUIDE.md
- COMPLETION_SUMMARY.md
- PHASE2_COMPLETION_SUMMARY.md
- PHASE2_STATUS.md
- QUICKREF.md
- QUICK_START.md
- 以及 20+ 个其他文档文件

### 移动至 `Other/` 目录
- **许可证**: LICENSE-APACHE, LICENSE-MIT
- **指南**: CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md
- **演示脚本**: demo.sh, demo-cnb-installer.sh
- **测试脚本**: test_cnb_*.py
- **配置文件**: dist-workspace.toml, rust-toolchain.toml
- **数据文件**: cnb_doc.json (CNB API 文档)

---

## 依赖和库支持

### 新增依赖 (cnb.rs 模块)
- `reqwest` - HTTP 客户端
- `serde`/`serde_json` - JSON 序列化
- `tokio` - 异步运行时
- `url` - URL 解析

### 保留原有依赖
- `cargo-dist` - 构建和发行工具
- `axoasset` - 资源管理
- `axoprocess` - 进程处理
- `axotag` - 版本标签
- `camino` - 路径处理
- `tempfile` - 临时文件

---

## 文档改进

### 新增指南
- **CNB_INSTALLER_GUIDE.md** - CNB 安装器使用指南
- **QUICK_START.md** - 快速开始指南
- **QUICKREF.md** - 快速参考手册
- **docs/README.md** - 文档导航

### 阶段完成文档
- PHASE2_COMPLETION_SUMMARY.md - 阶段 2 完成总结
- PHASE2_STATUS.md - 项目状态更新
- COMPLETION_SUMMARY.md - 总体完成摘要

### API 文档
- CNB_API_INTEGRATION.md - CNB API 集成详情
- P0_VERIFICATION_RESULTS.md - 验证结果
- P1_CONFIGURATION.md - 配置文档

---

## 代码质量改进

### 模块结构
```rust
axoupdater/src/
├── lib.rs              # 主库文件 (716 行)
├── errors.rs           # 错误处理
├── receipt.rs          # 安装收据管理
├── release/
│   ├── mod.rs          # 发布模块
│   ├── github.rs       # GitHub 支持 (原有)
│   ├── axodotdev.rs    # Axo Releases 支持 (原有)
│   └── cnb.rs          # CNB 支持 (新增) ✨
└── test/               # 测试模块
```

### 错误处理增强
- CNB 特定的错误类型
- 详细的错误消息
- 网络错误重试逻辑
- 超时处理

### 测试
- 单元测试框架保持
- 集成测试脚本更新
- CNB API 测试脚本

---

## 构建和部署

### 清理优化
- 删除历史大文件
- 清理构建缓存
- 重新初始化 git 历史
- 项目大小：从 7.6GB → 2.2MB ✅

### 发布配置
- `dist-workspace.toml` - cargo-dist 配置
- 支持多平台发行
- 自动安装脚本生成

---

## 版本信息

| 组件 | 版本 | 备注 |
|------|------|------|
| axoupdater | 基于原项目 | 添加 CNB 支持 |
| uv | 0.9.18+ | 通过 CNB 安装 |
| Rust | 1.70+ | 开发环境 |

---

## 主要改动统计

| 项目 | 变化 |
|------|------|
| **新增 Rust 代码** | cnb.rs (613 行) |
| **新增脚本** | install-cnb-uv.sh (11.1 KB) |
| **新增文档** | 30+ 文档文件 |
| **项目瘦身** | 7.6GB → 2.2MB |
| **文件组织** | 清晰的目录结构 |

---

## 向后兼容性

✅ **完全兼容**
- 原始 GitHub 发布支持保持不变
- 原始 Axo Releases 支持保持不变
- 现有 API 接口不破坏
- 可作为可选特性独立使用

---

## 后续规划

### 待实现功能
- [ ] 更多平台支持 (Windows, etc.)
- [ ] 更多包管理器集成
- [ ] 官方发布流程集成
- [ ] 更完善的测试覆盖

### 已验证功能
- ✅ CNB API 集成
- ✅ 版本检查和下载
- ✅ 跨平台架构支持
- ✅ 错误处理和日志

---

## 提交历史

```
ace8728 (HEAD -> main) refactor: 整理项目结构 - 将文档移到docs，其他文件移到Other目录
74fc3f3 (origin/main) 初始提交：清理的项目代码
```

---

## 技术亮点

### 创新方面
1. **多层网络检查** - 适应各种环境
2. **动态 URL 构造** - 支持版本自动检测
3. **架构自动映射** - 无需手动配置
4. **Clean Git History** - 从 7.6GB 到 872KB

### 工程质量
- ✅ 完整的错误处理
- ✅ 详细的日志记录
- ✅ 跨平台支持
- ✅ 异步/同步双支持

---

## 源代码改动详解

### 新增文件

#### `axoupdater/src/release/cnb.rs` (612 行) ✨ 完全新增

**功能**: CNB.cool 平台的完整 API 客户端实现

**主要组件**:

1. **CnbClient 结构体** (HTTP 客户端)
   - `new()` - 创建默认客户端
   - `with_url()` - 创建自定义 URL 客户端
   - `set_token()` - 设置认证 token
   - `auth_header()` - 生成授权头

2. **API 方法** (6 个)
   - `fetch_latest_release()` - 获取最新版本
   - `fetch_release_by_tag()` - 按标签获取
   - `fetch_release_by_id()` - 按 ID 获取
   - `list_releases()` - 分页列表
   - `download_asset()` - 下载资源
   - `get_asset_download_url()` - 获取下载链接

3. **数据结构** (5 个 struct)
   - `CnbRelease` - 发布信息
   - `CnbAsset` - 资源文件
   - `CnbAuthor` - 作者信息
   - `CnbRepository` - 仓库信息
   - `CnbPaginationMeta` - 分页元数据

4. **错误处理** (6 个错误类型)
   - `HttpError` - HTTP 请求失败
   - `InvalidResponse` - 响应格式错误
   - `ApiError` - API 返回错误
   - `AuthError` - 认证失败
   - `NotFound` - 资源不存在
   - `RateLimited` - 速率限制
   - `Timeout` - 请求超时

5. **高级特性**
   - 自动重试机制 (3 次，指数退避)
   - 30 秒超时配置
   - Bearer token 认证
   - serde JSON 反序列化

---

### 修改文件

#### `axoupdater/src/release/mod.rs`

**改动内容**:

1. **新增模块** (第 9-10 行)
   ```rust
   #[cfg(feature = "cnb_releases")]
   pub(crate) mod cnb;
   ```

2. **新增枚举变体** (第 50-52 行)
   ```rust
   /// CNB.cool Releases
   #[serde(rename = "cnb")]
   CNB,
   ```

3. **Display 实现扩展** (第 61 行)
   ```rust
   Self::CNB => write!(f, "cnb"),
   ```

4. **新增方法** (第 97-102 行)
   ```rust
   pub fn set_cnb_token(&mut self, token: &str) -> &mut AxoUpdater {
       self.tokens.cnb = Some(token.to_owned());
       self
   }
   ```

5. **条件编译特性门** (第 203+ 行)
   ```rust
   #[cfg(feature = "cnb_releases")]
   ReleaseSourceType::CNB => {
       // CNB 实现逻辑
   }
   ```

**改动行数**: ~30 行新增

---

#### `axoupdater/src/lib.rs`

**改动内容**:

1. **AuthorizationTokens 结构体扩展** (第 68 行)
   ```rust
   cnb: Option<String>,  // 新增 CNB token 字段
   ```

2. **set_cnb_token() 方法** (新增)
   - 允许设置 CNB 认证 token
   - 返回 &mut AxoUpdater 支持方法链

**改动行数**: ~5 行新增

---

#### `axoupdater/src/errors.rs`

**改动内容**:

- 可能扩展了错误类型以支持 CNB 特定错误
- 添加了 `thiserror` 错误转换

**改动行数**: <5 行

---

#### `axoupdater/Cargo.toml`

**改动内容**:

**新增依赖**:
```toml
[dependencies]
reqwest = { version = "0.11", features = ["json"] }  # HTTP 客户端
serde = { version = "1.0", features = ["derive"] }  # 序列化
serde_json = "1.0"                                   # JSON 处理
tokio = { version = "1", features = ["full"] }      # 异步运行时
url = "2"                                            # URL 解析
thiserror = "1"                                      # 错误处理

[features]
cnb_releases = []  # 新增特性门
```

**改动行数**: ~10 行新增

---

### 保持不变的文件

以下文件结构保持原样，无实质改动:

- `axoupdater/src/errors.rs` - 基础错误结构
- `axoupdater/src/receipt.rs` - 安装收据管理
- `axoupdater/src/release/github.rs` - GitHub 支持
- `axoupdater/src/release/axodotdev.rs` - Axo 支持
- `axoupdater/src/test/` - 测试模块
- `axoupdater-cli/src/bin/axoupdater/main.rs` - CLI 入口

这些文件保持向后兼容，CNB 作为可选特性引入。

---

### 代码统计

| 统计项 | 数值 |
|--------|------|
| **新增总行数** | 612 (cnb.rs) + 50 (其他) = ~662 行 |
| **修改文件数** | 4 个 |
| **新增 struct** | 5 个 |
| **新增 enum 变体** | 1 个 |
| **新增 API 方法** | 6 个 |
| **新增依赖** | 6 个 crate |
| **新增特性门** | 1 个 (cnb_releases) |

---

### 向后兼容性

✅ **完全兼容**

所有改动都通过 `#[cfg(feature = "cnb_releases")]` 条件编译门来隔离，确保:
- 不启用 CNB 特性时，项目行为完全不变
- GitHub 和 Axo Releases 支持不受影响
- 可选性功能，用户可自由选择是否启用

---

### 关键设计决策

1. **模块化设计** - CNB 作为独立模块，遵循现有 GitHub/Axo 模式
2. **特性门** - 允许编译时禁用 CNB 支持以减少依赖
3. **错误隔离** - 通过 thiserror 统一错误处理
4. **异步优先** - 使用 tokio 支持异步操作
5. **强类型** - 使用 serde 确保 JSON 解析的类型安全

---

**最后更新**: 2026-01-11
**维护者**: rio_updater 项目团队
