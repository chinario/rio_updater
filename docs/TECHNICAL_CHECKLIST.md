# 技术验收清单

## 📋 项目完成度分析

### 已完成的部分 ✅

- [x] 高级开发规划（DEVELOPMENT_PLAN.md）
- [x] CNB 平台 Token 获取（db5HVM2xIiR0Zo11dcsuL4WeHGE）
- [x] 测试场景确定（astral-sh/uv 项目）
- [x] 测试版本策略（0.9.17 → 0.9.18）

---

## 📌 立即需要补充的信息（优先级：高）

### 1. API 端点验证清单

**任务**: 确认 CNB.cool 的实际 API 端点

```
需要完成的步骤:
□ 访问 https://docs.cnb.cool/ 查看 API 文档
□ 提取实际的 API 基础 URL（如：https://api.cnb.cool/v1）
□ 记录获取最新版本的完整端点
□ 记录获取指定版本的完整端点
□ 记录发布资源下载链接的完整路径格式
□ 测试每个端点的返回格式（JSON 结构）

填充位置：CNB_API_INTEGRATION.md
```

### 2. Receipt 格式验证

**任务**: 获取并分析实际的 receipt.json 格式

```
需要完成的步骤:
□ 在 uv 应用目录找到 receipt.json
  Linux/macOS: ~/.config/uv/receipt.json
  Windows: %LOCALAPPDATA%\uv\receipt.json
□ 将完整内容复制保存
□ 分析 CNB 特定的字段（source、cnb 字段等）
□ 确定如何在 receipt 中指定 CNB 作为发布源
□ 确定如何在 receipt 中存储 CNB 仓库标识

填充位置：CNB_API_INTEGRATION.md 第 3 节
```

### 3. 本地测试验证

**任务**: 测试 CNB API 实际连接

```bash
# 需要在本地运行以下命令并记录输出

# 测试 1: 验证 Token 有效性
curl -i -H "Authorization: Bearer db5HVM2xIiR0Zo11dcsuL4WeHGE" \
  https://api.cnb.cool/repos/astral-sh/uv/releases/latest

# 测试 2: 获取最新版本
# 记录：状态码、响应时间、JSON 结构

# 测试 3: 获取指定版本 (0.9.17)
# 记录：响应结构与最新版本是否一致

填充位置：TESTING_RESULTS.md（新文件）
```

---

## 🔧 第二阶段需要的支撑文档

### 4. 错误处理映射表

**任务**: 确定 CNB API 的所有可能错误

```
需要补充的表格：

| HTTP 状态码 | CNB 错误码 | 说明 | Rust 错误类型 |
|-----------|-----------|------|-------------|
| 200 | - | 成功 | OK |
| 401 | UNAUTHORIZED | 无效 token | CnbError::Unauthorized |
| 403 | FORBIDDEN | 权限不足 | CnbError::PermissionDenied |
| 404 | NOT_FOUND | 版本不存在 | CnbError::NotFound |
| 429 | RATE_LIMITED | 超过限制 | CnbError::RateLimited |
| 500+ | SERVER_ERROR | 服务器错误 | CnbError::ServerError |

填充位置：CNB_API_INTEGRATION.md 第 4 节
```

### 5. Rate Limit 配置

**任务**: 确定 CNB 平台的限流策略

```
需要确认：
□ 单个 token 的请求速率限制（如：60 req/min）
□ 突发容量（burst capacity）
□ 重试策略（Retry-After 响应头）
□ 是否有月度 API 配额限制
□ 不同操作的成本是否不同

填充位置：CNB_API_INTEGRATION.md 第 5 节
```

---

## 📊 数据流图补充

**任务**: 创建清晰的数据流程图

```
需要创建的文档：DATA_FLOW.md

内容：
1. 应用启动 → 读取 receipt.json → 确定更新源（CNB）
2. 调用 CNB API → 获取最新版本信息
3. 版本比对 → 确定是否需要更新
4. 下载更新包 → 完整性验证 → 安装
5. 更新 receipt.json → 完成
```

---

## 🧪 测试框架准备

**任务**: 设置 Mock 测试框架

```
需要补充：

1. Mock HTTP 响应数据集
   文件：tests/fixtures/cnb_responses.json
   内容：
   - GetLatestRelease 成功响应
   - GetReleaseByTag 成功响应
   - 各种错误响应示例

2. 测试数据
   文件：tests/fixtures/cnb_test_data.rs
   内容：
   - 测试仓库标识符
   - 版本号数据
   - 资源 URL 示例

填充位置：新增 tests/ 目录
```

---

## 📝 缺失的配置文件

### 需要创建的文件

```
project_root/
├── .env.example              ✅ 已创建
├── CNB_API_INTEGRATION.md    ✅ 已创建
├── TESTING_RESULTS.md        ❌ 需创建
├── DATA_FLOW.md              ❌ 需创建
├── tests/
│   ├── fixtures/
│   │   ├── cnb_responses.json   ❌ 需创建
│   │   └── cnb_test_data.rs     ❌ 需创建
│   └── cnb_integration_test.rs  ❌ 需创建
└── docs/
    ├── CNB_ARCHITECTURE.md      ❌ 需创建
    ├── CNB_USAGE.md            ❌ 需创建
    └── CNB_DEVELOPMENT.md      ❌ 需创建
```

---

## ✔️ 优先级排序

### 🔴 **第 1 优先级（本周完成）**
1. API 端点验证 → 填充 CNB_API_INTEGRATION.md
2. 本地 API 测试 → 生成 TESTING_RESULTS.md
3. Receipt 格式确认 → 补充样本 receipt.json

### 🟠 **第 2 优先级（下周开始）**
4. 创建 DATA_FLOW.md（数据流图）
5. 设置 Mock 测试数据集
6. 开始 cnb.rs 模块开发

### 🟡 **第 3 优先级（开发中）**
7. 编写详细的架构文档
8. 完成单元测试框架
9. 编写集成测试

---

## 📞 需要用户提供的信息

请在 GitHub Issue 或邮件中提供以下信息：

```markdown
1. CNB.cool API 文档链接
   - 官方 API 文档 URL
   - Swagger/OpenAPI 规范位置

2. API 端点实际情况
   - 基础 URL 确认
   - 端点路径格式
   - 请求/响应示例（真实 JSON）

3. 认证与权限
   - Token 的有效期
   - 权限范围说明
   - 是否支持 anonymous 访问

4. receipt.json 示例
   - CNB 格式的完整样本
   - 特定字段说明

5. Rate Limit 信息
   - 请求频率限制
   - 限流恢复策略
```

---

## 最后验收标准

在开始核心开发（第二阶段）前，需要完成：

- [ ] CNB_API_INTEGRATION.md 信息完整（90% 以上）
- [ ] TESTING_RESULTS.md 测试记录齐全
- [ ] .env.example 配置正确可用
- [ ] 本地能成功调用至少一个 CNB API
- [ ] Receipt 格式已确认和文档化
- [ ] 错误映射表已建立
- [ ] DATA_FLOW.md 已绘制

**预计完成日期**: 2026-01-15

---

**更新时间**: 2026-01-11
**维护人**: @chinario
