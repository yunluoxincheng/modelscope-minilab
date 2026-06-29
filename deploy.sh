#!/usr/bin/env bash
# ============================================================================
# 智模工坊 / ModelScope MiniLab —— 服务器一键部署脚本
#
# 服务器上只需把这个脚本和 .env 放在同一目录（docker-compose.yml 缺失时
# 会自动从 GitHub 拉取）。运行：
#   ./deploy.sh             部署/更新（拉镜像 + 启动 backend+redis + 健康检查）
#   ./deploy.sh mysql       同上，并额外启用 MySQL（--profile mysql）
#   ./deploy.sh status      查看容器状态
#   ./deploy.sh logs        跟随后端日志（Ctrl+C 退出，不影响服务）
#   ./deploy.sh restart     重启服务
#   ./deploy.sh down        停止并移除容器（数据卷保留）
#   ./deploy.sh health      只做健康检查
#   ./deploy.sh help        帮助
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

REPO_RAW="https://raw.githubusercontent.com/yunluoxincheng/modelscope-minilab/main"
HEALTH_URL="http://127.0.0.1:8000/api/health"

# ---------- 输出 ----------
if [[ -t 1 ]]; then
  C_G=$'\033[32m'; C_R=$'\033[31m'; C_Y=$'\033[33m'; C_C=$'\033[36m'; C_0=$'\033[0m'
else
  C_G=""; C_R=""; C_Y=""; C_C=""; C_0=""
fi
info() { printf "%s==>%s %s\n" "$C_C" "$C_0" "$*"; }
ok()   { printf "%s[OK]%s %s\n"   "$C_G" "$C_0" "$*"; }
warn() { printf "%s[!]%s %s\n"    "$C_Y" "$C_0" "$*"; }
die()  { printf "%s[ERR]%s %s\n"  "$C_R" "$C_0" "$*" >&2; exit 1; }

# ---------- 工具 ----------
has() { command -v "$1" >/dev/null 2>&1; }

detect_compose() {
  if docker compose version >/dev/null 2>&1; then
    COMPOSE=(docker compose)
  elif has docker-compose; then
    COMPOSE=(docker-compose)
  else
    die "未找到 docker compose，请先安装 Docker Engine（含 compose 插件）。"
  fi
}

# 读取 .env 里某个变量的值（不回显到日志，仅内部使用）
env_value() {
  grep -E "^${1}=" .env 2>/dev/null | head -1 | cut -d= -f2- \
    | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//"
}

assert_nonempty() {
  [[ -n "$(env_value "$1")" ]] || die ".env 里 $2（$1）为空，请先填写。"
}
assert_not_placeholder() {
  [[ "$(env_value "$1")" != "$2" ]] || die ".env 里 $1 仍是占位值「$2」，请改成真实值。"
}

# ---------- 步骤 ----------
ensure_files() {
  info "检查文件"
  if [[ ! -f docker-compose.yml ]]; then
    warn "未找到 docker-compose.yml，从 GitHub 拉取..."
    curl -fsSL "$REPO_RAW/docker-compose.yml" -o docker-compose.yml \
      || die "下载 docker-compose.yml 失败，请手动放到脚本同目录。"
    ok "已下载 docker-compose.yml"
  fi
  [[ -f .env ]] || die "未找到 .env。请复制 docker-compose.env.example 为 .env 并填好密钥。"
  ok "docker-compose.yml / .env 就绪"
}

preflight() {
  info "前置检查"
  has docker || die "未找到 docker，请先安装 Docker Engine。"
  has curl   || die "未找到 curl（健康检查需要）。"
  detect_compose
  ok "compose 命令：${COMPOSE[*]}"

  ensure_files

  info "校验 .env 关键变量（不打印值）"
  assert_nonempty        JWT_SECRET       "JWT 密钥"
  assert_not_placeholder JWT_SECRET       "please-replace-with-openssl-rand-hex-32"
  assert_nonempty        WECHAT_APP_ID    "微信 AppID"
  assert_nonempty        WECHAT_APP_SECRET "微信 AppSecret"

  if [[ "$(env_value ENV)" == "prod" && "$(env_value WECHAT_AUTH_MOCK)" == "true" ]]; then
    die "生产环境（ENV=prod）禁止 WECHAT_AUTH_MOCK=true，请在 .env 改为 false。"
  fi
  ok "关键变量校验通过"
}

wait_health() {
  info "等待后端就绪（最多 60s）"
  local i
  for i in $(seq 1 30); do
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
      ok "后端健康检查通过（$HEALTH_URL）"
      return 0
    fi
    sleep 2
  done
  return 1
}

cmd_deploy() {
  local profile="${1:-}"
  preflight
  info "拉取镜像（自动匹配服务器架构）"
  if [[ -n "$profile" ]]; then
    "${COMPOSE[@]}" --profile "$profile" pull
    info "启动 backend + redis + $profile"
    "${COMPOSE[@]}" --profile "$profile" up -d --remove-orphans
  else
    "${COMPOSE[@]}" pull
    info "启动 backend + redis"
    "${COMPOSE[@]}" up -d --remove-orphans
  fi
  if ! wait_health; then
    die "后端 60s 内未就绪，请查看日志：${COMPOSE[*]} logs backend"
  fi
  echo
  ok "部署完成，容器状态："
  "${COMPOSE[@]}" ps
  echo
  info "上线前别忘了："
  echo "  1) Nginx + HTTPS 反代到 127.0.0.1:8000（微信小程序必需）"
  echo "  2) 微信公众平台配置 request / uploadFile 合法域名"
  echo "  3) 小程序 miniapp/utils/config.js 的 API_BASE 改成 https://你的域名/api"
}

cmd_status()  { detect_compose; "${COMPOSE[@]}" ps; }
cmd_logs()    { detect_compose; "${COMPOSE[@]}" logs -f --tail=200 backend; }
cmd_restart() { detect_compose; warn "重启服务"; "${COMPOSE[@]}" restart; }
cmd_down()    { detect_compose; warn "停止并移除容器（数据卷保留）"; "${COMPOSE[@]}" down; }
cmd_health()  { detect_compose; if ! wait_health; then die "健康检查未通过"; fi; }

usage() { sed -n '3,15p' "$0" | sed 's/^# \{0,1\}//'; }

main() {
  case "${1:-up}" in
    up|deploy) cmd_deploy "" ;;
    mysql)     cmd_deploy "mysql" ;;
    status|ps) cmd_status ;;
    logs)      cmd_logs ;;
    restart)   cmd_restart ;;
    down|stop) cmd_down ;;
    health)    cmd_health ;;
    help|-h|--help) usage ;;
    *) die "未知命令：$1（用 ./deploy.sh help 查看用法）" ;;
  esac
}

main "$@"
