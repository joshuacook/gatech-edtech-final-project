DIRS ?= api docker frontend/src frontend.bak prompts
FILES ?= docker-compose.yml

IGNORE_DIRS ?= .git node_modules __pycache__ .DS_Store
IGNORE_FILES ?= *.pyc *.pyo *.ico *.woff *.woff2 *.ttf *.eot *.svg *.png *.jpg *.jpeg *.gif
comma := ,
space := $(empty) $(empty)
TMP_FILE := $(shell mktemp)
FRONTEND_CONTAINER := $(shell docker-compose ps -q frontend)

up:
	docker-compose up -d

down:
	docker-compose down

reset:
	docker-compose down --volumes
	rm -rf filestore
	docker-compose up -d

build:
	docker-compose build --no-cache

logs:
	docker-compose logs -f api frontend db

ps:
	docker-compose ps

npm-install-%:
	cd frontend && npm install $* --save
	docker exec -i $(FRONTEND_CONTAINER) npm install $*

cat:
	@> $(TMP_FILE)
	@echo "Processing files..."
	@# Process individual files first
	@for file in $(FILES); do \
		if [ -f "$$file" ]; then \
			echo "Adding: $$file"; \
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
			echo "Scanning directory: $$dir"; \
			find "$$dir" -type f \
				$(foreach dir,$(IGNORE_DIRS),-not -path "*/$(dir)/*") \
				$(foreach pattern,$(IGNORE_FILES),-not -name "$(pattern)") \
				-print0 | while IFS= read -r -d '' file; do \
					echo "Adding: $$file"; \
					echo -e "\n\n# $$file\n\n" >> $(TMP_FILE); \
					cat "$$file" >> $(TMP_FILE); \
					echo -e "\n\n" >> $(TMP_FILE); \
			done; \
		else \
			echo "Warning: Directory $$dir does not exist" >&2; \
		fi \
	done
	@echo "Copying contents to clipboard..."
	@cat $(TMP_FILE) | pbcopy
	@rm $(TMP_FILE)
	@echo "Done!"