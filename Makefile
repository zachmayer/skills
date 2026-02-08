SKILLS_DIR := skills
INSTALL_DIR := $(HOME)/.claude/skills
EXTERNAL_DIR := $(SKILLS_DIR)/.external

check-requirements:
	uv --version
.PHONY: check-requirements


install: check-requirements
	uv python install
	uv sync --locked --all-groups
	uv run pre-commit install
.PHONY: install


upgrade:
	uv lock --upgrade
	uv run pre-commit autoupdate
.PHONY: upgrade


lint:
	uv run pre-commit run -a
.PHONY: lint


typecheck:
	uv run ty check skills/ main/
.PHONY: typecheck


test:
	uv run pytest
.PHONY: test


build:
	uv build
.PHONY: build


install-local:
	@echo "Installing skills to $(INSTALL_DIR)..."
	@mkdir -p $(INSTALL_DIR)
	@for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		if [ "$$skill_name" != ".external" ]; then \
			echo "  Linking $$skill_name"; \
			ln -sfn "$$(pwd)/$$skill_dir" "$(INSTALL_DIR)/$$skill_name"; \
		fi; \
	done
	@echo "Done. Skills available as /skill-name in Claude Code."
.PHONY: install-local


uninstall-local:
	@echo "Removing skills from $(INSTALL_DIR)..."
	@for skill_dir in $(SKILLS_DIR)/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		if [ "$$skill_name" != ".external" ]; then \
			rm -f "$(INSTALL_DIR)/$$skill_name"; \
		fi; \
	done
	@echo "Done."
.PHONY: uninstall-local


pull-external:
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
