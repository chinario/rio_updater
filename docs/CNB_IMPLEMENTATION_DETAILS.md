# CNB.cool 集成实现详解

## 概述

rio_updater 项目对 CNB.cool 平台的支持**完全基于官方 JSON API**，而**不是 HTML 解析**。这是一个正式的、结构化的实现。

---

## 实现架构

### 核心组件

```
┌─────────────────────────────────────────────────────┐
│         axoupdater/src/release/cnb.rs (613行)       │
├─────────────────────────────────────────────────────┤
│  CnbClient                  [HTTP 客户端]           │
│  └─ RESTful API 调用        [基于 reqwest]          │
│     └─ JSON 反序列化       [基于 serde]            │
│        └─ 强类型结构体      [Rust 结构体]           │
└─────────────────────────────────────────────────────┘
```

### API 端点

| 功能 | 端点 | 方法 |
|------|------|------|
| **获取最新发布** | `/{repo}/-/releases/latest` | GET |
| **按标签获取发布** | `/{repo}/-/releases/tags/{tag}` | GET |
| **按 ID 获取发布** | `/{repo}/-/releases/{id}` | GET |
| **列出所有发布** | `/{repo}/-/releases?page=X&page_size=Y` | GET |
| **下载资源** | `/{repo}/-/releases/download/{tag}/{filename}` | GET |

---

## 数据结构

### 1. CnbRelease - 发布信息

```rust
pub struct CnbRelease {
    pub id: String,                          // 唯一标识符
    pub tag_name: Option<String>,            // 标签名称 (如: "v0.9.18")
    pub name: String,                        // 发布名称
    pub body: Option<String>,                // 发布说明 (Markdown)
    pub draft: bool,                         // 是否为草稿
    pub is_latest: bool,                     // 是否为最新版本
    pub prerelease: Option<bool>,            // 是否为预发布版本
    pub author: Option<CnbAuthor>,           // 作者信息
    pub assets: Vec<CnbAsset>,               // 发布资源列表
    pub created_at: String,                  // 创建时间
    pub updated_at: Option<String>,          // 更新时间
    pub published_at: Option<String>,        // 发布时间
}
```

### 2. CnbAsset - 发布资源

```rust
pub struct CnbAsset {
    pub id: String,                          // 资源唯一标识
    pub name: String,                        // 文件名
    pub size: Option<i64>,                   // 文件大小 (字节)
    pub download_url: Option<String>,        // 下载 URL
    pub browser_download_url: Option<String>,// 浏览器下载 URL
    pub content_type: Option<String>,        // MIME 类型
    pub created_at: Option<String>,          // 创建时间
}
```

### 3. CnbAuthor - 作者信息

```rust
pub struct CnbAuthor {
    pub username: Option<String>,            // 用户名
    pub name: Option<String>,                // 显示名称
    pub avatar_url: Option<String>,          // 头像 URL
}
```

---

## API 调用方法

### 1. 获取最新发布（高级用法）

```rust
let client = CnbClient::new(None);
let release = client.fetch_latest_release("astral-sh/uv").await?;

println!("Latest version: {}", release.tag_name.unwrap());
println!("Assets: {} files", release.assets.len());
```

**API 响应示例**：
```json
{
  "id": "release_12345",
  "tag_name": "0.9.18",
  "name": "Release 0.9.18",
  "draft": false,
  "prerelease": false,
  "assets": [
    {
      "id": "asset_001",
      "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
      "size": 22200000,
      "download_url": "/astral-sh/uv/-/releases/download/0.9.18/uv-x86_64-unknown-linux-gnu.tar.gz",
      "browser_download_url": "https://cnb.cool/astral-sh/uv/-/releases/download/0.9.18/uv-x86_64-unknown-linux-gnu.tar.gz"
    }
  ]
}
```

### 2. 按标签获取特定版本

```rust
let client = CnbClient::new(None);
let release = client.fetch_release_by_tag("astral-sh/uv", "0.9.18").await?;
```

### 3. 列出所有发布（支持分页）

```rust
let client = CnbClient::new(None);
let releases = client.list_releases("astral-sh/uv", Some(1), Some(10)).await?;
```

### 4. 下载资源文件

```rust
let client = CnbClient::new(None);
let response = client.download_asset(
    "astral-sh/uv",
    "0.9.18",
    "uv-x86_64-unknown-linux-gnu.tar.gz"
).await?;

// 保存响应到文件
let bytes = response.bytes().await?;
```

---

## HTTP 客户端配置

### 请求头配置

```rust
let mut headers = HeaderMap::new();
headers.insert(
    ACCEPT,
    "application/vnd.cnb.api+json"
        .parse()
        .unwrap_or_else(|_| HeaderValue::from_static("application/json"))
);
```

**关键配置**：
- ✅ Content-Type: `application/vnd.cnb.api+json`
- ✅ Accept 头正确设置
- ✅ 30秒超时配置
- ✅ Bearer token 认证支持

### 认证支持

```rust
// 创建需要认证的客户端
let client = CnbClient::new(Some("your-api-token".to_string()));

// 或动态设置 token
let mut client = CnbClient::new(None);
client.set_token("your-api-token".to_string());
```

---

## 错误处理

### 支持的错误类型

```rust
pub enum CnbError {
    HttpError(String),              // HTTP 请求失败
    InvalidResponse(String),        // 响应格式无效
    ApiError { code: i32, message: String },  // API 返回错误
    AuthError(String),              // 认证失败 (401/403)
    NotFound(String),               // 资源不存在 (404)
    RateLimited,                    // 速率限制 (429)
    Timeout,                        // 请求超时
}
```

### 重试机制

```rust
// 自动重试最多 3 次
// 指数退避: 1秒、2秒、4秒
async fn execute_with_retry<T>(
    &self,
    method: &str,
    url: &str,
    max_retries: u32,  // 默认为 3
) -> Result<T, CnbError>
```

**重试策略**：
- ✅ 超时错误自动重试
- ✅ 指数退避时间间隔
- ✅ 客户端错误（4xx）不重试
- ✅ 速率限制（429）返回错误

---

## 与 install-cnb-uv.sh 的区别

### Rust 库实现 (cnb.rs)

```rust
// JSON API - 官方数据格式
let release = client.fetch_latest_release("astral-sh/uv").await?;
let assets = release.assets;
let download_url = asset.browser_download_url;
```

**特点**：
- ✅ 完整的 JSON 解析
- ✅ 强类型保证
- ✅ 异步支持
- ✅ 错误处理完善
- ✅ 适合库集成

### Shell 脚本实现 (install-cnb-uv.sh)

```bash
# HTML 页面 - 简化处理
release_tag=$(curl -s "${CNB_BASE_URL}/${CNB_REPO}/-/releases" | \
    grep -o '"tagRef":"refs/tags/[^"]*"' | head -1 | \
    cut -d'"' -f4 | sed 's|refs/tags/||')
```

**特点**：
- ✅ 轻量级（11KB）
- ✅ 无外部依赖
- ✅ POSIX shell 兼容
- ✅ 适合直接使用
- ⚠️ 基于 HTML 文本解析

---

## 数据流示意

```
用户应用
    │
    ├─► axoupdater 库
    │    │
    │    └─► CnbClient
    │         │
    │         ├─► fetch_latest_release()
    │         │    │
    │         │    ├─► HTTP GET
    │         │    │    │
    │         │    │    └─► https://api.cnb.cool/{repo}/-/releases/latest
    │         │    │
    │         │    └─► JSON 反序列化
    │         │         │
    │         │         └─► CnbRelease 结构体
    │         │
    │         └─► 返回强类型数据
    │              │
    │              └─► Release { assets, version, ... }
    │
    └─► install-cnb-uv.sh 脚本
         │
         ├─► curl HTML 页面
         │    │
         │    └─► https://cnb.cool/{repo}/-/releases
         │
         ├─► grep + sed 文本解析
         │    │
         │    └─► 提取版本号
         │
         └─► 构造下载 URL
              │
              └─► https://cnb.cool/{repo}/-/releases/download/{tag}/{file}
```

---

## 架构对比

| 特性 | cnb.rs 库 | install-cnb-uv.sh |
|------|----------|-------------------|
| **数据格式** | JSON API | HTML 文本 |
| **解析方式** | serde 反序列化 | grep + sed |
| **类型安全** | ✅ 完全 | ❌ 无 |
| **错误处理** | ✅ 完善 | ⚠️ 基础 |
| **性能** | ✅ 高效 | ⚠️ 文本处理 |
| **依赖** | reqwest, serde | curl, grep, sed |
| **用途** | 库集成 | 直接安装 |
| **维护性** | ✅ 高 | ⚠️ 中 |

---

## 关键优势

### 1. 官方 API 使用

✅ **优点**：
- 完全遵循官方 API 设计
- 获得正式支持和文档
- 版本化 API 端点
- 专业的数据结构

### 2. 强类型系统

✅ **优点**：
- 编译时类型检查
- IDE 自动补全
- 减少运行时错误
- 易于重构和维护

### 3. 异步支持

✅ **优点**：
- Tokio 异步运行时
- 高效的网络处理
- 支持并发请求
- 非阻塞操作

### 4. 完善的错误处理

✅ **优点**：
- 具体的错误类型
- 自动重试机制
- 指数退避策略
- 超时和速率限制处理

---

## 使用示例

### 在 Rust 项目中使用

```rust
use axoupdater::{AxoUpdater, ReleaseSourceType};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut updater = AxoUpdater::new_for("uv");
    
    // 配置 CNB 释放源
    updater.set_release_source(ReleaseSourceType::CNB, "astral-sh/uv");
    
    // 检查更新
    let receipt = updater.load_receipt()?;
    if receipt.is_update_needed().await? {
        println!("New version available!");
        receipt.run().await?;
    }
    
    Ok(())
}
```

### 直接使用 CnbClient

```rust
use axoupdater::release::cnb::CnbClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = CnbClient::new(None);
    
    // 获取最新版本
    let release = client.fetch_latest_release("astral-sh/uv").await?;
    println!("Latest: {}", release.tag_name.unwrap());
    
    // 列出所有资源
    for asset in release.assets {
        println!("- {} ({})", asset.name, asset.size.unwrap_or(0));
    }
    
    Ok(())
}
```

---

## 测试覆盖

项目包含以下测试：
- `Other/test_cnb_platform.py` - Python 集成测试
- `Other/test_cnb_uv_integration.py` - uv 集成测试
- `Other/test_cnb_with_uv.py` - 完整测试

---

## 总结

| 方面 | 说明 |
|------|------|
| **API 类型** | ✅ RESTful JSON API |
| **数据解析** | ✅ serde JSON 反序列化 |
| **HTTP 客户端** | ✅ reqwest |
| **错误处理** | ✅ 完善的错误类型和重试 |
| **认证方式** | ✅ Bearer token |
| **支持级别** | ✅ 完整的官方 API 支持 |

**rio_updater 的 CNB 实现是生产级别的、正式的、基于官方 API 的集成。**

---

**文档更新**: 2026-01-11  
**维护者**: rio_updater 项目团队
