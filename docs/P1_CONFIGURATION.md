# P1 配置：CNB 集成完整设置

## 概览

P1 阶段确保所有配置和测试框架就位，为 Phase 2 开发做准备。

## ✅ 完成项

### 1. API 端点已验证
- ✅ `/releases/latest` - 获取最新发布
- ✅ `/releases` - 列举发布（分页）
- ✅ 认证机制有效
- ✅ Content-Type 要求已识别

### 2. 代码集成已完成
- ✅ `axoupdater/src/release/cnb.rs` 创建（~550 行）
- ✅ `ReleaseSourceType::CNB` 添加到枚举
- ✅ `set_cnb_token()` 方法添加
- ✅ `AuthorizationTokens::cnb` 字段添加
- ✅ `Cargo.toml` 更新（依赖和特性）
- ✅ `reqwest` 和 `serde_json` 依赖添加

### 3. 测试脚本已创建
- ✅ `scripts/test_cnb.sh` - bash 测试套件
- ✅ `scripts/verify_cnb_api.py` - Python API 验证
- ✅ 验证 4 个关键端点
- ✅ 认证测试通过

## 📋 配置清单

### Cargo.toml 依赖
```toml
[features]
cnb_releases = ["reqwest/json"]

[dependencies]
reqwest = { version = "0.11.24", features = ["json"], optional = true }
serde_json = "1.0.120"
```

### 环境配置
```bash
# .env 文件配置
export CNB_TOKEN="db5HVM2xIiR0Zo11dcsuL4WeHGE"
export API_BASE_URL="https://api.cnb.cool"
```

### 测试存储库
```
Owner: astral-sh
Repository: uv
Release Tags: v0.9.18, 0.9.18
```

## 🔧 API 详细规范

### 1. 最新发布端点
```http
GET https://api.cnb.cool/{owner}/{repo}/-/releases/latest
Authorization: Bearer {token}
Accept: application/vnd.cnb.api+json
```

**响应 (200):**
```json
{
  "id": "release_id",
  "tag_name": "0.9.18",
  "name": "0.9.18",
  "assets": [...],
  "is_latest": true,
  "created_at": "2025-01-10T12:00:00Z"
}
```

### 2. 列举发布端点
```http
GET https://api.cnb.cool/{owner}/{repo}/-/releases?page=1&page_size=10
Authorization: Bearer {token}
Accept: application/vnd.cnb.api+json
```

**响应 (200):** Release 对象数组

### 3. 按标签获取发布（需要验证格式）
```http
GET https://api.cnb.cool/{owner}/{repo}/-/releases/tags/{tag}
Authorization: Bearer {token}
Accept: application/vnd.cnb.api+json
```

**可能的标签格式:**
- `v0.9.18` (带前缀)
- `0.9.18` (不带前缀)

**建议:** Rust 实现应尝试两种格式或从列表过滤

## 📊 数据结构规范

### Release 模型
```rust
pub struct CnbRelease {
    pub id: String,                      // 唯一标识符
    pub tag_name: Option<String>,        // 标签名称
    pub name: String,                    // 显示名称
    pub body: Option<String>,            // 发布说明
    pub draft: bool,                     // 草稿状态
    pub is_latest: bool,                 // 是否最新
    pub prerelease: Option<bool>,        // 预发布标记
    pub author: Option<CnbAuthor>,       // 作者信息
    pub assets: Vec<CnbAsset>,           // 资源列表
    pub created_at: String,              // 创建时间
    pub updated_at: Option<String>,      // 更新时间
    pub published_at: Option<String>,    // 发布时间
}
```

### Asset 模型
```rust
pub struct CnbAsset {
    pub id: String,                          // 资源ID
    pub name: String,                        // 文件名
    pub size: Option<i64>,                   // 文件大小
    pub download_url: Option<String>,        // API下载URL
    pub browser_download_url: Option<String>, // 浏览器下载URL
    pub content_type: Option<String>,        // MIME类型
    pub created_at: Option<String>,          // 创建时间
}
```

## ⚙️ 集成检查清单

### Phase 2 前检查
- [ ] 代码编译通过: `cargo check --features cnb_releases`
- [ ] 所有测试通过: `cargo test --features cnb_releases`
- [ ] clippy 检查通过: `cargo clippy --features cnb_releases`
- [ ] fmt 检查通过: `cargo fmt --check`
- [ ] API 响应验证: `python3 scripts/verify_cnb_api.py`

### 代码质量
- [ ] 文档注释完整 (100% coverage)
- [ ] 错误处理完善
- [ ] 重试逻辑实现正确
- [ ] 无 `unwrap()` 调用（除了初始化）

### 测试覆盖
- [ ] 单元测试: 所有公共方法
- [ ] 集成测试: 完整的获取流程
- [ ] 错误测试: 404, 401, 429 响应
- [ ] Mock 测试: 使用 httpmock 库

## 📝 Next Steps

### 立即执行 (P1 完成)
1. ✅ 运行 API 验证脚本
2. ✅ 验证数据结构
3. ✅ 确认错误处理映射
4. ⏳ 编译检查（待 Rust 环境）

### Phase 2 开发准备
1. 创建详细的单元测试
2. 实现 mock HTTP 响应
3. 添加集成测试
4. 文档更新

## 📞 故障排除

### API 返回 406
**问题**: `application/vnd.cnb.api+json` Content-Type 缺失

**解决方案**: 
```rust
.default_header("Accept", "application/vnd.cnb.api+json")
```

### 标签查询返回 404
**问题**: 标签格式不匹配

**解决方案**:
```rust
// 尝试多种格式
let tag_variants = vec![tag, &tag.trim_start_matches('v')];
for variant in tag_variants {
    if let Ok(release) = fetch_release_by_tag(variant) {
        return Ok(release);
    }
}
```

### 认证失败
**问题**: Token 无效或缺失

**检查项**:
- [ ] Token 是否设置: `export CNB_TOKEN=...`
- [ ] 格式是否正确: `Bearer {token}`
- [ ] Token 是否过期（测试 token 无过期时间）

## 📦 交付物

- ✅ `/axoupdater/src/release/cnb.rs` (550 lines)
- ✅ `/axoupdater/Cargo.toml` (更新)
- ✅ `/axoupdater/src/release/mod.rs` (更新)
- ✅ `/axoupdater/src/lib.rs` (更新)
- ✅ `/scripts/test_cnb.sh`
- ✅ `/scripts/verify_cnb_api.py`
- ✅ `/docs/P0_VERIFICATION_RESULTS.md`
- ✅ `/docs/P1_CONFIGURATION.md` (本文件)

## 统计

- 代码行数: ~550 (cnb.rs)
- 集成点: 4 (mod.rs, lib.rs, release enum, Cargo.toml)
- 测试脚本: 2
- 文档: 2

---

**状态**: P1 完成 ✅
**下一阶段**: Phase 2 - 完整实现和测试
**预计时长**: 5-7 天
