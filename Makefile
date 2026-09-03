SHELL := /bin/sh

ANSIBLE_LINT ?= ansible-lint
ANSIBLE_PLAYBOOK ?= ansible-playbook
ANSIBLE_CONFIG := $(CURDIR)/ansible/ansible.cfg
GO ?= go
KUSTOMIZE_VERSION ?= v5.6.0
OVERLAY_DIR ?= ../homelab-local
TARGET_HOST ?=
CONFIRM ?=
TOOLS_BIN := $(CURDIR)/.tools/$(KUSTOMIZE_VERSION)/bin
KUSTOMIZE := $(TOOLS_BIN)/kustomize
PYTHON ?= python3
YAMLLINT ?= yamllint

OVERLAY_ROOT := $(abspath $(OVERLAY_DIR))
OVERLAY_NETWORK := $(OVERLAY_ROOT)/config/network.yaml
OVERLAY_INVENTORY := $(OVERLAY_ROOT)/ansible/inventory/production/hosts.yaml
NETWORK_PLAYBOOK := ansible/playbooks/network-stage.yaml
NETWORK_RUNTIME_ARGS = \
	--inventory "$(OVERLAY_INVENTORY)" \
	--extra-vars "@$(OVERLAY_NETWORK)" \
	--extra-vars "homelab_environment_confirmation=$(CONFIRM)" \
	--extra-vars "homelab_target_confirmation=$(TARGET_HOST)" \
	--limit "$(TARGET_HOST)"

export ANSIBLE_CONFIG

.PHONY: help validate yaml ansible-syntax ansible-lint kustomize secrets public-boundary \
	overlay-check network-plan network-apply

help:
	@echo "make validate         Run every local validation"
	@echo "make yaml             Lint YAML files"
	@echo "make ansible-syntax   Check the Ansible playbook syntax"
	@echo "make ansible-lint     Lint the Ansible tree"
	@echo "make kustomize        Render the homelab Kubernetes tree"
	@echo "make secrets          Reject plaintext Kubernetes Secrets"
	@echo "make public-boundary  Reject operational data from the public tree"
	@echo "make overlay-check    Validate private overlay paths and exact target selection"
	@echo "make network-plan     Preview one confirmed host using the private overlay"
	@echo "make network-apply    Apply one confirmed host with automatic rollback armed"

validate: yaml ansible-syntax ansible-lint kustomize secrets public-boundary

yaml:
	$(YAMLLINT) .

ansible-syntax:
	$(ANSIBLE_PLAYBOOK) --syntax-check ansible/playbooks/network-stage.yaml

ansible-lint:
	$(ANSIBLE_LINT) ansible/playbooks ansible/roles ansible/inventory

kustomize: $(KUSTOMIZE)
	$(KUSTOMIZE) build kubernetes/clusters/homelab >/dev/null

$(KUSTOMIZE):
	mkdir -p $(TOOLS_BIN)
	GOBIN=$(TOOLS_BIN) $(GO) install \
		sigs.k8s.io/kustomize/kustomize/v5@$(KUSTOMIZE_VERSION)

secrets:
	$(PYTHON) -m unittest discover -s tools/tests
	$(PYTHON) tools/check_plaintext_secrets.py

public-boundary:
	$(PYTHON) tools/check_public_boundary.py

overlay-check:
	@test -n "$(strip $(OVERLAY_DIR))" || { echo "OVERLAY_DIR is required." >&2; exit 2; }
	@test -n "$(strip $(TARGET_HOST))" || { echo "TARGET_HOST is required." >&2; exit 2; }
	@test -n "$(strip $(CONFIRM))" || { echo "CONFIRM is required." >&2; exit 2; }
	@test "$(CONFIRM)" != "public-example" || { \
		echo "The public example environment cannot be confirmed." >&2; exit 2; }
	@test -f "$(OVERLAY_NETWORK)" || { \
		echo "Missing private network config: $(OVERLAY_NETWORK)" >&2; exit 2; }
	@test -f "$(OVERLAY_INVENTORY)" || { \
		echo "Missing private inventory: $(OVERLAY_INVENTORY)" >&2; exit 2; }
	@$(ANSIBLE_PLAYBOOK) $(NETWORK_RUNTIME_ARGS) $(NETWORK_PLAYBOOK) --list-hosts | \
		awk -v host="$(TARGET_HOST)" \
		'NF == 1 && $$1 == host { found = 1 } END { exit(found ? 0 : 1) }' || { \
		echo "TARGET_HOST must name exactly one host in physical_hosts." >&2; exit 2; }

network-plan: overlay-check
	$(ANSIBLE_PLAYBOOK) $(NETWORK_RUNTIME_ARGS) $(NETWORK_PLAYBOOK) --check --diff

network-apply: overlay-check
	$(ANSIBLE_PLAYBOOK) $(NETWORK_RUNTIME_ARGS) $(NETWORK_PLAYBOOK) --diff \
		--extra-vars networkd_apply=true
