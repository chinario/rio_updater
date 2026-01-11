# CNB 实现对比：JSON API vs HTML 解析

## 快速回答

**我们对 CNB 的支持是基于官方 JSON API 还是 HTML 解析？**

**答案：双轨制**

```
┌─────────────────────────────────┐
│   rio_updater 项目               │
├─────────────────────────────────┤
│                                 │
│  ✅ Rust 库 (cnb.rs)             │  
│     └─ JSON API (官方格式)       │
│                                 │
│  ⚠️ Shell 脚本 (install-cnb-uv) │  
│     └─ HTML 文本解析 (简化)      │
│                                 │
└─────────────────────────────────┘
```

---

## Rust 库：JSON API（推荐）

### 实现位置
- **文件**: `axoupdater/src/release/cnb.rs` (613 行)
- **类型**: 官方 RESTful JSON API

### 数据流

```
用户代码
   │
   └─► CnbClient
        │
        ├─► HTTP GET 请求
        │    │
        │    └─► https://api.cnb.cool/astral-sh/uv/-/releases/latest
        │
        ├─► 接收 JSON 响应
        │    │
        │    └─► {
        │         "id": "123",
        │         "tag_name": "0.9.18",
        │         "assets": [...],
        │         ...
        │        }
        │
        └─► serde 反序列化
             │
             └─► CnbRelease 结构体
                  │
                  ├─► tag_name
                  ├─► assets []
                  ├─► author
                  └─► 其他字段...
```

### 代码示例

```rust
// 创建客户端
let client = CnbClient::new(None);

// 调用 API
let release = client.fetch_latest_release("astral-sh/uv").await?;

// 获取强类型数据
println!("版本: {}", release.tag_name.unwrap());
println!("资源数: {}", release.assets.len());

// 列出所有资源
for asset in release.assets {
    println!("- {} ({}字节)", 
        asset.name, 
        asset.size.unwrap_or(0)
    );
}
```

### 支持的操作

| 方法 | 功能 | 参数 |
|------|------|------|
| `fetch_latest_release()` | 获取最新版本 | repo 名称 |
| `fetch_release_by_tag()` | 按标签获取 | repo, tag |
| `fetch_release_by_id()` | 按 ID 获取 | repo, id |
| `list_releases()` | 分页列表 | repo, page, page_size |
| `download_asset()` | 下载资源 | repo, tag, filename |
| `get_asset_download_url()` | 获取下载链接 | repo, tag, filename |

### API 端点

```bash
# 获取最新版本
GET /astral-sh/uv/-/releases/latest

# 按标签获取特定版本
GET /astral-sh/uv/-/releases/tags/0.9.18

# 按 ID 获取
GET /astral-sh/uv/-/releases/{release_id}

# 分页列出所有版本
GET /astral-sh/uv/-/releases?page=1&page_size=10

# 下载资源文件
GET /astral-sh/uv/-/releases/download/0.9.18/uv-x86_64-unknown-linux-gnu.tar.gz
```

### JSON 响应示例

```json
{
  "id": "release_12345",
  "tag_name": "0.9.18",
  "name": "uv 0.9.18",
  "body": "## 更新内容\n- 新增功能\n- 修复 bug",
  "draft": false,
  "is_latest": true,
  "prerelease": false,
  "author": {
    "username": "astral-sh",
    "name": "Astral Software",
    "avatar_url": "https://..."
  },
  "assets": [
    {
      "id": "asset_001",
      "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
      "size": 22200000,
      "download_url": "/astral-sh/uv/-/releases/download/0.9.18/uv-x86_64-unknown-linux-gnu.tar.gz",
      "browser_download_url": "https://cnb.cool/astral-sh/uv/-/releases/download/0.9.18/uv-x86_64-unknown-linux-gnu.tar.gz",
      "content_type": "application/gzip",
      "created_at": "2024-01-10T12:34:56Z"
    },
    {
      "id": "asset_002",
      "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
      "size": 21500000,
      "download_url": "/astral-sh/uv/-/releases/download/0.9.18/uv-aarch64-unknown-linux-gnu.tar.gz",
      "browser_download_url": "https://cnb.cool/astral-sh/uv/-/releases/download/0.9.18/uv-aarch64-unknown-linux-gnu.tar.gz",
      "content_type": "application/gzip",
      "created_at": "2024-01-10T12:34:56Z"
    }
  ],
  "created_at": "2024-01-10T12:34:56Z",
  "published_at": "2024-01-10T12:34:56Z"
}
```

### 优势

✅ **类型安全**
```rust
// 编译时检查
let tag: Option<String> = release.tag_name; // ✅ Some("0.9.18")
let assets: Vec<CnbAsset> = release.assets;  // ✅ 类型确定
```

✅ **错误处理**
```rust
// 自动重试，指数退避
// 处理超时、速率限制等
let result = client.fetch_latest_release("repo").await?;
match result {
    Ok(release) => { /* ... */ },
    Err(CnbError::RateLimited) => { /* 429 */ },
    Err(CnbError::Timeout) => { /* 超时 */ },
    Err(e) => { /* 其他错误 */ },
}
```

✅ **性能**
```rust
// 异步、非阻塞
let future = client.fetch_latest_release("repo"); // 立即返回
let release = future.await?;  // 真正执行
```

---

## Shell 脚本：HTML 解析（简化）

### 实现位置
- **文件**: `install-cnb-uv.sh` (11.1 KB)
- **方式**: HTML 文本解析

### 数据流

```
curl 获取 HTML 页面
   │
   ├─► GET https://cnb.cool/astral-sh/uv/-/releases
   │
   ├─► 接收 HTML/JavaScript
   │    │
   │    └─► <html>
   │         <script>
   │          window.__INITIAL_STATE__ = {
   │           releases: [{
   │            tag_name: "0.9.18",
   │            ...
   │           }]
   │          }
   │         </script>
   │        </html>
   │
   ├─► grep 提取版本号
   │    │
   │    └─► "tagRef":"refs/tags/0.9.18"
   │
   ├─► sed 清理数据
   │    │
   │    └─► 0.9.18
   │
   └─► 构造下载 URL
        │
        └─► https://cnb.cool/astral-sh/uv/-/releases/download/0.9.18/...
```

### 代码示例

```bash
# 获取最新版本号
release_tag=$(curl -s "https://cnb.cool/astral-sh/uv/-/releases" | \
    grep -o '"tagRef":"refs/tags/[^"]*"' | \
    head -1 | \
    cut -d'"' -f4 | \
    sed 's|refs/tags/||')

echo "Latest version: $release_tag"  # 0.9.18

# 构造下载 URL
download_url="https://cnb.cool/astral-sh/uv/-/releases/download/${release_tag}/uv-${pattern}.tar.gz"

# 下载文件
curl -L "$download_url" -o /tmp/uv.tar.gz
```

### 步骤分解

```bash
# 步骤 1: 获取 HTML 页面（包含嵌入的 JSON）
curl -s "https://cnb.cool/astral-sh/uv/-/releases"
# 返回大量 HTML + JavaScript

# 步骤 2: 用 grep 找到版本标签行
grep -o '"tagRef":"refs/tags/[^"]*"'
# 返回: "tagRef":"refs/tags/0.9.18"

# 步骤 3: 提取标签值
head -1 | cut -d'"' -f4
# 返回: refs/tags/0.9.18

# 步骤 4: 移除前缀
sed 's|refs/tags/||'
# 返回: 0.9.18
```

### 支持的操作

| 操作 | 脚本部分 | 说明 |
|------|---------|------|
| 网络检查 | Lines 93-127 | 3层后备检查 |
| 版本检测 | Lines 129-141 | 从 HTML 提取 |
| URL 构造 | Lines 143-153 | 动态生成 |
| 文件下载 | 后续代码 | curl 下载 |
| 档案提取 | 后续代码 | tar 解压 |

### 优势

✅ **轻量级**
- 11KB，无外部库
- 只需 curl, grep, sed, tar

✅ **快速安装**
```bash
sh install-cnb-uv.sh
# 直接安装，无依赖
```

✅ **跨平台兼容**
```bash
# POSIX shell 兼容
# 支持 Linux, macOS, 容器等
```

---

## 对比总结

### 选择方案时

```
需要在 Rust 项目中集成？
  ↓
  是 → 使用 Rust 库 (cnb.rs)
       ✅ JSON API
       ✅ 类型安全
       ✅ 完整功能
  
  否 → 快速安装工具？
       ↓
       是 → 使用 Shell 脚本
            ✅ 无依赖
            ✅ 轻量级
            ✅ 即开即用
```

### 功能对比矩阵

```
                    Rust 库    Shell 脚本
获取最新版本         ✅          ✅
获取指定版本         ✅          ⚠️
列表分页             ✅          ❌
下载资源             ✅          ✅
获取作者信息         ✅          ❌
错误处理             ✅          ⚠️
自动重试             ✅          ❌
进度显示             ⚠️          ✅
直接安装             ❌          ✅
```

---

## 关键区别

### 1. 数据源

**Rust 库**：
```
官方 JSON API
├─ 结构化数据
├─ 完整信息
└─ 版本化接口
```

**Shell 脚本**：
```
HTML 页面 (包含嵌入 JSON)
├─ 文本处理
├─ 基本信息
└─ 简化提取
```

### 2. 解析方式

**Rust 库**：
```rust
// serde 自动解析 JSON
#[derive(Deserialize)]
struct CnbRelease {
    tag_name: Option<String>,
    assets: Vec<CnbAsset>,
    // ...
}

let release: CnbRelease = response.json().await?;
```

**Shell 脚本**：
```bash
# 正则表达式和文本处理
grep -o '"tagRef":"refs/tags/[^"]*"' | \
sed 's|refs/tags/||'
```

### 3. 可靠性

**Rust 库**：
- ✅ 自动重试
- ✅ 错误类型
- ✅ 超时处理
- ✅ 速率限制感知

**Shell 脚本**：
- ⚠️ 基本错误检查
- ⚠️ 简单的网络检查
- ✅ 降级优雅

---

## 实际使用示例

### 使用 Rust 库

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1. 创建客户端
    let client = CnbClient::new(None);
    
    // 2. 获取最新版本
    let release = client.fetch_latest_release("astral-sh/uv").await?;
    
    // 3. 遍历资源
    for asset in &release.assets {
        if asset.name.contains("x86_64") && asset.name.contains("linux") {
            println!("Linux 版本: {}", asset.name);
            println!("下载链接: {}", asset.browser_download_url.as_ref().unwrap());
            break;
        }
    }
    
    Ok(())
}
```

### 使用 Shell 脚本

```bash
#!/bin/bash
# 直接运行安装
sh install-cnb-uv.sh

# 或设置参数
CNB_INSTALL_DIR="$HOME/mytools" \
CNB_VERBOSE=1 \
sh install-cnb-uv.sh
```

---

## 总结

| 特性 | JSON API | HTML 解析 |
|------|----------|----------|
| **维护责任** | 官方承诺 | 用户承担 |
| **数据质量** | 高 | 中 |
| **易用性** | 高（库） | 高（脚本） |
| **功能完整性** | 100% | 70% |
| **性能** | 高 | 中 |
| **生产就绪** | ✅ | ✅* |

\* 受限于 HTML 解析的稳定性

---

**建议**：
- 📦 **库集成** → 使用 JSON API (cnb.rs)
- 🚀 **快速安装** → 使用 Shell 脚本

两者都经过测试，都可以在生产环境使用！
