SKILLS_DIR := skills
INSTALL_DIR := $(HOME)/.claude/skills
EXTERNAL_DIR := $(SKILLS_DIR)/.external

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
.PHONY: help
.DEFAULT_GOAL := help


install: ## Install all dependencies, settings, external skills, and local skills
	uv python install
	uv sync --locked --all-groups
	uv run pre-commit install
	$(MAKE) pull-external
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
		if [ "$$skill_name" != ".external" ]; then \
			echo "  Linking $$skill_name"; \
			ln -sfn "$$(pwd)/$$skill_dir" "$(INSTALL_DIR)/$$skill_name"; \
		fi; \
	done
	@echo "Done. Skills available as /skill-name in Claude Code."
.PHONY: install-local


install-heartbeat: ## Set up heartbeat cron job (every 4 hours)
	@mkdir -p ~/claude/obsidian/heartbeat
	@if [ ! -f ~/claude/obsidian/heartbeat/tasks.md ]; then \
		printf '# Heartbeat Tasks\n\n## Pending\n\n## Completed\n\n' > ~/claude/obsidian/heartbeat/tasks.md; \
		echo "Created task file at ~/claude/obsidian/heartbeat/tasks.md"; \
	fi
	@SCRIPT="$$(cd $(SKILLS_DIR)/heartbeat/scripts && pwd)/heartbeat.sh"; \
	chmod +x "$$SCRIPT"; \
	(crontab -l 2>/dev/null | grep -v heartbeat; echo "0 */4 * * * $$SCRIPT >> ~/claude/obsidian/heartbeat/heartbeat.log 2>&1") | crontab -; \
	echo "Heartbeat cron installed (every 4 hours). Verify with: crontab -l"
.PHONY: install-heartbeat


uninstall-local: ## Remove skills from ~/.claude/skills/
	@echo "Removing skills from $(INSTALL_DIR)..."
	@for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		if [ "$$skill_name" != ".external" ]; then \
			rm -f "$(INSTALL_DIR)/$$skill_name"; \
		fi; \
	done
	@echo "Done."
.PHONY: uninstall-local


clean: ## Remove venv and external skills, then re-sync
	rm -rf .venv
	rm -rf $(EXTERNAL_DIR)
	uv sync --all-groups
.PHONY: clean


pull-external: ## Pull external skills from FUTURE_TOKENS
	@mkdir -p $(EXTERNAL_DIR)
	@echo "Pulling FUTURE_TOKENS skills..."
	@if [ -d "/tmp/FUTURE_TOKENS" ]; then \
		cd /tmp/FUTURE_TOKENS && git pull; \
	else \
		git clone https://github.com/jordanrubin/FUTURE_TOKENS.git /tmp/FUTURE_TOKENS; \
	fi
	@for skill_dir in /tmp/FUTURE_TOKENS/*/; do \
		if [ -f "$$skill_dir/SKILL.md" ] || [ -f "$$skill_dir/$$(basename $$skill_dir | tr '[:lower:]' '[:upper:]').md" ]; then \
			skill_name=$$(basename "$$skill_dir" | tr '[:upper:]' '[:lower:]'); \
			echo "  Copying $$skill_name"; \
			cp -r "$$skill_dir" "$(EXTERNAL_DIR)/$$skill_name"; \
		fi; \
	done
	@echo "External skills in $(EXTERNAL_DIR)/. Run 'make install-local' to link them."
.PHONY: pull-external
