# 🚀 立即行动清单

**状态**: ✅ 可开始开发  
**日期**: 2026-01-11  
**优先级**: 按顺序执行

---

## 📋 P0 - 本周必做（开发前提）

### ✅ 任务 1: 正式化 DEVELOPMENT_PLAN
**预计时间**: 1-2 小时  
**关键步骤**:

```
[ ] 在 DEVELOPMENT_PLAN.md 中正式添加以下章节：

## API 配置确认

### 基础信息
- API 基础 URL: https://api.cnb.cool/
- 认证: Bearer Token (不支持 anonymous)
- Token: db5HVM2xIiR0Zo11dcsuL4WeHGE (guest 权限，只读)
- Rate Limit: 无限制
- 超时策略: 重试 3 次，每次 30 秒

### 核心端点（来自 cnb_doc.json）

1. **获取最新版本**
   GET /repos/{owner}/{repo}/releases/latest

2. **按 Tag 获取版本**
   GET /repos/{owner}/{repo}/releases/tags/{tag}

3. **按 ID 获取版本**
   GET /repos/{owner}/{repo}/releases/{id}

4. **获取资源详情**
   GET /repos/{owner}/{repo}/releases/assets/{asset_id}

### Receipt 格式

当 release_type = "cnb" 时：
{
  "binaries": [...],
  "source": {
    "app_name": "uv",
    "owner": "astral-sh",
    "release_type": "cnb"
    // TODO: 需确认是否需要 api_base 字段
  },
  "version": "0.9.18"
}
```

---

### ✅ 任务 2: 验证 API 响应格式
**预计时间**: 30 分钟  
**关键步骤**:

```bash
[ ] 运行以下命令验证 API 可用性：

# 设置环境
export CNB_TOKEN=db5HVM2xIiR0Zo11dcsuL4WeHGE

# 测试 1: 获取最新版本
curl -i -H "Authorization: Bearer $CNB_TOKEN" \
  https://api.cnb.cool/repos/astral-sh/uv/releases/latest

# 测试 2: 将响应格式记录到文档
python scripts/verify_cnb_api.py

[ ] 检查输出文件: docs/API_VERIFICATION.md
```

**期望结果**:
- ✅ HTTP 200 OK
- ✅ JSON 响应包含 tag_name, assets 等字段
- ✅ 文档已生成

---

### ✅ 任务 3: 确认 Receipt CNB 字段
**预计时间**: 30 分钟  
**关键问题**:

```
需要确认并记录到 docs/RECEIPT_SPECIFICATION.md：

1. Receipt 中 source 字段修改为：
   "release_type": "cnb"
   
2. 是否需要添加 "api_base" 字段？
   - 如果支持自定义 API URL（企业部署）：需要
   - 如果只支持默认 https://api.cnb.cool：不需要
   
3. Token 的存储方式：
   - 方案 A: 不存储，运行时从环境变量读取 ✅ 推荐
   - 方案 B: 加密存储在 receipt 中
   
4. 是否需要存储其他信息？
   - 组织 ID？
   - 仓库 ID？
```

---

## 📋 P1 - 本周内完成（开发配置）

### ✅ 任务 4: 提取 API 端点清单
**预计时间**: 1 小时  
**输出**:

创建文件 `docs/CNB_API_ENDPOINTS.md`，包含：

```markdown
# CNB API 端点完整清单

从 cnb_doc.json 的 Releases 分类中，提取以下 12 个 API：

## 获取版本信息（必需）

1. GetLatestRelease: GET /repos/{owner}/{repo}/releases/latest
2. GetReleaseByID: GET /repos/{owner}/{repo}/releases/{id}  
3. GetReleaseByTag: GET /repos/{owner}/{repo}/releases/tags/{tag}
4. ListReleases: GET /repos/{owner}/{repo}/releases

## 获取资源信息（必需）

5. GetReleaseAsset: GET /repos/{owner}/{repo}/releases/assets/{asset_id}
6. ListReleaseAssets: GET /repos/{owner}/{repo}/releases/{id}/assets

## 管理版本（可选，当前不需要）

7. CreateRelease: POST /repos/{owner}/{repo}/releases
8. UpdateRelease: PATCH /repos/{owner}/{repo}/releases/{id}
9. DeleteRelease: DELETE /repos/{owner}/{repo}/releases/{id}
...

## 必需端点的请求/响应格式

### 1. GetLatestRelease

请求:
  GET https://api.cnb.cool/repos/astral-sh/uv/releases/latest
  Authorization: Bearer {token}

响应 (JSON):
  {
    "id": 12345,
    "tag_name": "0.9.18",
    "name": "uv v0.9.18",
    "body": "Release notes...",
    "prerelease": false,
    "created_at": "2026-01-10T...",
    "assets": [
      {
        "id": 67890,
        "name": "uv-0.9.18-x86_64-unknown-linux-gnu.tar.gz",
        "browser_download_url": "https://...storage.cnb.cool.../..."
      }
    ]
  }
```

---

### ✅ 任务 5: 编写测试命令脚本
**预计时间**: 1 小时  
**创建**:

文件 `scripts/test_cnb.sh`:

```bash
#!/bin/bash

# CNB 集成测试脚本

set -e

echo "=== CNB 集成测试开始 ==="

# 加载环境变量
if [ ! -f .env ]; then
    echo "❌ .env 文件不存在"
    exit 1
fi
source .env

echo "✅ 环境变量已加载"

# 单元测试
echo ""
echo "--- 单元测试 ---"
cargo test cnb --lib --all-features -- --nocapture
echo "✅ 单元测试通过"

# 集成测试
echo ""
echo "--- 集成测试 ---"
cargo test --test '*cnb*' --all-features -- --nocapture
echo "✅ 集成测试通过"

# 性能测试（可选）
echo ""
echo "--- 性能测试 ---"
echo "API 响应时间（100次调用平均）:"
# TODO: 性能测试脚本

echo ""
echo "=== 所有测试通过 ==="
```

---

### ✅ 任务 6: 编写成功标准文档
**预计时间**: 1 小时  
**创建**:

文件 `docs/ACCEPTANCE_CRITERIA.md`:

```markdown
# CNB 集成验收标准

## 功能验收

### 版本检测 ✅
- [ ] 能正确调用 GetLatestRelease 接口
- [ ] 能解析 JSON 响应并获取版本号
- [ ] 能正确比对版本号 (0.9.18 > 0.9.17)
- [ ] 支持预发布版本 (alpha, beta, rc)

### 资源获取 ✅
- [ ] 能获取资源下载 URL
- [ ] 能识别多平台资源
- [ ] 能选择当前平台的正确资源

### 升级执行 ✅
- [ ] 能下载资源
- [ ] 能验证完整性 (checksum)
- [ ] 能替换二进制文件
- [ ] 新版本可立即运行
- [ ] 失败时自动回滚

### 错误处理 ✅
- [ ] 401 Unauthorized: token 无效 → 提示用户设置 TOKEN
- [ ] 404 Not Found: 版本不存在 → 正确提示
- [ ] 429 Rate Limited: 限流 → 自动重试
- [ ] Timeout: 超时 → 重试 3 次

## 性能标准

| 指标 | 目标值 | 测试方法 |
|------|--------|--------|
| API 响应 | < 2s | `time curl ...` |
| 版本检测成功率 | 100% | 运行 100 次 |
| 升级成功率 | 100% | 运行 10 次完整升级 |
| 内存占用 | < 50MB | top/htop 监控 |

## 安全标准

- [ ] Token 不以明文存储 receipt 中
- [ ] Token 只通过环境变量读取
- [ ] 所有 API 调用使用 HTTPS
- [ ] 支持资源签名验证

## 测试覆盖率

- [ ] 单元测试覆盖率 > 80%
- [ ] cnb.rs 模块覆盖率 > 90%
- [ ] 关键路径 100% 覆盖
```

---

## 📋 P2 - 开发过程中参考

### 🔧 任务 7: Python 验证脚本
**位置**: `scripts/verify_cnb_api.py`

```python
#!/usr/bin/env python3
import os
import json
import requests

TOKEN = os.getenv("CNB_TOKEN", "db5HVM2xIiR0Zo11dcsuL4WeHGE")
BASE_URL = "https://api.cnb.cool"

def test_api():
    url = f"{BASE_URL}/repos/astral-sh/uv/releases/latest"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        
        with open("docs/API_VERIFICATION.md", "w") as f:
            f.write("# API 验证结果\n\n")
            f.write(f"状态码: {r.status_code}\n\n")
            f.write("```json\n")
            f.write(json.dumps(r.json(), indent=2))
            f.write("\n```")
        
        print(f"✅ API 验证成功 (status={r.status_code})")
        print(f"✅ 结果已保存到: docs/API_VERIFICATION.md")
    except Exception as e:
        print(f"❌ API 验证失败: {e}")
        exit(1)

if __name__ == "__main__":
    test_api()
```

---

## ✨ 快速开始

### 立即执行（10 分钟）：

```bash
# 1. 验证 API
export CNB_TOKEN=db5HVM2xIiR0Zo11dcsuL4WeHGE
curl -H "Authorization: Bearer $CNB_TOKEN" \
  https://api.cnb.cool/repos/astral-sh/uv/releases/latest | jq .

# 2. 检查现有的 .env.example
cat .env.example

# 3. 查看已创建的文档
ls -la docs/ | grep -i cnb
```

---

## 📊 进度追踪

```
P0 任务：
[ ] 正式化 DEVELOPMENT_PLAN ────────── 预计完成: 今天
[ ] 验证 API 响应格式 ────────────── 预计完成: 今天  
[ ] 确认 Receipt CNB 字段 ────────── 预计完成: 今天

P1 任务：
[ ] 提取 API 端点清单 ────────────── 预计完成: 明天
[ ] 编写测试命令脚本 ────────────── 预计完成: 明天
[ ] 编写成功标准文档 ────────────── 预计完成: 明天

✅ 准备完成，可启动第二阶段开发
```

---

## 🎯 下一步

**完成上述所有 P0 项目后：**
→ 开始第二阶段：核心开发（cnb.rs 实现）

**预计时间表：**
- P0 项目: 3 小时（今天完成）
- P1 项目: 3 小时（明天完成）  
- 第二阶段: 5-7 天（下周开始）

---

**更新时间**: 2026-01-11  
**维护**: @chinario
