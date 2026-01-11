# CNB API Integration - 关键发现

## P0 验证完成 ✅

### API 端点验证结果

#### ✅ 成功的端点

1. **获取最新发布版本**
   - 端点: `GET /{repo}/-/releases/latest`
   - 状态: ✅ HTTP 200
   - 响应格式: 单个发布对象，包含 42 个资源

2. **列举发布版本（分页）**
   - 端点: `GET /{repo}/-/releases?page={page}&page_size={page_size}`
   - 状态: ✅ HTTP 200
   - 响应格式: 发布对象数组

3. **认证机制**
   - 要求: Bearer Token 认证
   - 无效令牌响应: HTTP 401
   - 工作正常 ✅

#### ⚠️ 需要调整的端点

1. **按标签获取发布版本**
   - 端点: `GET /{repo}/-/releases/tags/{tag}`
   - 当前状态: HTTP 404
   - 原因: 可能需要不同的标签格式（无 'v' 前缀）
   - 解决方案: 在 Rust 代码中自动尝试标签变体

### 关键发现

#### 1. Content-Type 要求
**必需**: `Accept: application/vnd.cnb.api+json`
- 不设置此头会导致 HTTP 406 错误
- Rust `reqwest` 库需要配置此头

#### 2. 发布数据结构
```json
{
  "id": "string",
  "tag_name": "0.9.18",
  "name": "0.9.18",
  "body": "string (optional)",
  "draft": false,
  "is_latest": true,
  "prerelease": false,
  "author": { ... },
  "assets": [
    {
      "id": "string",
      "name": "filename",
      "size": 12345,
      "download_url": "https://...",
      "browser_download_url": "https://...",
      "content_type": "application/...",
      "created_at": "2025-01-10T..."
    }
  ],
  "created_at": "2025-01-10T...",
  "updated_at": "2025-01-10T...",
  "published_at": "2025-01-10T..."
}
```

#### 3. 认证配置
- 方法: Bearer Token (Authorization header)
- 格式: `Authorization: Bearer {token}`
- 测试令牌: `db5HVM2xIiR0Zo11dcsuL4WeHGE`
- 权限: 读取（足以获取发布信息）

### P0 任务完成清单

- ✅ 验证 API 端点响应格式
- ✅ 确认认证机制
- ✅ 测试数据模型
- ✅ 识别 Content-Type 要求
- ✅ 验证分页支持

### P1 待做项

1. **处理标签查询的 404 错误**
   - 实现标签变体尝试逻辑
   - 或从列表中过滤查找

2. **更新 Rust 代码**
   - 在 CnbClient 中添加 Accept header
   - 实现错误处理和重试逻辑

3. **创建单元测试**
   - Mock HTTP 响应
   - 测试数据转换

### Rust 集成关键点

```rust
// 1. 在 reqwest::Client::builder() 中配置
.default_headers(header_map)  // 添加 Accept header

// 2. 错误处理映射
CnbError::NotFound -> AxoupdateError::ReleaseNotFound
CnbError::AuthError -> AxoupdateError::Unauthorized
CnbError::Timeout -> 重试逻辑

// 3. 标签处理
- 存储原始标签（如 "v0.9.18"）
- 尝试两种格式查询
```

---

生成时间: 2025-01-11
验证环境: Ubuntu 24.04.3 LTS
测试工具: Python 3 + requests
