SKILLS_DIR := .claude/skills
AGENTS_DIR := .claude/agents
INSTALL_DIR := $(HOME)/.claude/skills
AGENTS_INSTALL_DIR := $(HOME)/.claude/agents

# ── Help ─────────────────────────────────────────────────────────

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'
.PHONY: help

# ── Install ──────────────────────────────────────────────────────

install: ## Install everything: system deps, UV deps, skills, agents, config
	@# ── System dependencies (requires Homebrew) ──
	@command -v brew >/dev/null || { echo "ERROR: Homebrew required. Install from https://brew.sh"; exit 1; }
	brew install uv gh
	@# ── Python + UV dependencies ──
	uv python install
	uv sync --locked --all-extras --all-groups
	@# ── Pre-commit hooks ──
	@# Note: only unsets repo-local core.hooksPath. A global setting would still interfere.
	git config --unset-all core.hooksPath || true
	uv run pre-commit install
	@# ── Browser for web_grab skill ──
	uv run playwright install chromium
	@# ── Semantic search CLI (Apple Silicon) ──
	uv tool install git+https://github.com/jina-ai/jina-grep-cli.git || true
	@# ── Directories ──
	@mkdir -p $(INSTALL_DIR) $(AGENTS_INSTALL_DIR) $(HOME)/claude/scratch $(HOME)/claude/worktrees $(HOME)/.claude/hooks
	@# ── Security hooks ──
	@cp $(CURDIR)/.claude/hooks/reject-shell-operators.sh $(HOME)/.claude/hooks/reject-shell-operators.sh
	@chmod +x $(HOME)/.claude/hooks/reject-shell-operators.sh
	@# ── Settings and global CLAUDE.md (with timestamped backup) ──
	@ts=$$(date +%Y%m%d%H%M%S); \
	if [ -f "$(HOME)/.claude/settings.json" ]; then cp "$(HOME)/.claude/settings.json" "$(HOME)/.claude/settings.json.$$ts.bak"; fi; \
	if [ -f "$(HOME)/CLAUDE.md" ]; then cp "$(HOME)/CLAUDE.md" "$(HOME)/CLAUDE.md.$$ts.bak"; fi
	@cp settings.template.json $(HOME)/.claude/settings.json
	@cp CLAUDE.template.md $(HOME)/CLAUDE.md
	@# ── Symlink skills ──
	@for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		echo "  Linking $$skill_name"; \
		ln -sfn "$$(pwd)/$$skill_dir" "$(INSTALL_DIR)/$$skill_name"; \
	done
	@# ── Symlink agents ──
	@for agent in $(AGENTS_DIR)/*.md; do \
		agent_name=$$(basename "$$agent"); \
		echo "  Linking agent $$agent_name"; \
		ln -sfn "$$(pwd)/$$agent" "$(AGENTS_INSTALL_DIR)/$$agent_name"; \
	done
	@echo ""
	@echo "Install complete. Skills available as /skill-name in Claude Code."
	@echo ""
	@echo "Some skills need API keys. Add to ~/.zshrc:"
	@echo '  export OPENAI_API_KEY="your-key"'
	@echo '  export ANTHROPIC_API_KEY="your-key"'
	@echo '  export GOOGLE_API_KEY="your-key"'
.PHONY: install

install-ci: ## Install for CI (no system deps, no heavy extras)
	uv python install
	uv sync --locked --group dev
.PHONY: install-ci

uninstall: ## Remove skills, agents, and hooks from ~/.claude/
	@echo "Removing skills from $(INSTALL_DIR)..."
	@for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		rm -f "$(INSTALL_DIR)/$$skill_name"; \
	done
	@rm -f $(HOME)/.claude/hooks/reject-shell-operators.sh
	@for agent in $(AGENTS_DIR)/*.md; do \
		rm -f "$(AGENTS_INSTALL_DIR)/$$(basename "$$agent")"; \
	done
	@echo "Done."
.PHONY: uninstall

# ── Development ──────────────────────────────────────────────────

lint: ## Run linters and formatters
	uv run pre-commit run -a
.PHONY: lint

typecheck: ## Run type checker
	uv run ty check .claude/skills/ main/ --exclude '.claude/skills/pdf_to_markdown/' --exclude '.claude/skills/web_grab/scripts/browser.py' --exclude '.claude/skills/web_grab/scripts/fetch_page.py'
.PHONY: typecheck

test: ## Run tests
	uv run pytest
.PHONY: test

test-integration: ## Run integration tests (requires gh auth)
	uv run pytest tests/integration -m integration -v
.PHONY: test-integration

check: lint typecheck test ## Run all checks (lint + typecheck + test)
	@echo "All checks passed."
.PHONY: check

upgrade: ## Upgrade all dependencies
	uv lock --upgrade
	uv run pre-commit autoupdate
.PHONY: upgrade

clean: ## Remove venv and re-sync
	rm -rf .venv
	uv sync --locked --all-extras --all-groups
.PHONY: clean

# ── Heartbeat (opt-in, machine-specific) ─────────────────────────

HEARTBEAT_LABEL := com.anthropic.claude-heartbeat
HEARTBEAT_PLIST := $(HOME)/Library/LaunchAgents/$(HEARTBEAT_LABEL).plist
HEARTBEAT_LOG_DIR := $(HOME)/.claude/logs

install-heartbeat: ## Install heartbeat launchd daemon (every 15 min)
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
	@REPOS_FILE="$(HOME)/.claude/heartbeat-repos.conf"; \
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
