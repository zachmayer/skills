SKILLS_DIR := .claude/skills
AGENTS_DIR := .claude/agents
INSTALL_DIR := $(HOME)/.claude/skills
AGENTS_INSTALL_DIR := $(HOME)/.claude/agents
CODEX_SKILLS_DIR := $(HOME)/.agents/skills
CODEX_CONFIG_DIR := $(HOME)/.codex

# ── Help ─────────────────────────────────────────────────────────

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'
.PHONY: help

# ── Install ──────────────────────────────────────────────────────

install-ci: ## Install for CI (UV deps + pre-commit, no system deps)
	uv python install
	uv sync --locked --group dev
	git config --unset-all core.hooksPath || true
	uv run pre-commit install
.PHONY: install-ci

install: ## Install everything: system deps, UV deps, skills, agents, config
	@# ── System dependencies (requires Homebrew) ──
	@command -v brew >/dev/null || { echo "ERROR: Homebrew required. Install from https://brew.sh"; exit 1; }
	brew update
	brew upgrade
	brew install uv gh pyright node jq google-cloud-sdk trufflehog
	brew install --cask codex
	brew doctor || true
	npm install -g @googleworkspace/cli
	@# ── Claude Code (native app, not npm) ──
	@command -v claude >/dev/null || { echo "  Installing Claude Code..."; curl -fsSL https://claude.ai/install.sh | bash; }
	@# ── Claude Code plugins ──
	claude plugin install ralph-loop@claude-plugins-official
	claude plugin install chrome-devtools-mcp@claude-plugins-official
	@# ── Fix plugin hook permissions ──
	@# claude-plugins-official marketplace re-extracts from GCS on every Claude
	@# startup, losing execute bits on all .sh files (anthropics/claude-code#38705).
	@# This chmod only helps until the next restart; the upstream fix is pending.
	@find $(HOME)/.claude/plugins/marketplaces -name "*.sh" -exec chmod +x {} \;
	@find $(HOME)/.claude/plugins/cache -name "*.sh" -exec chmod +x {} \;
	@# ── Python + UV dependencies (via install-ci) ──
	$(MAKE) install-ci
	@# ── All extras (browser, etc.) ──
	uv sync --locked --all-extras --all-groups
	@# ── Browser for web-grab skill ──
	uv run playwright install chromium
	@# ── Semantic search CLI (Apple Silicon) ──
	uv tool install git+https://github.com/jina-ai/jina-grep-cli.git || true
	@# ── Kaggle CLI ──
	uv tool install kaggle || true
	@# ── Directories ──
	@mkdir -p $(INSTALL_DIR) $(AGENTS_INSTALL_DIR) $(HOME)/claude/scratch $(HOME)/claude/worktrees $(HOME)/.claude/hooks $(CODEX_SKILLS_DIR) $(CODEX_CONFIG_DIR)
	@# ── Security hooks ──
	@cp $(CURDIR)/.claude/hooks/reject-shell-operators.sh $(HOME)/.claude/hooks/reject-shell-operators.sh
	@chmod +x $(HOME)/.claude/hooks/reject-shell-operators.sh
	@# ── Settings and global CLAUDE.md (with timestamped backup) ──
	@set -e; ts=$$(date +%Y%m%d%H%M%S); \
	if [ -f "$(HOME)/.claude/settings.json" ]; then cp "$(HOME)/.claude/settings.json" "$(HOME)/.claude/settings.json.$$ts.bak"; fi; \
	if [ -f "$(HOME)/CLAUDE.md" ]; then cp "$(HOME)/CLAUDE.md" "$(HOME)/CLAUDE.md.$$ts.bak"; fi
	@cp settings.template.json $(HOME)/.claude/settings.json
	@cp CLAUDE.template.md $(HOME)/CLAUDE.md
	@# ── Symlink skills ──
	@set -e; for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		echo "  Linking $$skill_name"; \
		ln -sfn "$$(pwd)/$$skill_dir" "$(INSTALL_DIR)/$$skill_name"; \
	done
	@# ── Symlink agents ──
	@set -e; for agent in $(AGENTS_DIR)/*.md; do \
		agent_name=$$(basename "$$agent"); \
		echo "  Linking agent $$agent_name"; \
		ln -sfn "$$(pwd)/$$agent" "$(AGENTS_INSTALL_DIR)/$$agent_name"; \
	done
	@# ── Prune stale symlinks (from renamed/deleted skills or agents) ──
	@for link in $(INSTALL_DIR)/* $(AGENTS_INSTALL_DIR)/*; do \
		if [ -L "$$link" ] && ! [ -e "$$link" ]; then \
			echo "  Removing stale link $$link"; \
			rm -f "$$link"; \
		fi; \
	done
	@# ── Codex: symlink global AGENTS.md → CLAUDE.md ──
	@ln -sfn $(HOME)/CLAUDE.md $(CODEX_CONFIG_DIR)/AGENTS.md
	@echo "  Linked ~/.codex/AGENTS.md → ~/CLAUDE.md"
	@# ── Codex: symlink skills into ~/.agents/skills/ (direct to repo) ──
	@set -e; for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		ln -sfn "$$(pwd)/$$skill_dir" "$(CODEX_SKILLS_DIR)/$$skill_name"; \
	done
	@echo "  Linked skills into ~/.agents/skills/ for Codex"
	@# ── Codex: prune stale symlinks ──
	@for link in $(CODEX_SKILLS_DIR)/*; do \
		if [ -L "$$link" ] && ! [ -e "$$link" ]; then \
			echo "  Removing stale Codex link $$link"; \
			rm -f "$$link"; \
		fi; \
	done
	@# ── Auth (idempotent — skips if already logged in) ──
	@echo ""
	@echo "=== Auth ==="
	@gh auth status 2>/dev/null; if [ $$? -ne 0 ]; then echo "  GitHub: logging in..."; gh auth login; else echo "  GitHub: already authenticated."; fi
	@if [ -d "$(HOME)/.config/gws" ] && ls $(HOME)/.config/gws/credentials* >/dev/null 2>&1; then \
		echo "  Google Workspace: already authenticated."; \
	elif [ -f "$(HOME)/.config/gws/client_secret.json" ]; then \
		echo "  Google Workspace: logging in..."; \
		gws auth login; \
	else \
		echo "  Google Workspace: not configured yet."; \
		echo "    Run 'gws auth setup' to create a GCP project and OAuth client,"; \
		echo "    then re-run 'make install' or 'make auth' to complete login."; \
	fi
	@# ── Claude Code auth check ──
	@if claude auth status 2>/dev/null | grep -q '"loggedIn": true'; then \
		echo "  Claude Code: authenticated."; \
	else \
		echo "  WARNING: Claude Code is not logged in. Run 'claude login' to authenticate."; \
	fi
	@# ── Codex auth check ──
	@if codex auth whoami 2>/dev/null | grep -q "Logged in"; then \
		echo "  Codex: authenticated."; \
	else \
		echo "  WARNING: Codex is not logged in. Run 'codex login' to authenticate."; \
	fi
	@echo ""
	@echo "Install complete. Skills available as /skill-name in Claude Code and Codex."
	@echo ""
	@echo "Some skills need API keys. Add to ~/.zshrc:"
	@echo '  export OPENAI_API_KEY="your-key"'
	@echo '  export ANTHROPIC_API_KEY="your-key"'
	@echo '  export GOOGLE_API_KEY="your-key"'
.PHONY: install

uninstall: ## Remove skills, agents, and hooks from ~/.claude/ and ~/.agents/
	@echo "Removing skills from $(INSTALL_DIR)..."
	@set -e; for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		rm -f "$(INSTALL_DIR)/$$skill_name"; \
	done
	@rm -f $(HOME)/.claude/hooks/reject-shell-operators.sh
	@set -e; for agent in $(AGENTS_DIR)/*.md; do \
		rm -f "$(AGENTS_INSTALL_DIR)/$$(basename "$$agent")"; \
	done
	@echo "Removing Codex symlinks..."
	@set -e; for skill_dir in $(SKILLS_DIR)/*/; do \
		rm -f "$(CODEX_SKILLS_DIR)/$$(basename "$$skill_dir")"; \
	done
	@rm -f $(CODEX_CONFIG_DIR)/AGENTS.md
	@echo "Done."
.PHONY: uninstall

auth: ## Re-login to GitHub and Google Workspace
	@echo "=== GitHub ==="
	gh auth login
	@echo ""
	@echo "=== Google Workspace ==="
	gws auth login
.PHONY: auth

# ── Development ──────────────────────────────────────────────────

lint: ## Run linters and formatters
	uv run pre-commit run -a
.PHONY: lint

typecheck: ## Run type checker
	uv run ty check .claude/skills/ main/ --exclude '.claude/skills/pdf-to-markdown/' --exclude '.claude/skills/web-grab/scripts/browser.py' --exclude '.claude/skills/web-grab/scripts/fetch_page.py'
.PHONY: typecheck

ci: lint typecheck ## CI checks: lint + typecheck + unit tests
	uv lock --check
	uv run pytest
	@echo "CI checks passed."
.PHONY: ci

test: ci ## All checks: CI + integration + local tests
	uv run pytest tests/integration -m integration -v
	uv run pytest tests/integration -m local -v
	@echo "All checks passed."
.PHONY: test

upgrade: ## Upgrade all dependencies
	uv lock --upgrade
	uv run pre-commit autoupdate
.PHONY: upgrade

clean: ## Remove venv and re-sync
	rm -rf .venv
	uv sync --locked --all-extras --all-groups
.PHONY: clean

# ── Claude.ai packaging ─────────────────────────────────────────
# Skills excluded from web packaging (require auth: API keys, CLI login, or vault git push)
SKILLS_WEB_EXCLUDE := \
	api-key-checker \
	discussion-partners \
	gh-cli \
	gws-cli \
	heartbeat \
	kaggle \
	knowledge-system \
	lean-prover \
	llm-judge \
	modal \
	pr-review \
	prior-art-review \
	private-repo \
	prompt-evolution \
	ralph-loop \
	session-lifecycle \
	slack-bridge \
	superforecaster \
	trufflehog \
	web-grab

BUILD_WEB := build/claude-ai

build-web: ## Package web-compatible skills as .zip files for Claude.ai upload
	@rm -rf $(BUILD_WEB)
	@mkdir -p $(BUILD_WEB)
	@set -e; for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		skip=false; \
		for excluded in $(SKILLS_WEB_EXCLUDE); do \
			if [ "$$skill_name" = "$$excluded" ]; then skip=true; break; fi; \
		done; \
		if [ "$$skip" = "false" ]; then \
			echo "  Packaging $$skill_name"; \
			(cd "$$skill_dir" && zip -qr - . -x '__pycache__/*' '*.pyc' '.DS_Store') > "$(BUILD_WEB)/$$skill_name.zip"; \
		fi; \
	done
	@echo ""
	@included=$$(ls -1 $(BUILD_WEB) | wc -l | tr -d ' '); \
	total=$$(ls -1d $(SKILLS_DIR)/*/ | wc -l | tr -d ' '); \
	echo "Packaged $$included/$$total skills → $(BUILD_WEB)/"
	@echo "Drag .zip files into a Claude.ai Project to install."
.PHONY: build-web

# ── Heartbeat (opt-in, machine-specific) ─────────────────────────

HEARTBEAT_LABEL := com.anthropic.claude-heartbeat
HEARTBEAT_PLIST := $(HOME)/Library/LaunchAgents/$(HEARTBEAT_LABEL).plist
HEARTBEAT_LOG_DIR := $(HOME)/.claude/logs

install-heartbeat: install ## Install everything + heartbeat launchd daemon (every 15 min)
	@if [ ! -f "$(HOME)/.claude/heartbeat.env" ]; then \
		echo "ERROR: ~/.claude/heartbeat.env not found."; \
		echo "Run 'make setup-heartbeat-token' first."; \
		exit 1; \
	fi
	@mkdir -p $(HEARTBEAT_LOG_DIR) $(dir $(HEARTBEAT_PLIST))
	@set -e; \
	SCRIPT="$$(cd $(SKILLS_DIR)/heartbeat/scripts && pwd)/heartbeat.sh"; \
	chmod +x "$$SCRIPT"; \
	launchctl bootout gui/$$(id -u)/$(HEARTBEAT_LABEL) 2>/dev/null || true; \
	sed -e "s|HEARTBEAT_SCRIPT_PATH|$$SCRIPT|g" \
		-e "s|HEARTBEAT_LOG_DIR|$(HEARTBEAT_LOG_DIR)|g" \
		$(SKILLS_DIR)/heartbeat/$(HEARTBEAT_LABEL).plist \
		> $(HEARTBEAT_PLIST); \
	launchctl bootstrap gui/$$(id -u) $(HEARTBEAT_PLIST)
	@echo ""
	@echo "Heartbeat installed (launchd, every 15 min)."
	@echo "  Verify:  launchctl list | grep claude-heartbeat"
	@echo "  Logs:    tail -20 $(HEARTBEAT_LOG_DIR)/heartbeat.log"
	@echo "  Stop:    make uninstall-heartbeat"
.PHONY: install-heartbeat

uninstall-heartbeat: ## Remove heartbeat launchd daemon
	@launchctl bootout gui/$$(id -u)/$(HEARTBEAT_LABEL) 2>/dev/null || true
	@rm -f $(HEARTBEAT_PLIST)
	@echo "Heartbeat uninstalled."
.PHONY: uninstall-heartbeat

test-heartbeat: ## Run heartbeat once manually
	@echo "Running heartbeat manually..."
	@$(SKILLS_DIR)/heartbeat/scripts/heartbeat.sh
.PHONY: test-heartbeat

setup-heartbeat-labels: ## Create ai:* labels on heartbeat repos
	@set -e; REPOS_FILE="$(HOME)/.claude/heartbeat-repos.conf"; \
	if [ -f "$$REPOS_FILE" ]; then \
		REPOS=$$(grep -Ev '^[[:space:]]*($$|#)' "$$REPOS_FILE"); \
	else \
		REPOS="zachmayer/skills"; \
	fi; \
	for repo in $$REPOS; do \
		echo "Creating labels on $$repo..."; \
		gh label create "ai:queued" --repo "$$repo" --color 0075CA --description "In the AI queue; heartbeat picks up next cycle" --force; \
		gh label create "ai:coding" --repo "$$repo" --color FBCA04 --description "AI agent is actively coding; do not modify" --force; \
		gh label create "ai:review" --repo "$$repo" --color 6F42C1 --description "PR needs review; AI or human can review" --force; \
	done
	@echo "Labels created."
.PHONY: setup-heartbeat-labels

setup-heartbeat-token: ## Show instructions for heartbeat OAuth token setup
	@echo "=== Heartbeat Token Setup ==="
	@echo ""
	@echo "Step 1: Run 'claude setup-token' and follow the browser prompts."
	@echo ""
	@echo "Step 2: Save the token:"
	@echo '  echo "export CLAUDE_CODE_OAUTH_TOKEN=<paste-token>" > ~/.claude/heartbeat.env'
	@echo "  chmod 600 ~/.claude/heartbeat.env"
	@echo ""
	@echo "Step 3: make install-heartbeat"
	@echo ""
	@if [ -f "$(HOME)/.claude/heartbeat.env" ]; then \
		echo "Status: token configured"; \
	else \
		echo "Status: token NOT configured — complete steps above"; \
	fi
.PHONY: setup-heartbeat-token
