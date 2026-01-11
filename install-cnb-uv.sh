#!/bin/sh
# CNB 平台 uv 安装脚本
# 参照 astral.sh/uv/install.sh 设计
# 功能：从 CNB.cool 平台下载并安装 uv
# 
# 使用:
#   curl -fsSL https://your-server/install-cnb-uv.sh | sh
#
# 环境变量:
#   CNB_BASE_URL        - CNB 平台的基础 URL (默认: https://cnb.cool)
#   CNB_REPO            - CNB 上的仓库名 (默认: astral-sh/uv)
#   CNB_VERBOSE         - 详细输出 (设为 1 启用)
#   CNB_INSTALL_DIR     - 安装目录 (默认: $HOME/.local/bin)
#   CNB_NO_MODIFY_PATH  - 不修改 PATH (设为 1 禁用)

set -u

# ============================================================================
# 配置
# ============================================================================

APP_NAME="uv"
CNB_BASE_URL="${CNB_BASE_URL:-https://cnb.cool}"
CNB_REPO="${CNB_REPO:-astral-sh/uv}"
VERBOSE="${CNB_VERBOSE:-0}"
NO_MODIFY_PATH="${CNB_NO_MODIFY_PATH:-0}"

# ============================================================================
# 工具函数
# ============================================================================

# 打印信息
info() {
    if [ "$VERBOSE" = "1" ]; then
        echo "ℹ️  $*" >&2
    fi
}

# 打印成功
success() {
    echo "✅ $*" >&2
}

# 打印警告
warn() {
    echo "⚠️  $*" >&2
}

# 打印错误并退出
error() {
    echo "❌ 错误: $*" >&2
    exit 1
}

# 获取系统架构
get_arch() {
    local arch
    arch=$(uname -m)
    case "$arch" in
        x86_64) echo "x86_64" ;;
        aarch64) echo "aarch64" ;;
        arm64) echo "aarch64" ;;  # macOS
        *) error "不支持的架构: $arch" ;;
    esac
}

# 获取操作系统
get_os() {
    local os
    os=$(uname -s)
    case "$os" in
        Linux) echo "linux" ;;
        Darwin) echo "macos" ;;
        *) error "不支持的操作系统: $os" ;;
    esac
}

# 获取 HOME 目录
get_home() {
    if [ -n "${HOME:-}" ]; then
        echo "$HOME"
    elif [ -n "${USER:-}" ]; then
        getent passwd "$USER" | cut -d: -f6
    else
        getent passwd "$(id -un)" | cut -d: -f6
    fi
}

# ============================================================================
# 网络函数
# ============================================================================

# 检查网络连接
check_network() {
    info "检查网络连接..."
    
    # 方法 1: 尝试 ping（如果可用）
    if command -v ping >/dev/null 2>&1; then
        if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
            info "网络检查通过 (ping)"
            return 0
        fi
    fi
    
    # 方法 2: 尝试连接到 CNB 平台（最可靠）
    if command -v curl >/dev/null 2>&1; then
        if curl -s -m 5 -o /dev/null -w "%{http_code}" "$CNB_BASE_URL" 2>/dev/null | grep -q "^[23]"; then
            info "网络检查通过 (CNB 平台可访问)"
            return 0
        fi
    fi
    
    # 方法 3: 尝试 wget
    if command -v wget >/dev/null 2>&1; then
        if wget -q -T 5 -O /dev/null "$CNB_BASE_URL" 2>/dev/null; then
            info "网络检查通过 (wget)"
            return 0
        fi
    fi
    
    # 如果前面的方法都失败了，发出警告但继续（可能是防火墙或网络问题）
    warn "网络检查失败，但将尝试继续安装..."
    return 0
}

# 获取最新发布版本号
get_latest_release_tag() {
    # 从 CNB 发布页面提取最新的版本标签
    curl -s "${CNB_BASE_URL}/${CNB_REPO}/-/releases" 2>/dev/null | \
        grep -o '"tagRef":"refs/tags/[^"]*"' | head -1 | \
        cut -d'"' -f4 | sed 's|refs/tags/||'
}

# 获取下载 URL
get_download_url() {
    local os="$1"
    local arch="$2"
    
    # 根据操作系统和架构构建文件名模式
    local pattern
    case "$os-$arch" in
        linux-x86_64) pattern="x86_64-unknown-linux-gnu" ;;
        linux-aarch64) pattern="aarch64-unknown-linux-gnu" ;;
        macos-x86_64) pattern="x86_64-apple-darwin" ;;
        macos-aarch64) pattern="aarch64-apple-darwin" ;;
        *) error "不支持的操作系统或架构: $os-$arch" ;;
    esac
    
    info "寻找 $os-$arch 的下载 URL..."
    
    # 获取最新发布版本
    local release_tag
    release_tag=$(get_latest_release_tag)
    
    if [ -z "$release_tag" ]; then
        error "无法获取发布版本号"
    fi
    
    info "最新版本: $release_tag"
    
    # 构建下载 URL
    echo "${CNB_BASE_URL}/${CNB_REPO}/-/releases/download/${release_tag}/uv-${pattern}.tar.gz"
}

# ============================================================================
# 安装函数
# ============================================================================

# 下载文件
download_file() {
    local url="$1"
    local dest="$2"
    
    info "下载 $url"
    
    if command -v curl >/dev/null 2>&1; then
        if ! curl -fL "$url" -o "$dest"; then
            error "下载失败: $url"
        fi
    elif command -v wget >/dev/null 2>&1; then
        if ! wget -q "$url" -O "$dest"; then
            error "下载失败: $url"
        fi
    else
        error "需要 curl 或 wget 命令"
    fi
    
    success "下载完成: $dest"
}

# 验证文件
verify_file() {
    local file="$1"
    local expected_sha256="$2"
    
    if [ -z "$expected_sha256" ]; then
        warn "未提供 SHA256 校验和，跳过验证"
        return 0
    fi
    
    info "验证文件: $file"
    
    if command -v sha256sum >/dev/null 2>&1; then
        local actual_sha256
        actual_sha256=$(sha256sum "$file" | cut -d' ' -f1)
        
        if [ "$actual_sha256" = "$expected_sha256" ]; then
            success "文件验证通过"
            return 0
        else
            error "文件验证失败: 期望 $expected_sha256, 实际 $actual_sha256"
        fi
    else
        warn "sha256sum 不可用，跳过验证"
        return 0
    fi
}

# 提取存档
extract_archive() {
    local archive="$1"
    local dest_dir="$2"
    
    info "提取存档: $archive"
    
    mkdir -p "$dest_dir"
    
    if command -v tar >/dev/null 2>&1; then
        if ! tar -xzf "$archive" -C "$dest_dir"; then
            error "提取失败: $archive"
        fi
    else
        error "需要 tar 命令"
    fi
    
    success "提取完成"
}

# 安装二进制文件
install_binary() {
    local source="$1"
    local install_dir="$2"
    local binary_name="$3"
    
    mkdir -p "$install_dir"
    
    info "安装二进制: $binary_name"
    
    # 复制文件
    cp "$source" "$install_dir/$binary_name" || error "复制文件失败"
    
    # 设置执行权限
    chmod +x "$install_dir/$binary_name" || error "设置权限失败"
    
    success "安装成功: $install_dir/$binary_name"
}

# 修改 PATH
modify_path() {
    local install_dir="$1"
    local home_dir="$2"
    
    if [ "$NO_MODIFY_PATH" = "1" ]; then
        info "跳过 PATH 修改（CNB_NO_MODIFY_PATH=1）"
        return 0
    fi
    
    info "配置 PATH..."
    
    local shell_rc=""
    if [ -f "$home_dir/.bashrc" ]; then
        shell_rc="$home_dir/.bashrc"
    elif [ -f "$home_dir/.zshrc" ]; then
        shell_rc="$home_dir/.zshrc"
    else
        warn "找不到 shell 配置文件"
        return 0
    fi
    
    # 检查是否已经添加
    if ! grep -q "$install_dir" "$shell_rc" 2>/dev/null; then
        echo "" >> "$shell_rc"
        echo "# CNB 平台 uv 安装" >> "$shell_rc"
        echo "export PATH=\"$install_dir:\$PATH\"" >> "$shell_rc"
        success "已更新 PATH: $shell_rc"
    else
        info "PATH 已包含 $install_dir"
    fi
}

# ============================================================================
# 主安装流程
# ============================================================================

main() {
    local temp_dir
    local home_dir
    local install_dir
    local os
    local arch
    local download_url
    local archive_path
    local binary_path
    
    echo "=========================================="
    echo "CNB 平台 uv 安装程序"
    echo "=========================================="
    echo ""
    
    # 初始化
    temp_dir=$(mktemp -d)
    home_dir=$(get_home)
    install_dir="${CNB_INSTALL_DIR:-$home_dir/.local/bin}"
    os=$(get_os)
    arch=$(get_arch)
    
    info "操作系统: $os"
    info "架构: $arch"
    info "主目录: $home_dir"
    info "安装目录: $install_dir"
    info "CNB 仓库: $CNB_REPO"
    info "CNB 基础 URL: $CNB_BASE_URL"
    
    # 清理
    trap "rm -rf $temp_dir" EXIT
    
    # 步骤 1: 检查网络
    info ""
    echo "【步骤 1】检查网络..."
    check_network
    
    # 步骤 2: 获取下载 URL
    echo "【步骤 2】从 CNB 获取下载信息..."
    download_url=$(get_download_url "$os" "$arch" "$CNB_REPO")
    
    if [ -z "$download_url" ]; then
        error "无法获取下载 URL"
    fi
    
    success "找到下载 URL: $download_url"
    
    # 步骤 3: 下载文件
    echo "【步骤 3】下载文件..."
    archive_path="$temp_dir/uv.tar.gz"
    download_file "$download_url" "$archive_path"
    
    # 步骤 4: 提取文件
    echo "【步骤 4】提取文件..."
    extract_archive "$archive_path" "$temp_dir"
    
    # 步骤 5: 查找二进制文件
    echo "【步骤 5】定位二进制文件..."
    if [ -f "$temp_dir/uv" ]; then
        binary_path="$temp_dir/uv"
    else
        # 可能在子目录中
        binary_path=$(find "$temp_dir" -name "uv" -type f -executable 2>/dev/null | head -1)
    fi
    
    if [ -z "$binary_path" ]; then
        error "找不到 uv 二进制文件"
    fi
    
    success "找到二进制: $binary_path"
    
    # 步骤 6: 安装
    echo "【步骤 6】安装..."
    install_binary "$binary_path" "$install_dir" "uv"
    
    # 步骤 7: 安装 uvx (如果存在)
    if [ -f "$temp_dir/uvx" ] || find "$temp_dir" -name "uvx" -type f -executable 2>/dev/null | grep -q .; then
        uvx_path=$(find "$temp_dir" -name "uvx" -type f -executable 2>/dev/null | head -1)
        if [ -n "$uvx_path" ]; then
            install_binary "$uvx_path" "$install_dir" "uvx"
        fi
    fi
    
    # 步骤 8: 修改 PATH
    echo "【步骤 8】配置环境..."
    modify_path "$install_dir" "$home_dir"
    
    # 验证
    echo "【步骤 9】验证安装..."
    if command -v uv >/dev/null 2>&1; then
        local version
        version=$(uv --version 2>/dev/null || echo "unknown")
        success "uv 已安装: $version"
    else
        # 尝试直接运行
        if "$install_dir/uv" --version >/dev/null 2>&1; then
            success "uv 已安装在 $install_dir/uv"
            echo ""
            echo "请运行以下命令添加到 PATH:"
            echo "  export PATH=\"$install_dir:\$PATH\""
        else
            warn "无法验证 uv 安装"
        fi
    fi
    
    # 完成
    echo ""
    echo "=========================================="
    success "安装完成！"
    echo "=========================================="
    echo ""
    echo "使用方法:"
    echo "  uv --help        # 显示帮助信息"
    echo "  uv --version     # 显示版本信息"
    echo ""
}

# 运行主程序
main "$@"
