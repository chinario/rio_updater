#!/bin/sh
log_success() { printf "✅ %s\n" "$1"; }
log_info() { printf "ℹ️  %s\n" "$1"; }
log_error() { printf "❌ %s\n" "$1"; }

echo
echo "===== CNB 平台 uv 安装脚本演示 ====="
echo

log_info "运行快速健康检查..."
echo

script="/workspaces/rio_updater/install-cnb-uv.sh"
if [ -f "$script" ] && [ -x "$script" ] && sh -n "$script" 2>/dev/null; then
    log_success "安装脚本: 健康✓"
else
    log_error "安装脚本: 问题✗"
    exit 1
fi

test_script="/workspaces/rio_updater/test_cnb_platform.py"
if [ -f "$test_script" ] && python3 -m py_compile "$test_script" 2>/dev/null; then
    log_success "测试脚本: 健康✓"
else
    log_error "测试脚本: 问题✗"
    exit 1
fi

if curl -s -o /dev/null -w "%{http_code}" "https://cnb.cool" 2>/dev/null | grep -q "^200"; then
    log_success "CNB 平台: 在线✓"
else
    log_error "CNB 平台: 离线✗"
    exit 1
fi

missing=0
for cmd in curl wget tar; do
    if command -v "$cmd" > /dev/null 2>&1; then
        log_success "工具 $cmd: 可用✓"
    else
        log_error "工具 $cmd: 缺失✗"
        missing=$((missing + 1))
    fi
done

echo
if [ $missing -eq 0 ]; then
    log_success "✨ 所有检查通过！CNB 平台 uv 安装脚本已准备就绪"
    exit 0
else
    log_error "❌ 缺失 $missing 个工具"
    exit 1
fi
