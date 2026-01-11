# CNB.cool API 集成指南

## 1. API 基础信息

### 基础 URL
```
https://api.cnb.cool  # 需要确认
```

### 认证方式
```http
Authorization: Bearer {token}
# Token: db5HVM2xIiR0Zo11dcsuL4WeHGE
```

---

## 2. 关键 API 端点

### 2.1 获取最新版本
**端点**: `/repos/{owner}/{repo}/releases/latest`

**请求示例**:
```http
GET /repos/astral-sh/uv/releases/latest HTTP/1.1
Authorization: Bearer db5HVM2xIiR0Zo11dcsuL4WeHGE
Host: api.cnb.cool
```

**响应格式** (需实际验证):
```json
{
  "id": 12345,
  "tag_name": "0.9.18",
  "name": "uv 0.9.18",
  "body": "Release notes...",
  "prerelease": false,
  "created_at": "2026-01-11T10:00:00Z",
  "published_at": "2026-01-11T10:00:00Z",
  "assets": [
    {
      "id": 67890,
      "name": "uv-0.9.18-x86_64-unknown-linux-gnu.tar.gz",
      "browser_download_url": "https://storage.cnb.cool/...",
      "content_type": "application/gzip"
    }
  ]
}
```

### 2.2 按 Tag 获取版本
**端点**: `/repos/{owner}/{repo}/releases/tags/{tag}`

### 2.3 按 ID 获取版本
**端点**: `/repos/{owner}/{repo}/releases/{id}`

### 2.4 下载资源
**端点**: `/repos/{owner}/{repo}/releases/assets/{asset_id}`

---

## 3. Receipt 信息

### receipt.json 位置
```
Linux/macOS: ~/.config/uv/receipt.json
Windows: %LOCALAPPDATA%\uv\receipt.json
```

### receipt.json 示例结构 (需实际获取)
```json
{
  "version": 1,
  "installer": {
    "kind": "cargo-dist",
    "version": "0.12.0"
  },
  "installed_version": "0.9.17",
  "platform": {
    "os": "linux",
    "arch": "x86_64"
  },
  "source": "cnb",
  "cnb": {
    "owner": "astral-sh",
    "repo": "uv",
    "api_base": "https://api.cnb.cool"
  }
}
```

---

## 4. 错误处理

### CNB API 错误响应格式

```json
{
  "code": "NOT_FOUND",
  "message": "Release not found",
  "details": "..."
}
```

### HTTP 状态码
- `200 OK` - 成功
- `401 Unauthorized` - 认证失败 (无效 token)
- `403 Forbidden` - 权限不足
- `404 Not Found` - 资源不存在
- `429 Too Many Requests` - 超过 rate limit
- `500+ Server Error` - 服务器错误

---

## 5. Rate Limit

**需要确认**:
- [ ] 单个 token 的请求限制 (例如: 60 req/min)
- [ ] 是否有突发请求容量
- [ ] 超限响应头说明

---

## 6. 平台特性

| 特性 | 支持状态 | 说明 |
|------|---------|------|
| Bearer Token | ✅ | 已确认 |
| Anonymous 访问 | ❓ | 需确认 |
| 预发布版本 | ❓ | 需确认 |
| 大文件下载 | ❓ | 需确认 |
| 断点续传 | ❓ | 需确认 |
| 自签名证书 | ❓ | 需确认 |

---

## 7. 测试场景验证清单

### 测试用例 1: 获取最新版本
```bash
# 环境配置
export CNB_TOKEN="db5HVM2xIiR0Zo11dcsuL4WeHGE"
export CNB_REPO="astral-sh/uv"

# 预期结果: 返回版本 0.9.18（或当前最新版本）
curl -H "Authorization: Bearer $CNB_TOKEN" \
  "https://api.cnb.cool/repos/$CNB_REPO/releases/latest"
```

### 测试用例 2: 按 Tag 获取版本
```bash
# 预期结果: 返回版本 0.9.17
curl -H "Authorization: Bearer $CNB_TOKEN" \
  "https://api.cnb.cool/repos/$CNB_REPO/releases/tags/0.9.17"
```

### 测试用例 3: 版本比对
```
已安装版本: 0.9.17
最新版本: 0.9.18
预期: 检测到可用更新
```

---

## 8. 下一步行动

1. **API 文档获取** (优先级 1)
   - [ ] 访问 cnb.cool API 文档获取实际端点
   - [ ] 记录完整的 URL 路径
   - [ ] 验证请求/响应格式

2. **本地测试** (优先级 1)
   ```bash
   # 用实际 token 和 repo 测试
   curl -H "Authorization: Bearer db5HVM2xIiR0Zo11dcsuL4WeHGE" \
     "https://api.cnb.cool/repos/astral-sh/uv/releases/latest"
   ```

3. **Receipt 验证** (优先级 2)
   - [ ] 从 uv 应用获取实际 receipt.json
   - [ ] 分析字段结构
   - [ ] 确定 CNB 特定字段

4. **错误场景测试** (优先级 2)
   - [ ] 使用无效 token 测试 401 响应
   - [ ] 请求不存在的版本测试 404
   - [ ] 记录所有可能的错误码
