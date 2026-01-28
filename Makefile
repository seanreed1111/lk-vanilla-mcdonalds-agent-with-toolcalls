# =============================================================================
# McDonald's Drive-Thru Agent - Makefile
# =============================================================================
# Quick Reference:
#   make run MODE=console    - Run drive-thru agent in console mode (testing)
#   make run MODE=dev        - Run drive-thru agent with LiveKit (voice testing)
#   make test                - Run all tests
#   make setup               - Install dependencies and download models
# =============================================================================

.PHONY: help run run-text setup test format lint download-files clean
.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Colors
# -----------------------------------------------------------------------------
BLUE   := \033[0;34m
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
BOLD   := \033[1m
NC     := \033[0m

# -----------------------------------------------------------------------------
# Default Variables
# -----------------------------------------------------------------------------
MODE   ?=
ARGS   ?=
SCOPE  ?= all

# =============================================================================
# HELP
# =============================================================================
help:
	@echo "$(CYAN)$(BOLD)McDonald's Drive-Thru Agent$(NC)"
	@echo ""
	@echo "$(BOLD)Most Common Commands:$(NC)"
	@echo "  $(GREEN)make run MODE=console$(NC)     Test agent in terminal (no voice)"
	@echo "  $(GREEN)make run MODE=dev$(NC)         Run agent with LiveKit (voice enabled)"
	@echo "  $(GREEN)make run-text [MODE=console]$(NC) Run agent in text-only mode (no audio)"
	@echo "  $(GREEN)make run MODE=start$(NC)       Run agent in production mode"
	@echo "  $(GREEN)make test$(NC)                 Run all tests"
	@echo ""
	@echo "$(BOLD)Setup:$(NC)"
	@echo "  $(GREEN)make setup$(NC)                Install dependencies and download models"
	@echo "  $(GREEN)make download-files$(NC)       Download required model files only"
	@echo ""
	@echo "$(BOLD)Development:$(NC)"
	@echo "  $(GREEN)make format$(NC)               Format code with ruff"
	@echo "  $(GREEN)make lint$(NC)                 Lint code with ruff"
	@echo "  $(GREEN)make test SCOPE=unit$(NC)      Run unit tests only"
	@echo "  $(GREEN)make test SCOPE=integration$(NC) Run integration tests only"
	@echo "  $(GREEN)make test ARGS=\"-k order\"$(NC) Run tests matching 'order'"
	@echo ""
	@echo "$(BOLD)Utilities:$(NC)"
	@echo "  $(GREEN)make clean$(NC)                Remove caches and generated files"

# =============================================================================
# RUN - Drive-Thru Agent Execution
# =============================================================================

run:  ## Run drive-thru agent (use MODE=console|dev|start)
	@if [ -z "$(MODE)" ]; then \
		echo "$(YELLOW)Error: MODE is required$(NC)"; \
		echo "Usage: make run MODE=[console|dev|start]"; \
		echo "  console - Test agent in terminal (no voice)"; \
		echo "  dev     - Run agent with LiveKit (voice enabled)"; \
		echo "  start   - Run agent in production mode"; \
		exit 1; \
	fi
	@case "$(MODE)" in \
		console) \
			echo "$(BLUE)Starting drive-thru agent in console mode...$(NC)"; \
			uv run python src/agent.py console; \
			echo "$(GREEN)Agent session complete$(NC)" ;; \
		dev) \
			echo "$(BLUE)Starting drive-thru agent in dev mode...$(NC)"; \
			uv run python src/agent.py dev ;; \
		start) \
			echo "$(BLUE)Starting drive-thru agent in production mode...$(NC)"; \
			uv run python src/agent.py start ;; \
		*) \
			echo "$(YELLOW)Error: Invalid MODE: $(MODE)$(NC)"; \
			echo "Valid modes: console, dev, start"; \
			exit 1 ;; \
	esac

run-text:  ## Run agent in text-only mode (use MODE=console|dev|start, default: console)
	@MODE_VALUE=$${MODE:-console}; \
	case "$$MODE_VALUE" in \
		console) \
			echo "$(BLUE)Starting drive-thru agent in text-only console mode...$(NC)"; \
			SESSION__TEXT_ONLY_MODE=true uv run python src/agent.py console; \
			echo "$(GREEN)Agent session complete$(NC)" ;; \
		dev) \
			echo "$(BLUE)Starting drive-thru agent in text-only dev mode...$(NC)"; \
			SESSION__TEXT_ONLY_MODE=true uv run python src/agent.py dev ;; \
		start) \
			echo "$(BLUE)Starting drive-thru agent in text-only production mode...$(NC)"; \
			SESSION__TEXT_ONLY_MODE=true uv run python src/agent.py start ;; \
		*) \
			echo "$(YELLOW)Error: Invalid MODE: $$MODE_VALUE$(NC)"; \
			echo "Valid modes: console (default), dev, start"; \
			exit 1 ;; \
	esac

# =============================================================================
# SETUP - Dependencies and Models
# =============================================================================

setup:  ## Install dependencies and download required models
	@echo "$(BLUE)Installing dependencies...$(NC)"
	uv sync
	@echo "$(GREEN)Dependencies installed$(NC)"
	@echo "$(BLUE)Downloading model files (VAD, turn detector)...$(NC)"
	uv run python src/agent.py download-files
	@echo "$(GREEN)Setup complete!$(NC)"

download-files:  ## Download required model files (VAD, turn detector, etc.)
	@echo "$(BLUE)Downloading model files...$(NC)"
	uv run python src/agent.py download-files
	@echo "$(GREEN)Model files downloaded$(NC)"

# =============================================================================
# TEST - Run Tests
# =============================================================================

test:  ## Run tests (use SCOPE=unit|integration|all, ARGS for pytest flags)
	@echo "$(BLUE)Running tests (SCOPE=$(SCOPE))...$(NC)"
	@case "$(SCOPE)" in \
		unit) \
			uv run pytest tests/ -m "not integration" -v $(ARGS) ;; \
		integration) \
			uv run pytest tests/ -m integration -v $(ARGS) ;; \
		all) \
			uv run pytest tests/ -v $(ARGS) ;; \
		*) \
			echo "$(YELLOW)Unknown SCOPE: $(SCOPE)$(NC)"; \
			echo "Usage: make test SCOPE=[unit|integration|all] [ARGS=\"pytest-flags\"]"; \
			exit 1 ;; \
	esac
	@echo "$(GREEN)Tests complete$(NC)"

# =============================================================================
# CODE QUALITY - Formatting and Linting
# =============================================================================

format:  ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run ruff format
	@echo "$(GREEN)Code formatted$(NC)"

lint:  ## Lint and fix code with ruff
	@echo "$(BLUE)Linting code...$(NC)"
	uv run ruff check --fix
	@echo "$(GREEN)Linting complete$(NC)"

# =============================================================================
# UTILITIES
# =============================================================================

clean:  ## Remove caches and generated files
	@echo "$(BLUE)Cleaning caches and generated files...$(NC)"
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Clean complete$(NC)"
