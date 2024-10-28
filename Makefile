# Makefile

DIRS ?= api docker frontend prompts
IGNORE ?= .git,node_modules,.DS_Store,__pycache__, .pyc, .pyo
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
	@for dir in $(DIRS); do \
		if [ -d "$$dir" ]; then \
			find "$$dir" -type f $(IGNORE_ARGS) -print0 | while IFS= read -r -d '' file; do \
				cat "$$file" >> $(TMP_FILE); \
				echo -e "\n\n" >> $(TMP_FILE); \
			done; \
		else \
			echo "Warning: Directory $$dir does not exist" >&2; \
		fi \
	done
	@cat $(TMP_FILE) | pbcopy
	@rm $(TMP_FILE)