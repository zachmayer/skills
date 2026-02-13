SKILLS_DIR := skills
INSTALL_DIR := $(HOME)/.claude/skills

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
.PHONY: help
.DEFAULT_GOAL := help


install: ## Install all dependencies, settings, and local skills
	uv python install
	uv sync --locked --all-groups
	uv run pre-commit install
	uv run playwright install chromium
	$(MAKE) install-local
.PHONY: install


install-ci: ## Install without heavy deps (marker-pdf/torch) for CI
	uv python install
	uv sync --locked --group dev
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
	uv run ty check skills/ main/
.PHONY: typecheck


test: ## Run tests
	uv run pytest
.PHONY: test


build: ## Build package
	uv build
.PHONY: build


install-local: ## Install settings and symlink skills to ~/.claude/
	@mkdir -p $(INSTALL_DIR)
	@if [ -f "$(HOME)/.claude/settings.json" ]; then \
		cp "$(HOME)/.claude/settings.json" "$(HOME)/.claude/settings.json.bak"; \
	fi
	@cp settings.template.json $(HOME)/.claude/settings.json
	@echo "Installed settings to ~/.claude/settings.json"
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
HEARTBEAT_LOG_DIR := $(HOME)/claude/obsidian/heartbeat

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


install-heartbeat: ## Install heartbeat launchd agent (every hour)
	@# Validate token exists before installing
	@if [ ! -f "$(HOME)/.claude/heartbeat.env" ]; then \
		echo "ERROR: ~/.claude/heartbeat.env not found."; \
		echo "Run 'make setup-heartbeat-token' first."; \
		exit 1; \
	fi
	@# Create task directory and seed file
	@mkdir -p $(HEARTBEAT_LOG_DIR)
	@if [ ! -f $(HEARTBEAT_LOG_DIR)/tasks.md ]; then \
		printf '# Heartbeat Tasks\n\nTasks for Claude to process on each heartbeat cycle.\n\n## Pending\n\n## Completed\n\n' > $(HEARTBEAT_LOG_DIR)/tasks.md; \
		echo "Created task file at $(HEARTBEAT_LOG_DIR)/tasks.md"; \
	fi
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
	echo "Heartbeat installed (launchd, every hour)."; \
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
	@echo "Heartbeat uninstalled. Task file preserved at $(HEARTBEAT_LOG_DIR)/tasks.md"
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
