# CNB.cool 集成开发规划方案

## 项目概述

为 axoupdater 添加 CNB.cool 平台支持，使其能够从 CNB.cool 平台获取和管理应用版本发布，扩展 axoupdater 的发布源支持能力。

**目标时间线**：2026 年 1 月 - 2 月

---

## 第一阶段：需求分析与设计

### 1.1 API 功能梳理

**时间估计**：2-3 天

#### 目标
分析 CNB.cool API 文档，确定核心 API 端点和调用流程

#### 详细步骤

1. **分析发布相关 API**
   - [ ] 查阅 `Releases` 分类 API（12 个 API）
   - [ ] 确定获取最新版本的 API：`GetLatestRelease`
   - [ ] 确定获取指定版本的 API：`GetReleaseByID`
   - [ ] 确定获取发布附件的 API：`GetReleaseAsset`
   - [ ] 文档位置：cnb_doc.json 中 `paths./releases/{repo}/-/latest`

2. **分析仓库相关 API**
   - [ ] 查阅 `Repositories` 分类 API（15 个 API）
   - [ ] 确定仓库信息获取方式
   - [ ] 确定仓库识别机制（对标 GitHub 仓库 owner/repo）

3. **分析认证机制**
   - [ ] 确定 Bearer Token 认证方式
   - [ ] 确定权限模型
   - [ ] 制定 token 配置策略
   - [X] 用户已经提供token：db5HVM2xIiR0Zo11dcsuL4WeHGE

4. **对比分析**
   - [ ] 与 GitHub API 对比功能差异
   - [ ] 与 Axo Releases API 对比
   - [ ] 文档存档：`cnb_api_analysis.md`

### 1.2 架构设计

**时间估计**：2-3 天

#### 目标
设计模块架构和数据流

#### 详细步骤

1. **模块设计**
   - [ ] 创建设计文档 `CNB_ARCHITECTURE.md`
   - [ ] 设计 `cnb.rs` 模块结构
   - [ ] 设计 `CnbClient` struct
   - [ ] 设计错误类型扩展

2. **API 客户端设计**
   - [ ] HTTP 客户端选择（reqwest / hyper）
   - [ ] 请求/响应序列化（serde/json）
   - [ ] 错误处理映射策略
   - [ ] Token 管理机制

3. **集成点设计**
   - [ ] `ReleaseSourceType` 枚举扩展
   - [ ] `Release` struct 兼容性检查
   - [ ] `Asset` struct 映射
   - [ ] 条件编译特性设计（`cnb_releases`）

4. **数据结构设计**
   - [ ] CNB 发布信息 struct
   - [ ] CNB 附件信息 struct
   - [ ] 字段映射关系表

### 1.3 环境准备

**时间估计**：1 天

#### 目标
准备开发环境和测试账号

#### 详细步骤

1. **获取 CNB 测试账号**
   - [x] 注册 cnb.cool 账号
   - [x] 创建测试仓库（如 test-app）：已经明确0.9.17版本用于测试安装，0.9.18版本用于测试能否更新，期间由用户切换latest版本：https://cnb.cool/astral-sh/uv/-/releases
   - [x] 创建发布版本用于测试:
   - [x] 生成 API Token:db5HVM2xIiR0Zo11dcsuL4WeHGE
   - [ ] 文档位置：`.env.example` 或 `README_CNB.md`

2. **环境配置**
   - [x] 设置 CNB_TOKEN 环境变量：db5HVM2xIiR0Zo11dcsuL4WeHGE
   - [ ] 配置本地测试仓库标识符
   - [ ] 准备测试数据集

3. **依赖检查**
   - [ ] 验证 reqwest 版本兼容性
   - [ ] 验证 serde_json 版本
   - [ ] 检查是否需要额外依赖

---

## 第二阶段：核心开发

### 2.1 CNB 客户端实现

**时间估计**：5-7 天

#### 目标
实现完整的 CNB API 客户端

#### 详细步骤

1. **创建 cnb.rs 模块**
   - [ ] 新建文件：`axoupdater/src/release/cnb.rs`
   - [ ] 导入必要的依赖
   - [ ] 定义模块作用域

2. **定义数据结构**
   - [ ] 定义 `CnbRelease` struct
     ```rust
     pub struct CnbRelease {
         pub id: u64,
         pub tag_name: String,
         pub name: String,
         pub body: String,
         pub prerelease: bool,
         pub created_at: String,
         pub published_at: Option<String>,
         pub assets: Vec<CnbAsset>,
     }
     ```
   - [ ] 定义 `CnbAsset` struct
   - [ ] 定义 `CnbRepository` struct
   - [ ] 添加 Deserialize 派生

3. **实现 CnbClient**
   - [ ] 创建 `CnbClient` struct
   - [ ] 实现 HTTP 客户端初始化
   - [ ] 实现 authentication 方法
   - [ ] 添加 token 管理

4. **实现核心 API 方法**
   - [ ] `fn fetch_latest_release()` - 获取最新版本
   - [ ] `fn fetch_release_by_tag()` - 按 tag 获取版本
   - [ ] `fn fetch_release_by_id()` - 按 ID 获取版本
   - [ ] `fn fetch_asset()` - 下载附件
   - [ ] 错误处理和重试逻辑

5. **错误处理**
   - [ ] 定义 `CnbError` enum
   - [ ] 实现 HTTP 错误映射
   - [ ] 实现 API 错误响应处理
   - [ ] 添加错误链路追踪

### 2.2 Release 源类型集成

**时间估计**：3-4 天

#### 目标
将 CNB 集成到现有的发布源框架

#### 详细步骤

1. **扩展 ReleaseSourceType**
   - [ ] 在 `axoupdater/src/release/mod.rs` 中
   - [ ] 添加 `CNB` 变量到 enum
   - [ ] 更新 Display 实现
   - [ ] 更新 Deserialize 实现

2. **实现 Release 获取**
   - [ ] 在 `AxoUpdater` 中添加 CNB 特性检查
   - [ ] 实现 `fetch_cnb_release()` 方法
   - [ ] 实现版本检查逻辑
   - [ ] 处理预发布版本

3. **实现 Release 转换**
   - [ ] 实现 `CnbRelease` → `Release` 转换
   - [ ] 实现 `CnbAsset` → `Asset` 转换
   - [ ] 处理 URL 规范化

4. **更新主逻辑**
   - [ ] 在 release 获取流程中添加 CNB 分支
   - [ ] 更新 match 语句
   - [ ] 确保向后兼容性

### 2.3 认证与配置

**时间估计**：2-3 天

#### 目标
实现 CNB Token 管理和环境配置

#### 详细步骤

1. **添加 Token 管理**
   - [ ] 在 `AuthorizationTokens` 中添加 `cnb: Option<String>`
   - [ ] 实现 `set_cnb_token()` 方法
   - [ ] 实现环境变量读取（`CNB_TOKEN`）

2. **配置读取**
   - [ ] 实现 receipt 中 CNB 配置的读取
   - [ ] 支持自定义 CNB 实例 URL（可选）
   - [ ] 实现配置文件支持

3. **权限模型**
   - [ ] 实现 token 验证
   - [ ] 处理权限不足的场景
   - [ ] 实现 anonymous 访问（如果 CNB 支持）

4. **文档更新**
   - [ ] 在 README.md 中添加 CNB 使用说明
   - [ ] 编写 CNB 环境变量配置指南
   - [ ] 创建 CNB 集成示例代码

---

## 第三阶段：测试与验证

### 3.1 单元测试

**时间估计**：3-4 天

#### 目标
编写全面的单元测试

#### 详细步骤

1. **创建测试模块**
   - [ ] 在 `axoupdater/src/test/` 中创建 `cnb_tests.rs`
   - [ ] 设置测试框架（mock HTTP 响应）

2. **API 客户端测试**
   - [ ] 测试成功响应处理
   - [ ] 测试错误响应处理
   - [ ] 测试 token 认证
   - [ ] 测试超时处理
   - [ ] 覆盖率目标：> 80%

3. **数据转换测试**
   - [ ] 测试 `CnbRelease` 反序列化
   - [ ] 测试 `CnbAsset` 映射
   - [ ] 测试 Release 转换
   - [ ] 测试 URL 处理

4. **集成逻辑测试**
   - [ ] 测试 release source 类型识别
   - [ ] 测试版本比对
   - [ ] 测试预发布版本处理

### 3.2 集成测试

**时间估计**：3-4 天

#### 目标
验证与 CNB 平台的实际交互

#### 详细步骤

1. **环境准备**
   - [ ] 设置集成测试仓库
   - [ ] 创建测试发布版本
   - [ ] 准备不同场景的测试数据

2. **E2E 测试场景**
   - [ ] 获取最新版本流程
   - [ ] 获取指定版本流程
   - [ ] 资源下载流程
   - [ ] 版本比对和更新流程

3. **异常场景测试**
   - [ ] 网络超时处理
   - [ ] 认证失败处理
   - [ ] 版本不存在处理
   - [ ] 资源不可用处理

4. **兼容性测试**
   - [ ] 与 GitHub releases 并行测试
   - [ ] 与 Axo releases 并行测试
   - [ ] 混合来源场景测试

### 3.3 性能测试

**时间估计**：2 天

#### 目标
验证性能指标

#### 详细步骤

1. **基准测试**
   - [ ] API 调用响应时间
   - [ ] 大文件下载速度
   - [ ] 内存占用情况

2. **负载测试**
   - [ ] 并发请求处理
   - [ ] Rate limit 处理
   - [ ] 长期稳定性测试

3. **对比分析**
   - [ ] 与 GitHub 源性能对比
   - [ ] 与 Axo 源性能对比

---

## 第四阶段：文档与发布

### 4.1 文档编写

**时间估计**：2-3 天

#### 目标
完整的用户和开发者文档

#### 详细步骤

1. **用户文档**
   - [ ] 更新 README.md
     - CNB 简介
     - 快速开始
     - 配置示例
   - [ ] 编写 `docs/CNB_USAGE.md`
     - 详细使用指南
     - 常见问题解答
     - 故障排查

2. **开发者文档**
   - [ ] 编写 `docs/CNB_DEVELOPMENT.md`
     - 架构说明
     - 代码结构
     - 扩展指南
   - [ ] 代码注释完善
     - 公共 API 文档注释
     - 复杂逻辑说明

3. **API 文档**
   - [ ] 生成 Rust doc
   - [ ] 验证文档链接
   - [ ] 补充示例代码

4. **更新日志**
   - [ ] 更新 CHANGELOG.md
   - [ ] 记录新功能列表
   - [ ] 记录 breaking changes（如有）

### 4.2 代码审查准备

**时间估计**：2 天

#### 目标
完善代码质量

#### 详细步骤

1. **代码规范检查**
   - [ ] 运行 `cargo fmt` 检查格式
   - [ ] 运行 `cargo clippy` 检查代码质量
   - [ ] 修复所有警告

2. **安全审查**
   - [ ] 检查依赖安全性
   - [ ] 运行 `cargo audit`
   - [ ] 审查 token 处理安全性

3. **文档审查**
   - [ ] 检查文档完整性
   - [ ] 验证示例代码可运行
   - [ ] 检查链接有效性

4. **测试覆盖**
   - [ ] 达到 > 80% 覆盖率
   - [ ] 补充缺失的测试
   - [ ] 运行完整测试套件

### 4.3 版本发布

**时间估计**：1-2 天

#### 目标
发布新版本

#### 详细步骤

1. **版本号确定**
   - [ ] 确定版本号（遵循 semver）
   - [ ] 示例：从 0.x.0 → 0.(x+1).0

2. **发布前检查**
   - [ ] 验证所有 tests 通过
   - [ ] 验证文档完整
   - [ ] 验证 CHANGELOG 更新

3. **发布流程**
   - [ ] 更新 Cargo.toml 版本号
   - [ ] 创建 git tag
   - [ ] 运行 `cargo publish` 到 crates.io（如果开源）
   - [ ] 创建 GitHub release

4. **发布验证**
   - [ ] 验证 crate 可正常使用
   - [ ] 验证文档在 docs.rs 正确显示
   - [ ] 验证 CI/CD 通过

---

## 第五阶段：后续优化

### 5.1 功能增强（第一版本之后）

- [ ] 支持 CNB 仓库列表查询
- [ ] 支持 CNB 组织/群组管理
- [ ] 支持 CNB 制品库（registry）集成
- [ ] 实现增量更新支持
- [ ] 支持自签名证书（企业部署）

### 5.2 性能优化

- [ ] 实现 release 缓存机制
- [ ] 实现并发下载支持
- [ ] 优化大文件处理

### 5.3 生态集成

- [ ] cargo-dist 集成支持
- [ ] CI/CD 工作流示例
- [ ] Docker 容器集成示例

---

## 技术栈与依赖

### 核心依赖
```toml
# HTTP 客户端
reqwest = { version = "0.11", features = ["json", "stream"] }

# JSON 序列化
serde_json = "1.0"
serde = { version = "1.0", features = ["derive"] }

# 异步运行时（已有）
tokio = { version = "1", features = ["full"] }

# 测试框架
mockito = "1.0"  # 用于 mock HTTP 请求
```

### 条件编译
```toml
[features]
default = ["github_releases", "axo_releases", "cnb_releases"]
github_releases = []
axo_releases = []
cnb_releases = []
blocking = []
```

---

## 文件清单

### 新增文件
- [ ] `axoupdater/src/release/cnb.rs` - CNB 客户端实现
- [ ] `docs/CNB_USAGE.md` - 用户使用文档
- [ ] `docs/CNB_DEVELOPMENT.md` - 开发文档
- [ ] `docs/CNB_ARCHITECTURE.md` - 架构设计文档
- [ ] `docs/cnb_api_analysis.md` - API 分析文档
- [ ] `tests/cnb_integration_tests.rs` - 集成测试
- [ ] `.env.example` - 环境变量示例

### 修改文件
- [ ] `axoupdater/src/release/mod.rs` - 添加 CNB 源类型和逻辑
- [ ] `axoupdater/src/lib.rs` - 添加 CNB token 管理
- [ ] `axoupdater/Cargo.toml` - 添加依赖和特性
- [ ] `README.md` - 添加 CNB 说明
- [ ] `CHANGELOG.md` - 记录新功能

---

## 风险评估

### 可能的风险

| 风险 | 概率 | 影响 | 应对方案 |
|------|------|------|--------|
| CNB API 变更 | 低 | 中 | 频繁同步文档，使用版本化 API |
| Token 认证失败 | 中 | 高 | 完善错误处理，提供调试工具 |
| 性能瓶颈 | 低 | 中 | 实现缓存，做好性能测试 |
| 网络稳定性 | 中 | 中 | 实现重试机制，超时配置 |
| 依赖冲突 | 低 | 低 | 定期更新依赖，做兼容性测试 |

---

## 时间表总结

| 阶段 | 任务 | 预计时间 |
|------|------|--------|
| 第一阶段 | 需求分析、设计、环境准备 | 8-10 天 |
| 第二阶段 | 核心开发 | 10-14 天 |
| 第三阶段 | 测试验证 | 8-12 天 |
| 第四阶段 | 文档发布 | 5-7 天 |
| **总计** | **4 个阶段** | **31-43 天** |

**预计完成日期**：2026 年 1 月 20 日 - 2 月 25 日

---

## 成功标准

- [x] 完成所有设计文档
- [ ] CNB 客户端实现完整
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试全部通过
- [ ] 文档完整且清晰
- [ ] 性能指标达到预期
- [ ] 代码审查通过
- [ ] 成功发布新版本

---

## 联系与反馈

如有任何问题或建议，请创建 Issue 或提交 PR。

最后更新：2026-01-11


需要补充：
- [x] 确认完整的 API 基础 URL：已确认为：https://api.cnb.cool/
- [x] 确认获取最新版本的实际端点路径:可参考cnb_doc.json文档
- [x] 确认获取指定版本的实际端点路径:可参考cnb_doc.json文档
- [x] 确认发布资源下载链接格式:可参考cnb_doc.json文档
需要补充：
- [x] uv 应用的 receipt.json 位置和内容示例:
> {"binaries":["uv.exe","uvx.exe","uvw.exe"],"binary_aliases":{},"cdylibs":[],"cstaticlibs":[],"install_layout":"flat","install_prefix":"C:\\Users\\dinof\\.local\\bin","modify_path":true,"provider":{"source":"cargo-dist","version":"0.30.2"},"source":{"app_name":"uv","name":"uv","owner":"astral-sh","release_type":"github"},"version":"0.9.16"}
- [x] receipt 中如何指定 CNB 作为发布源,见上述内容示例
- [x] receipt 中 CNB 特定字段说明:见上述内容示例

需要补充：
以下事项请在开发中用python脚本，结合cnb_doc验证
- [x] GetLatestRelease 实际响应格式（JSON 示例）
- [x] GetReleaseByID 实际响应格式
- [x] 资源下载链接的实际格式
- [x] 错误响应格式
需要补充：
- [x] CNB.cool 是否支持 anonymous 访问（无 token）:不支持，必须用token，我会提供一个guest权限的token（db5HVM2xIiR0Zo11dcsuL4WeHGE），配置到开发好的项目中。
- [x] token 权限范围说明:只读
- [x] API rate limit 限制:无限制
- [x] 网络超时建议值:重试3次（每次30秒）后报错终止
在 DEVELOPMENT_PLAN.md 中补充：
- [x] .env.example 文件模板:这是个github平台项目
- [x] 测试命令示例：替我做计划
- [x] 预期的测试输出：整体预期是开发好后的二进制代码可以将目标平滑升级
