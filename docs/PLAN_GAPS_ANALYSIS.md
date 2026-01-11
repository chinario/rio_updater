# DEVELOPMENT_PLAN 缺口分析报告

## 🔴 发现的 10 个关键缺口

### 缺口 1: API 端点实际 URL 缺失

**位置**: 第一阶段 1.1 - API 功能梳理

**问题**:
- 计划中没有记录 CNB.cool 的实际 API 基础 URL
- 没有具体的端点路径
- cnb_doc.json 提供了 Swagger 规范，但没有实际端点列表

**需要补充**:
```markdown
### 1.1.5 API 端点列表（核心）

- [ ] 确认 CNB API 基础 URL：_______
- [ ] 获取最新版本端点：_______
- [ ] 获取指定版本端点：_______
- [ ] 获取资源下载链接格式：_______
- [ ] 示例调用：
  ```bash
  curl -H "Authorization: Bearer {token}" \
    {base_url}/repos/{owner}/{repo}/releases/latest
  ```
```

---

### 缺口 2: Receipt 格式规范缺失

**位置**: 第一阶段 1.3 - 环境准备

**问题**:
- 没有提供实际的 receipt.json 样本
- 没有说明 CNB 相关的字段
- 没有规范 receipt 中如何指定 CNB 作为发布源

**需要补充**:
```markdown
### 1.3.4 Receipt 格式文档

- [ ] 获取实际的 receipt.json 样本
- [ ] 文档位置：docs/RECEIPT_FORMAT.md
- [ ] 包含内容：
  - CNB 特定字段说明
  - 字段映射关系
  - 示例文件（完整）
  
**关键问题需解答**:
- receipt 中如何识别 CNB 源？
- 如何存储仓库标识？(owner/repo vs 其他)
- 如何存储 API base URL？
- 是否需要存储 token？
```

---

### 缺口 3: 依赖版本检查不完整

**位置**: 第一阶段 1.3 - 依赖检查

**问题**:
- 只列出了要检查的依赖，没有指定版本
- 没有检查现有依赖是否已包含所需库
- 没有提及可能的依赖冲突

**需要补充**:
```markdown
### 1.3.3 依赖检查（详细版）

在 axoupdater/Cargo.toml 中：

- [ ] **reqwest**: 
  - 当前版本：_______（查看 Cargo.lock）
  - 需要功能：json, stream, cookies
  - 兼容性：需要支持 async/await

- [ ] **serde/serde_json**:
  - 当前版本：_______
  - 需要特性：derive

- [ ] **tokio**:
  - 当前版本：_______
  - 确认已有 async runtime

- [ ] **新增依赖**:
  - [ ] mockito (用于测试)：_______
  - [ ] 其他：_______
```

---

### 缺口 4: 与现有源的差异对比缺失

**位置**: 第一阶段 1.1 - 对比分析

**问题**:
- "对比分析" 部分没有实际的对比结果
- 没有列出 GitHub vs Axo vs CNB 的差异表

**需要补充**:
```markdown
### 1.1.4 发布源对比分析表

| 特性 | GitHub | Axo | CNB | 优先级 |
|------|--------|-----|-----|--------|
| 获取最新版本 | ✅ | ✅ | ❓ | 高 |
| 获取指定版本 | ✅ | ✅ | ❓ | 高 |
| 获取资源列表 | ✅ | ✅ | ❓ | 高 |
| Token 认证 | ✅ | ✅ | ✅ | 高 |
| Anonymous 访问 | ✅ | ❓ | ❓ | 中 |
| Rate Limit | 60/hr | ❓ | ❓ | 中 |
| 预发布版本 | ✅ | ✅ | ❓ | 中 |
| 资源下载 | Direct | Direct | ❓ | 高 |
| 断点续传 | ✅ | ❓ | ❓ | 低 |

填充位置：docs/cnb_api_analysis.md
```

---

### 缺口 5: 错误映射表缺失

**位置**: 第二阶段 2.1 - 错误处理

**问题**:
- 没有具体的错误码映射
- 没有 CNB 错误响应的实际示例
- 没有重试策略的详细说明

**需要补充**:
```markdown
### 2.1.5 错误处理映射

**任务**: 建立 CNB 错误 → Rust Error 的映射表

- [ ] **HTTP 4xx 错误**:
  - 401 Unauthorized → CnbError::Unauthorized
  - 403 Forbidden → CnbError::PermissionDenied
  - 404 Not Found → CnbError::NotFound
  - 429 Too Many Requests → CnbError::RateLimited

- [ ] **HTTP 5xx 错误**:
  - 500+ Server Error → CnbError::ServerError

- [ ] **CNB 特有错误**:
  - _______（需实际 API 文档）

- [ ] **重试策略**:
  - [ ] 哪些错误应该重试？
  - [ ] 重试次数上限：3 次
  - [ ] 退避策略：指数退避（初始 1s，最大 30s）
  - [ ] 哪些错误不应重试？(认证错误、权限错误等)
```

---

### 缺口 6: 异步 vs 同步实现选择缺失

**位置**: 第二阶段 2.1 - CNB 客户端实现

**问题**:
- 没有说明是否需要同步版本（blocking feature）
- 没有说明两个版本的代码结构

**需要补充**:
```markdown
### 2.1 补充：实现两个版本

**决定**: 是否支持 blocking 特性？

如果支持，需要：
- [ ] 设计 `CnbClient` 和 `CnbClientBlocking` 结构
- [ ] 使用 `#[cfg(feature = "blocking")]` 条件编译
- [ ] 提供两套 API 方法
- [ ] 两套都需要测试

实现位置：
- 异步版本：axoupdater/src/release/cnb.rs
- 同步版本：axoupdater/src/release/cnb_blocking.rs (可选)
```

---

### 缺口 7: 测试数据集缺失

**位置**: 第三阶段 3.1 - 单元测试

**问题**:
- 没有列出 Mock 测试数据集
- 没有指定测试数据文件的具体内容
- 没有说明如何生成 Mock 响应

**需要补充**:
```markdown
### 3.1 补充：测试 fixtures

**创建测试数据文件**:

1. **tests/fixtures/cnb_responses.json**
   - [ ] GetLatestRelease 成功响应
   - [ ] GetReleaseByTag 成功响应
   - [ ] 401 认证失败响应
   - [ ] 404 版本不存在响应
   - [ ] 429 Rate limit 响应

2. **tests/fixtures/test_data.rs**
   - [ ] 测试版本号集合
   - [ ] 测试仓库标识
   - [ ] 测试 token
   - [ ] 测试 URL

3. **使用 mockito 框架**
   - [ ] Mock server 设置
   - [ ] 响应数据加载
   - [ ] 请求验证
```

---

### 缺口 8: CI/CD 集成计划缺失

**位置**: 第四阶段 4.2 - 代码审查准备

**问题**:
- 没有提及 CI/CD 配置
- 没有提到 GitHub Actions 工作流
- 没有测试覆盖率报告设置

**需要补充**:
```markdown
### 4.2 补充：CI/CD 集成

- [ ] 更新 .github/workflows/ci.yml
  - [ ] 添加 CNB 特性编译检查
  - [ ] 添加 CNB 相关测试
  - [ ] 添加 token 环境变量配置

- [ ] 代码覆盖率报告
  - [ ] 配置 codecov
  - [ ] 设置覆盖率阈值 > 80%

- [ ] 安全检查
  - [ ] cargo audit
  - [ ] 敏感信息检查 (token 不提交)

工作流文件位置：.github/workflows/cnb_tests.yml
```

---

### 缺口 9: 发布前检查清单缺失

**位置**: 第四阶段 4.3 - 版本发布

**问题**:
- "发布前检查" 太笼统
- 没有具体的检查项和验证方法
- 没有回滚计划

**需要补充**:
```markdown
### 4.3 补充：发布检查清单

**发布前 1 天**:
- [ ] 所有代码提交已合并到 main
- [ ] 所有 PR 已审查
- [ ] CI/CD 全部通过

**发布前 1 小时**:
- [ ] 运行 `cargo test --all-features`
- [ ] 运行 `cargo clippy -- -D warnings`
- [ ] 运行 `cargo fmt --check`
- [ ] 运行 `cargo audit`
- [ ] 验证覆盖率 > 80%

**发布本身**:
- [ ] 更新 CHANGELOG.md (含 CNB 相关)
- [ ] 更新 Cargo.toml 版本号
- [ ] 本地验证：`cargo build --release --all-features`
- [ ] Git tag: `git tag v0.x.0`
- [ ] cargo publish

**发布后验证**:
- [ ] 验证 crates.io 上的版本
- [ ] 验证文档生成正确
- [ ] 验证 GitHub release 创建成功
- [ ] 测试 `cargo install axoupdater` 可行

**回滚计划**:
- [ ] 如何撤回已发布的版本？
- [ ] 如何通知用户？
```

---

### 缺口 10: 知识库和培训计划缺失

**位置**: 文档部分

**问题**:
- 没有为团队成员提供学习资料
- 没有常见问题解答
- 没有故障排查指南

**需要补充**:
```markdown
## 补充：知识库和培训

### 团队培训计划

- [ ] **CNB.cool 平台学习**
  - 官方文档：https://docs.cnb.cool/
  - 文档检查清单：docs/LEARNING_PATH.md

- [ ] **axoupdater 架构学习**
  - 现有源码分析：docs/AXOUPDATER_ARCHITECTURE.md
  - GitHub/Axo 实现对比

- [ ] **开发工作坊**
  - 模块设计评审会议
  - API 集成演示
  - 测试策略讨论

### 常见问题 (FAQ)

文档位置：docs/FAQ_CNB.md

- 如何调试 CNB 连接问题？
- Token 过期如何处理？
- 如何处理网络超时？
- 如何在本地测试 CNB 集成？
- 如何查看 API 调用日志？
```

---

## 📊 缺口汇总表

| # | 缺口 | 严重程度 | 位置 | 补充位置 |
|---|------|--------|------|--------|
| 1 | API 端点 URL | 🔴 高 | 第一阶段 1.1 | 补充 1.1.5 |
| 2 | Receipt 格式 | 🔴 高 | 第一阶段 1.3 | 补充 1.3.4 |
| 3 | 依赖版本检查 | 🟠 中 | 第一阶段 1.3 | 补充 1.3.3 |
| 4 | 源对比分析 | 🟠 中 | 第一阶段 1.1 | 补充 1.1.4 |
| 5 | 错误映射表 | 🔴 高 | 第二阶段 2.1 | 补充 2.1.5 |
| 6 | Blocking 实现 | 🟠 中 | 第二阶段 2.1 | 补充说明 |
| 7 | 测试数据集 | 🔴 高 | 第三阶段 3.1 | 补充描述 |
| 8 | CI/CD 集成 | 🟠 中 | 第四阶段 4.2 | 补充说明 |
| 9 | 发布检查清单 | 🟡 低 | 第四阶段 4.3 | 补充说明 |
| 10 | 团队培训 | 🟡 低 | 新增章节 | 新增部分 |

---

## ✅ 立即行动项

**优先级 1（本周完成）**：
1. ✅ 补充 API 端点 URL（从 CNB 文档或测试）
2. ✅ 补充 Receipt 格式规范
3. ✅ 补充错误映射表

**优先级 2（下周完成）**：
4. 补充依赖版本检查清单
5. 补充源对比分析表
6. 补充测试数据集描述

**优先级 3（开发中）**：
7. 补充 blocking 实现选择
8. 补充 CI/CD 配置说明
9. 补充发布检查清单
10. 补充知识库/培训计划

---

## 💡 建议

**改进 DEVELOPMENT_PLAN.md 的方式**：

1. **添加新章节**: "## 技术决策记录"
   - 记录每个关键决策的理由
   - 例如：为什么选择异步？为什么使用 reqwest？

2. **添加新章节**: "## 参考资源"
   - CNB 官方文档链接
   - axoupdater 源码链接
   - 相关 Issue/PR

3. **创建配套文件树**:
   ```
   docs/
   ├── DEVELOPMENT_PLAN.md (现有)
   ├── TECHNICAL_CHECKLIST.md ✅ 已创建
   ├── CNB_API_INTEGRATION.md ✅ 已创建
   ├── RECEIPT_FORMAT.md (待创建)
   ├── ERROR_MAPPING.md (待创建)
   ├── TEST_FIXTURES.md (待创建)
   ├── FAQ_CNB.md (待创建)
   ├── LEARNING_PATH.md (待创建)
   └── RELEASE_CHECKLIST.md (待创建)
   ```

---

**更新时间**: 2026-01-11
