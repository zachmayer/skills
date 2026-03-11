SKILLS_DIR := .claude/skills
INSTALL_DIR := $(HOME)/.claude/skills

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
.PHONY: help
.DEFAULT_GOAL := help


install: ## Install all dependencies, settings, and local skills
	uv python install
	uv sync --locked --all-extras --all-groups
	@echo "Clearing core.hooksPath so pre-commit can manage .git/hooks"
	git config --unset-all core.hooksPath || true
	uv run pre-commit install
	uv run playwright install chromium
	$(MAKE) install-local
	$(MAKE) install-heartbeat-agents
	$(MAKE) install-jina-grep
.PHONY: install


install-jina-grep: ## Install jina-grep CLI for semantic search (Apple Silicon only)
	uv tool install git+https://github.com/jina-ai/jina-grep-cli.git
	@echo "Installed jina-grep. Run 'jina-grep --help' to verify."
.PHONY: install-jina-grep


install-ci: ## Install without heavy deps (marker-pdf/torch) for CI
	uv python install
	uv sync --locked --group dev
	@echo "Clearing core.hooksPath so pre-commit can manage .git/hooks"
	git config --unset-all core.hooksPath || true
	uv run pre-commit install
.PHONY: install-ci


upgrade: ## Upgrade all dependencies
	uv lock --upgrade
	uv run pre-commit autoupdate
.PHONY: upgrade


lint: ## Run linters and formatters
	uv run pre-commit run -a
.PHONY: lint


typecheck: ## Run type checker
	uv run ty check .claude/skills/ main/
.PHONY: typecheck


test: ## Run tests
	uv run pytest
.PHONY: test


test-integration: ## Run integration tests (requires gh auth)
	uv run pytest tests/integration -m integration -v
.PHONY: test-integration


build: ## Build package
	uv build
.PHONY: build


install-heartbeat-agents: ## Install heartbeat agent files to ~/.claude/agents/
	@mkdir -p $(HOME)/.claude/agents
	@cp $(SKILLS_DIR)/heartbeat/agents/*.md $(HOME)/.claude/agents/
	@if ! grep -q '^\* ' .github/CODEOWNERS 2>/dev/null; then \
		echo "WARNING: .github/CODEOWNERS has no default owner (* rule)."; \
		echo "  Heartbeat uses this for PR assignment. Add: * @yourname"; \
	fi
	@echo "Installed heartbeat agents to ~/.claude/agents/"
.PHONY: install-heartbeat-agents



install-local: ## Install settings, global CLAUDE.md, and symlink skills to ~/.claude/
	@mkdir -p $(INSTALL_DIR)
	@mkdir -p $(HOME)/claude/scratch
	@mkdir -p $(HOME)/claude/worktrees
	@mkdir -p $(HOME)/.claude/hooks
	@cp $(CURDIR)/.claude/hooks/reject-shell-operators.sh $(HOME)/.claude/hooks/reject-shell-operators.sh
	@chmod +x $(HOME)/.claude/hooks/reject-shell-operators.sh
	@ts=$$(date +%Y%m%d%H%M%S); \
	if [ -f "$(HOME)/.claude/settings.json" ]; then \
		cp "$(HOME)/.claude/settings.json" "$(HOME)/.claude/settings.json.$$ts.bak"; \
	fi; \
	if [ -f "$(HOME)/CLAUDE.md" ]; then \
		cp "$(HOME)/CLAUDE.md" "$(HOME)/CLAUDE.md.$$ts.bak"; \
	fi
	@cp settings.template.json $(HOME)/.claude/settings.json
	@echo "Installed settings to ~/.claude/settings.json"
	@cp CLAUDE.template.md $(HOME)/CLAUDE.md
	@echo "Installed global CLAUDE.md to ~/CLAUDE.md"
	@for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		echo "  Linking $$skill_name"; \
		ln -sfn "$$(pwd)/$$skill_dir" "$(INSTALL_DIR)/$$skill_name"; \
	done
	@echo "Done. Skills available as /skill-name in Claude Code."
	@echo ""
	@echo "Some skills need API keys."
	@echo "Add them to your shell profile (~/.zshrc or ~/.bashrc):"
	@echo '  export OPENAI_API_KEY="your-key"'
	@echo '  export ANTHROPIC_API_KEY="your-key"'
	@echo '  export GOOGLE_API_KEY="your-key"'
.PHONY: install-local


HEARTBEAT_LABEL := com.anthropic.claude-heartbeat
HEARTBEAT_PLIST := $(HOME)/Library/LaunchAgents/$(HEARTBEAT_LABEL).plist
HEARTBEAT_LOG_DIR := $(HOME)/.claude/logs

setup-heartbeat-labels: ## Create ai:* labels on all heartbeat repos
	@REPOS_FILE="$(HOME)/.claude/heartbeat-repos.conf"; \
	if [ -f "$$REPOS_FILE" ]; then \
		REPOS=$$(grep -v '^\s*#' "$$REPOS_FILE" | grep -v '^\s*$$'); \
	else \
		REPOS="zachmayer/skills"; \
	fi; \
	for repo in $$REPOS; do \
		echo "Creating labels on $$repo..."; \
		gh label create "ai:queued" --repo "$$repo" --color 0075CA --description "In the AI queue; heartbeat picks up next cycle" --force 2>/dev/null || true; \
		gh label create "ai:coding" --repo "$$repo" --color FBCA04 --description "AI agent is actively coding; do not modify" --force 2>/dev/null || true; \
		gh label create "ai:review" --repo "$$repo" --color 6F42C1 --description "PR needs review; AI or human can review" --force 2>/dev/null || true; \
	done
	@echo "Labels created. Note: gh label create is in the deny list — run from a regular terminal."
	@echo "Manually delete old ai:human labels if present."
.PHONY: setup-heartbeat-labels


setup-heartbeat-token: ## Generate OAuth token for heartbeat (interactive, one-time)
	@echo "=== Heartbeat Token Setup ==="
	@echo ""
	@echo "This generates a 1-year OAuth token using your Claude subscription."
	@echo "The token will be stored in ~/.claude/heartbeat.env (mode 600)."
	@echo ""
	@echo "Step 1: Run this command and follow the browser prompts:"
	@echo ""
	@echo "  claude setup-token"
	@echo ""
	@echo "Step 2: Copy the token it outputs, then run:"
	@echo ""
	@echo '  echo "export CLAUDE_CODE_OAUTH_TOKEN=<paste-token-here>" > ~/.claude/heartbeat.env'
	@echo "  chmod 600 ~/.claude/heartbeat.env"
	@echo ""
	@echo "Step 3: Install the heartbeat:"
	@echo ""
	@echo "  make install-heartbeat"
	@echo ""
	@if [ -f "$(HOME)/.claude/heartbeat.env" ]; then \
		echo "Status: ~/.claude/heartbeat.env exists (token already configured)"; \
	else \
		echo "Status: ~/.claude/heartbeat.env NOT FOUND — complete steps above first"; \
	fi
.PHONY: setup-heartbeat-token


install-heartbeat: ## Install heartbeat launchd agent (every 15 min)
	@# Validate token exists before installing
	@if [ ! -f "$(HOME)/.claude/heartbeat.env" ]; then \
		echo "ERROR: ~/.claude/heartbeat.env not found."; \
		echo "Run 'make setup-heartbeat-token' first."; \
		exit 1; \
	fi
	@mkdir -p $(HEARTBEAT_LOG_DIR)
	@SCRIPT="$$(cd $(SKILLS_DIR)/heartbeat/scripts && pwd)/heartbeat.sh"; \
	chmod +x "$$SCRIPT"; \
	(crontab -l 2>/dev/null || true) | sed '/heartbeat/d' | crontab -; \
	launchctl bootout gui/$$(id -u)/$(HEARTBEAT_LABEL) 2>/dev/null || true; \
	sed -e "s|HEARTBEAT_SCRIPT_PATH|$$SCRIPT|g" \
		-e "s|HEARTBEAT_LOG_DIR|$(HEARTBEAT_LOG_DIR)|g" \
		$(SKILLS_DIR)/heartbeat/$(HEARTBEAT_LABEL).plist \
		> $(HEARTBEAT_PLIST); \
	launchctl bootstrap gui/$$(id -u) $(HEARTBEAT_PLIST); \
	echo ""; \
	echo "Heartbeat installed (launchd, every 15 min)."; \
	echo "  Verify:  launchctl list | grep claude-heartbeat"; \
	echo "  Logs:    tail -20 $(HEARTBEAT_LOG_DIR)/heartbeat.log"; \
	echo "  Test:    make test-heartbeat"; \
	echo "  Stop:    make uninstall-heartbeat"
.PHONY: install-heartbeat


uninstall-heartbeat: ## Remove heartbeat launchd agent
	@launchctl bootout gui/$$(id -u)/$(HEARTBEAT_LABEL) 2>/dev/null || true
	@rm -f $(HEARTBEAT_PLIST)
	@# Also remove old cron entry if present
	@(crontab -l 2>/dev/null || true) | sed '/heartbeat/d' | crontab -
	@echo "Heartbeat uninstalled."
.PHONY: uninstall-heartbeat


test-heartbeat: ## Run heartbeat script once manually (dry run)
	@echo "Running heartbeat manually..."
	@$(SKILLS_DIR)/heartbeat/scripts/heartbeat.sh
.PHONY: test-heartbeat


uninstall-local: ## Remove skills from ~/.claude/skills/
	@echo "Removing skills from $(INSTALL_DIR)..."
	@for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		rm -f "$(INSTALL_DIR)/$$skill_name"; \
	done
	@echo "Done."
.PHONY: uninstall-local


clean: ## Remove venv and lock file, then re-sync
	rm -rf .venv
	rm -f uv.lock
	uv sync --all-groups
.PHONY: clean
