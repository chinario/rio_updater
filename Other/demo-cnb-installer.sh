#!/bin/sh
# demo-cnb-installer.sh
# CNB 平台 uv 安装脚本演示
# 展示脚本的各种用法和功能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_header() {
    printf "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    printf "${BLUE}%s${NC}\n" "$1"
    printf "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

log_info() {
    printf "${BLUE}ℹ️  %s${NC}\n" "$1"
}

log_success() {
    printf "${GREEN}✅ %s${NC}\n" "$1"
}

log_warning() {
    printf "${YELLOW}⚠️  %s${NC}\n" "$1"
}

log_error() {
    printf "${RED}❌ %s${NC}\n" "$1"
}

# Demo 1: 验证环境
demo_environment() {
    log_header "演示 1: 验证安装环境"
    
    log_info "检查必需工具..."
    
    if command -v sh > /dev/null 2>&1; then
        log_success "sh 已安装"
    else
        log_error "sh 未安装"
        return 1
    fi
    
    if command -v curl > /dev/null 2>&1; then
        log_success "curl 已安装"
    else
        log_warning "curl 未安装"
    fi
    
    if command -v wget > /dev/null 2>&1; then
        log_success "wget 已安装"
    else
        log_warning "wget 未安装"
    fi
    
    if command -v tar > /dev/null 2>&1; then
        log_success "tar 已安装"
    else
        log_error "tar 未安装"
        return 1
    fi
    
    if command -v python3 > /dev/null 2>&1; then
        log_success "python3 已安装"
    else
        log_warning "python3 未安装"
    fi
}

# Demo 2: 验证安装脚本
demo_script_validation() {
    log_header "演示 2: 验证安装脚本"
    
    script="/workspaces/rio_updater/install-cnb-uv.sh"
    
    if [ ! -f "$script" ]; then
        log_error "脚本不存在: $script"
        return 1
    fi
    
    log_info "检查脚本: $script"
    
    if sh -n "$script" 2>/dev/null; then
        log_success "Shell 语法检查通过"
    else
        log_error "Shell 语法检查失败"
        return 1
    fi
    
    if [ -x "$script" ]; then
        log_success "脚本有执行权限"
    else
        log_warning "脚本没有执行权限"
    fi
    
    log_info "检查脚本函数..."
    
    for func in get_arch get_os check_network get_cnb_release_info download_file extract_archive install_binary modify_path main; do
        if grep -q "^${func}()" "$script"; then
            log_success "函数存在: $func"
        else
            log_warning "函数未找到: $func"
        fi
    done
}

# Demo 3: 验证 CNB 平台
demo_cnb_platform() {
    log_header "演示 3: 验证 CNB 平台"
    
    log_info "测试 CNB 平台连接..."
    
    if curl -s -o /dev/null -w "%{http_code}" "https://cnb.cool" 2>/dev/null | grep -q "^200"; then
        log_success "CNB 平台连接成功 (HTTP 200)"
    else
        log_error "CNB 平台连接失败"
        return 1
    fi
    
    log_info "测试仓库页面..."
    if curl -s -o /dev/null -w "%{http_code}" "https://cnb.cool/astral-sh/uv" 2>/dev/null | grep -q "^200"; then
        log_success "仓库页面可访问"
    else
        log_error "仓库页面不可访问"
        return 1
    fi
    
    log_info "测试 API 端点..."
    if curl -s "https://cnb.cool/astral-sh/uv/-/releases/latest" 2>/dev/null | grep -q "version"; then
        log_success "API 端点正常工作"
    else
        log_warning "API 端点可能需要认证"
    fi
}

# Demo 4: 运行测试套件
demo_test_suite() {
    log_header "演示 4: 运行测试套件"
    
    test_script="/workspaces/rio_updater/test_cnb_platform.py"
    
    if [ ! -f "$test_script" ]; then
        log_error "测试脚本不存在: $test_script"
        return 1
    fi
    
    log_info "运行 CNB 平台集成测试..."
    echo
    
    python3 "$test_script" 2>/dev/null | tail -15
}

# Demo 5: 查看安装选项
demo_install_options() {
    log_header "演示 5: 安装选项演示"
    
    log_info "支持的环境变量:"
    echo
    
    cat << 'EOF'
1. CNB_BASE_URL (默认: https://cnb.cool)
   用途: 指定 CNB 平台的基础 URL
   示例: CNB_BASE_URL=https://internal-cnb.com sh install-cnb-uv.sh

2. CNB_REPO (默认: astral-sh/uv)
   用途: 指定要安装的仓库
   示例: CNB_REPO=myorg/myapp sh install-cnb-uv.sh

3. CNB_VERBOSE (默认: 0)
   用途: 启用详细输出
   示例: CNB_VERBOSE=1 sh install-cnb-uv.sh

4. CNB_INSTALL_DIR (默认: $HOME/.local/bin)
   用途: 指定安装目录
   示例: CNB_INSTALL_DIR=/opt/tools sh install-cnb-uv.sh

5. CNB_NO_MODIFY_PATH (默认: 0)
   用途: 禁用 PATH 修改
   示例: CNB_NO_MODIFY_PATH=1 sh install-cnb-uv.sh
EOF
}

# Demo 6: 文件清单
demo_file_inventory() {
    log_header "演示 6: 项目文件清单"
    
    log_info "关键文件列表:"
    echo
    
    base_dir="/workspaces/rio_updater"
    
    if [ -f "$base_dir/install-cnb-uv.sh" ]; then
        lines=$(wc -l < "$base_dir/install-cnb-uv.sh")
        log_success "install-cnb-uv.sh ($lines 行)"
    fi
    
    if [ -f "$base_dir/test_cnb_platform.py" ]; then
        lines=$(wc -l < "$base_dir/test_cnb_platform.py")
        log_success "test_cnb_platform.py ($lines 行)"
    fi
    
    if [ -f "$base_dir/CNB_INSTALLER_GUIDE.md" ]; then
        log_success "CNB_INSTALLER_GUIDE.md (详细使用指南)"
    fi
    
    if [ -f "$base_dir/QUICK_START.md" ]; then
        log_success "QUICK_START.md (快速参考)"
    fi
    
    if [ -f "$base_dir/COMPLETION_SUMMARY.md" ]; then
        log_success "COMPLETION_SUMMARY.md (完成总结)"
    fi
}

# Demo 7: 快速测试
demo_quick_test() {
    log_header "演示 7: 快速健康检查"
    
    log_info "执行快速健康检查..."
    echo
    
    script="/workspaces/rio_updater/install-cnb-uv.sh"
    if [ -f "$script" ] && [ -x "$script" ] && sh -n "$script" 2>/dev/null; then
        log_success "安装脚本: 健康✓"
    else
        log_error "安装脚本: 问题✗"
        return 1
    fi
    
    test_script="/workspaces/rio_updater/test_cnb_platform.py"
    if [ -f "$test_script" ] && python3 -m py_compile "$test_script" 2>/dev/null; then
        log_success "测试脚本: 健康✓"
    else
        log_error "测试脚本: 问题✗"
        return 1
    fi
    
    if curl -s -o /dev/null -w "%{http_code}" "https://cnb.cool" 2>/dev/null | grep -q "^200"; then
        log_success "CNB 平台: 在线✓"
    else
        log_error "CNB 平台: 离线✗"
        return 1
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
    
    if [ $missing -eq 0 ]; then
        log_success "所有检查通过!"
    else
        log_warning "缺失 $missing 个工具"
    fi
}

# 主菜单
show_menu() {
    log_header "CNB 平台 uv 安装脚本演示程序"
    
    cat << 'EOF'

选择一个演示项目:

  1) 验证安装环境
  2) 验证安装脚本
  3) 验证 CNB 平台
  4) 运行测试套件
  5) 查看安装选项
  6) 查看文件清单
  7) 快速健康检查
  
  8) 运行所有演示
  0) 退出

请输入选项 (0-8):
EOF
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        while true; do
            echo
            show_menu
            printf "> "
            read -r choice
            
            case $choice in
                1) demo_environment ;;
                2) demo_script_validation ;;
                3) demo_cnb_platform ;;
                4) demo_test_suite ;;
                5) demo_install_options ;;
                6) demo_file_inventory ;;
                7) demo_quick_test ;;
                8) 
                    demo_environment
                    demo_script_validation
                    demo_cnb_platform
                    demo_file_inventory
                    demo_quick_test
                    demo_install_options
                    log_header "所有演示完成！"
                    log_success "CNB 平台 uv 安装脚本已准备就绪"
                    ;;
                0) 
                    log_info "谢谢使用!"
                    exit 0 
                    ;;
                *) log_error "无效选项" ;;
            esac
        done
    else
        case $1 in
            env) demo_environment ;;
            script) demo_script_validation ;;
            cnb) demo_cnb_platform ;;
            test) demo_test_suite ;;
            options) demo_install_options ;;
            files) demo_file_inventory ;;
            check) demo_quick_test ;;
            all) 
                demo_environment
                demo_script_validation
                demo_cnb_platform
                demo_file_inventory
                demo_quick_test
                demo_install_options
                ;;
            *)
                printf "用法: %s [env|script|cnb|test|options|files|check|all]\n" "$0"
                exit 1
                ;;
        esac
    fi
}

# 运行主函数
main "$@"
