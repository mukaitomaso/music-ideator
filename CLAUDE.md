# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install dependencies with all extras and dev packages
uv sync --all-extras --all-packages --group dev

# Alternative: Install specific package
uv add "mcp-agent"
```

### Code Quality
```bash
# Format code
uv run scripts/format.py

# Lint code with fixes
uv run scripts/lint.py --fix

# Run tests
uv run pytest

# Run tests with coverage
uv run coverage run -m pytest
uv run coverage xml -o coverage.xml
uv run coverage report -m --fail-under=80

# Generate HTML coverage report
uv run coverage html
```

### Schema Generation
```bash
# Generate JSON schema for configuration
uv run scripts/gen_schema.py
```

### Running Examples
```bash
# Navigate to any example directory
cd examples/basic/mcp_basic_agent

# Copy and configure secrets
cp mcp_agent.secrets.yaml.example mcp_agent.secrets.yaml

# Run the example
uv run main.py
```

## Core Architecture

### Application Structure
- **MCPApp** (`src/mcp_agent/app.py`): Central orchestrator managing global state, workflows, and MCP server connections
- **Agent** (`src/mcp_agent/agents/agent.py`): Aggregates MCP servers and provides tool access to LLMs
- **AugmentedLLM** (`src/mcp_agent/workflows/llm/augmented_llm.py`): Base class for LLMs enhanced with MCP capabilities
- **Context** (`src/mcp_agent/core/context.py`): Global state container with configuration and session management

### Workflow Patterns
All patterns are implemented as composable `AugmentedLLM` instances:

- **Orchestrator-Workers** (`src/mcp_agent/workflows/orchestrator/`): Central planner delegates tasks to specialized workers
- **Router** (`src/mcp_agent/workflows/router/`): Classifies input and routes to appropriate handlers
- **Parallel** (`src/mcp_agent/workflows/parallel/`): Fan-out to multiple LLMs with fan-in aggregation
- **Evaluator-Optimizer** (`src/mcp_agent/workflows/evaluator_optimizer/`): Iterative refinement with quality evaluation
- **Intent Classifier** (`src/mcp_agent/workflows/intent_classifier/`): Identifies user intent from input
- **Swarm** (`src/mcp_agent/workflows/swarm/`): Multi-agent orchestration pattern

### MCP Server Management
- **MCPAggregator** (`src/mcp_agent/mcp/mcp_aggregator.py`): Unified interface for multiple MCP servers with namespace management
- **MCPConnectionManager** (`src/mcp_agent/mcp/mcp_connection_manager.py`): Persistent connection management with health monitoring
- **gen_client** (`src/mcp_agent/mcp/gen_client.py`): Simple context manager for MCP server connections

### Execution Engines
- **AsyncioExecutor**: Default async execution for simple workflows
- **TemporalExecutor**: Enterprise workflow orchestration with durability and state persistence

### Configuration
- **mcp_agent.config.yaml**: Main configuration for MCP servers, execution engines, logging, and LLM providers
- **mcp_agent.secrets.yaml**: Git-ignored secrets file for API keys and sensitive data
- **JSON Schema**: Available at `schema/mcp-agent.config.schema.json`

## Key Patterns

### Agent Creation and Usage
```python
# Create agent with MCP server access
agent = Agent(
    name="agent_name",
    instruction="Agent purpose description",
    server_names=["fetch", "filesystem"]
)

# Use within async context
async with agent:
    llm = await agent.attach_llm(OpenAIAugmentedLLM)
    result = await llm.generate_str("Your prompt here")
```

### Workflow Composition
All workflows are `AugmentedLLM` instances, enabling composition:
```python
# Use one workflow as component of another
planner_llm = EvaluatorOptimizerLLM(...)
orchestrator = Orchestrator(planner=planner_llm, ...)
```

### MCP Server Configuration
Define servers in `mcp_agent.config.yaml`:
```yaml
mcp:
  servers:
    fetch:
      command: "uvx"
      args: ["mcp-server-fetch"]
    filesystem:
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
```

## Project Structure

### Core Source (`src/mcp_agent/`)
- `agents/`: Agent implementations
- `workflows/`: Workflow pattern implementations
- `mcp/`: MCP server management and client utilities
- `executor/`: Execution engine implementations
- `core/`: Core utilities and context management
- `logging/`: Event logging and progress tracking
- `tracing/`: OpenTelemetry integration

### Examples (`examples/`)
- `basic/`: Simple agent examples
- `workflows/`: Workflow pattern examples
- `usecases/`: Real-world application examples
- `model_providers/`: Provider-specific examples

### Tests (`tests/`)
- Organized by component with comprehensive test coverage
- Use `pytest` with async support

## Development Notes

- Use `uv` for dependency management
- Follow existing code patterns and conventions
- All workflows extend `AugmentedLLM` for composability
- MCP servers are managed through async context managers
- Configuration is centralized in YAML files with schema validation
- Comprehensive logging and tracing support via OpenTelemetry