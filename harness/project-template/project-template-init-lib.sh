#!/usr/bin/env bash

usage() {
  cat <<'EOF' >&2
Usage:
  bash ~/.agents/harness/project-template-init.sh --list

  bash ~/.agents/harness/project-template-init.sh backend-go \
    --dest <dir> \
    --module <go-module> \
    --service <service-name> \
    --domain <domain-name> \
    [--git-user-name <name>] \
    [--git-user-email <email>] \
    [--skip-git-init] \
    [--force] [--dry-run]

  bash ~/.agents/harness/project-template-init.sh frontend-vue \
    --dest <dir> \
    --app-name <app-name> \
    [--auth-redirect <route>] \
    [--login-path <route>] \
    [--git-user-name <name>] \
    [--git-user-email <email>] \
    [--skip-git-init] \
    [--force] [--dry-run]

Description:
  Convenience wrapper around project-template starter assets.

Aliases:
  backend-go   -> backend/go-backend-onion-template
  frontend-vue -> frontend/vue-feature-sliced-template
EOF
}

resolve_template() {
  case "$1" in
    backend-go|go-backend|backend/go-backend-onion-template)
      printf '%s\n' "backend/go-backend-onion-template"
      ;;
    frontend-vue|vue-frontend|frontend/vue-feature-sliced-template)
      printf '%s\n' "frontend/vue-feature-sliced-template"
      ;;
    *)
      printf '%s\n' "$1"
      ;;
  esac
}

is_nonempty_value() {
  local value="$1"
  [[ -n "${value//[[:space:]]/}" ]]
}

resolve_git_identity() {
  local field="$1"
  local value="$2"
  local prompt=""

  case "$field" in
    name)
      prompt="Git user.name"
      ;;
    email)
      prompt="Git user.email"
      ;;
    *)
      echo "FAIL: unsupported git identity field: $field" >&2
      exit 1
      ;;
  esac

  if is_nonempty_value "$value"; then
    printf '%s\n' "$value"
    return 0
  fi

  if [[ -t 0 ]]; then
    read -r -p "$prompt: " value
  fi

  if ! is_nonempty_value "$value"; then
    echo "FAIL: git user $field is required for new repositories; pass --git-user-name and --git-user-email or rerun interactively" >&2
    exit 1
  fi

  printf '%s\n' "$value"
}
