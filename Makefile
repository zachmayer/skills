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


install-heartbeat: ## Set up heartbeat cron job (every 4 hours)
	@mkdir -p ~/claude/obsidian/heartbeat
	@if [ ! -f ~/claude/obsidian/heartbeat/tasks.md ]; then \
		printf '# Heartbeat Tasks\n\n## Pending\n\n## Completed\n\n' > ~/claude/obsidian/heartbeat/tasks.md; \
		echo "Created task file at ~/claude/obsidian/heartbeat/tasks.md"; \
	fi
	@SCRIPT="$$(cd $(SKILLS_DIR)/heartbeat/scripts && pwd)/heartbeat.sh"; \
	chmod +x "$$SCRIPT"; \
	(crontab -l 2>/dev/null | grep -v '# CLAUDE_HEARTBEAT'; echo "0 */4 * * * $$SCRIPT >> ~/claude/obsidian/heartbeat/heartbeat.log 2>&1 # CLAUDE_HEARTBEAT") | crontab -; \
	echo "Heartbeat cron installed (every 4 hours). Verify with: crontab -l"
.PHONY: install-heartbeat


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


sync-external: ## Sync external skills from upstream URLs
	@uv run python scripts/sync_external.py
.PHONY: sync-external
