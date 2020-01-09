MAKEFLAGS += -L

VENV_DIR = .venv
LOCAL_GIT_HOOKS_DIR = scripts/git-hooks
GIT_HOOKS_DIR = .git/hooks
NODE_MODULES_DIR = node_modules
OVERVIEW_DIR = json/overview
EXAMPLE_DIR = json/examples
SCHEMA_DIR = json/schema
DOCS_DIR = docs

VENV_ACTIVATE = $(VENV_DIR)/bin/activate
INSTALL_GIT_HOOKS_SCRIPT = scripts/bash/install_git_hooks.sh
INSTALL_VENV_SCRIPT = scripts/bash/install_venv.sh
CLEANUP_OPML_SCRIPT = scripts/python/cleanup_opml.py
CREATE_RAW_OPML_SCRIPT = scripts/python/create_raw_opml.py
CONVERT_SCRIPT = scripts/python/opml_to_json.py
COMPUTE_SIGNATURE_SCRIPT = scripts/python/json_signature.py
CLEANUP_DOCS_SCRIPT = scripts/python/cleanup_docs.py

LOCAL_GIT_HOOKS_FILES := $(wildcard $(LOCAL_GIT_HOOKS_DIR)/*.sh)
GIT_HOOKS_FILES := $(patsubst $(LOCAL_GIT_HOOKS_DIR)/%,$(GIT_HOOKS_DIR)/%,${LOCAL_GIT_HOOKS_FILES:.sh=})
OVERVIEW_FILES := $(wildcard $(OVERVIEW_DIR)/*.overview.opml)
OVERVIEW_RAW_FILES := $(wildcard $(OVERVIEW_DIR)/*.overview.raw.opml)
OVERVIEW_RAW_OLD_FILES := $(wildcard $(OVERVIEW_DIR)/*.overview.raw.opml.old)
EXAMPLE_FILES := $(patsubst $(OVERVIEW_DIR)/%,$(EXAMPLE_DIR)/%,${OVERVIEW_FILES:.overview.opml=.example.json})
SCHEMA_FILES := $(patsubst $(OVERVIEW_DIR)/%,$(SCHEMA_DIR)/%,${OVERVIEW_FILES:.overview.opml=.schema.json})

JSONSCHEMA2MD_DIR = $(NODE_MODULES_DIR)/\@adobe/jsonschema2md
JSONSCHEMA2MD_BIN_PATH = $(NODE_MODULES_DIR)/.bin/jsonschema2md
DOCS_MARKDOWN_FILES := $(patsubst $(OVERVIEW_DIR)/%,$(DOCS_DIR)/%,${OVERVIEW_FILES:.overview.opml=.schema.md})
DOCS_SCHEMA_FILES := $(patsubst $(OVERVIEW_DIR)/%,$(DOCS_DIR)/%,${OVERVIEW_FILES:.overview.opml=.schema.json})

.PHONY:  all git-hooks venv raw json signature opml rawclean clean docs


# Rules

all: opml json docs

$(VENV_ACTIVATE): $(INSTALL_VENV_SCRIPT) Makefile
	$(INSTALL_VENV_SCRIPT) $(VENV_DIR)

venv: $(VENV_ACTIVATE)

$(GIT_HOOKS_DIR)/%: $(LOCAL_GIT_HOOKS_DIR)/%.sh Makefile $(VENV_ACTIVATE)
	. $(VENV_ACTIVATE); $(INSTALL_GIT_HOOKS_SCRIPT) "$<" "$@"

git-hooks: $(GIT_HOOKS_FILES)

raw: $(GIT_HOOKS_FILES)
	. $(VENV_ACTIVATE); python3 $(CREATE_RAW_OPML_SCRIPT) $(OVERVIEW_DIR)

signature: $(GIT_HOOKS_FILES)
	. $(VENV_ACTIVATE); python3 $(COMPUTE_SIGNATURE_SCRIPT) $(SCHEMA_FILES)
	. $(VENV_ACTIVATE); python3 $(COMPUTE_SIGNATURE_SCRIPT) $(EXAMPLE_FILES)

rawclean:
	rm -f $(OVERVIEW_RAW_FILES) $(OVERVIEW_RAW_OLD_FILES)

clean: rawclean
	rm -rf $(VENV_DIR)
	rm -f $(GIT_HOOKS_FILES)
	rm -rf $(NODE_MODULES_DIR)

opml: $(OVERVIEW_FILES)

json: $(SCHEMA_FILES) $(EXAMPLE_FILES)

$(SCHEMA_DIR)/%.schema.json: $(OVERVIEW_DIR)/%.overview.opml $(CONVERT_SCRIPT) $(COMPUTE_SIGNATURE_SCRIPT) $(GIT_HOOKS_FILES)
	. $(VENV_ACTIVATE); python3 $(CONVERT_SCRIPT) schema $(OVERVIEW_DIR)/$*.overview.opml $(SCHEMA_DIR)/$*.schema.json

$(EXAMPLE_DIR)/fairtracks_%.example.json: $(OVERVIEW_DIR)/fairtracks_%.overview.opml $(CONVERT_SCRIPT) $(COMPUTE_SIGNATURE_SCRIPT) $(GIT_HOOKS_FILES)
	. $(VENV_ACTIVATE); python3 $(CONVERT_SCRIPT) single_example $(OVERVIEW_DIR)/fairtracks_$*.overview.opml $(EXAMPLE_DIR)/fairtracks_$*.example.json

$(EXAMPLE_DIR)/fairtracks.example.json: $(OVERVIEW_FILES) $(CONVERT_SCRIPT) $(COMPUTE_SIGNATURE_SCRIPT) $(GIT_HOOKS_FILES)
	. $(VENV_ACTIVATE); python3 $(CONVERT_SCRIPT) full_example $(OVERVIEW_DIR)/fairtracks.overview.opml $(EXAMPLE_DIR)/fairtracks.example.json

$(OVERVIEW_DIR)/fairtrack%.overview.opml: $(OVERVIEW_DIR)/fairtrack%.overview.raw.opml $(CLEANUP_OPML_SCRIPT) $(GIT_HOOKS_FILES)
	. $(VENV_ACTIVATE); python3 $(CLEANUP_OPML_SCRIPT) $(OVERVIEW_DIR)/fairtrack$*.overview.raw.opml $(OVERVIEW_DIR)/fairtrack$*.overview.opml

.SECONDARY: jsonschema2md

$(JSONSCHEMA2MD_BIN_PATH): Makefile package.json package-lock.json
	npm ci

jsonschema2md: $(JSONSCHEMA2MD_BIN_PATH) $(CLEANUP_DOCS_SCRIPT) $(GIT_HOOKS_FILES)
	. $(VENV_ACTIVATE); $(JSONSCHEMA2MD_BIN_PATH) --input $(SCHEMA_DIR) --out $(DOCS_DIR) -n -p format,ontology,ancestors,namespace,matchType,foreignProperty,unique,autogenerated
	rm $(DOCS_SCHEMA_FILES)
	. $(VENV_ACTIVATE); python3 $(CLEANUP_DOCS_SCRIPT) $(DOCS_MARKDOWN_FILES)

$(DOCS_MARKDOWN_FILES): jsonschema2md $(SCHEMA_FILES) ;

docs: $(DOCS_MARKDOWN_FILES)
