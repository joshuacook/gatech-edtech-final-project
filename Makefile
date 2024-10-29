DIRS ?= api docker frontend prompts
FILES ?= docker-compose.yml
IGNORE ?= .git,node_modules,.DS_Store,__pycache__,.pyc,.pyo
IGNORE_ARGS := $(foreach pattern,$(subst $(comma),$(space),$(IGNORE)),-not -path "*/$(pattern)/*")
comma := ,
space := $(empty) $(empty)
TMP_FILE := $(shell mktemp)

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build --no-cache

logs:
	docker-compose logs -f api frontend db

ps:
	docker-compose ps

cat:
	@> $(TMP_FILE)
	@# Process individual files first
	@for file in $(FILES); do \
		if [ -f "$$file" ]; then \
			echo -e "\n\n# $$file\n\n" >> $(TMP_FILE); \
			cat "$$file" >> $(TMP_FILE); \
			echo -e "\n\n" >> $(TMP_FILE); \
		else \
			echo "Warning: File $$file does not exist" >&2; \
		fi \
	done
	@# Process directories recursively
	@for dir in $(DIRS); do \
		if [ -d "$$dir" ]; then \
			find "$$dir" -type f -print0 $(IGNORE_ARGS) | while IFS= read -r -d '' file; do \
				echo -e "\n\n# $$file\n\n" >> $(TMP_FILE); \
				cat "$$file" >> $(TMP_FILE); \
				echo -e "\n\n" >> $(TMP_FILE); \
			done; \
		else \
			echo "Warning: Directory $$dir does not exist" >&2; \
		fi \
	done
	@cat $(TMP_FILE) | pbcopy
	@rm $(TMP_FILE)