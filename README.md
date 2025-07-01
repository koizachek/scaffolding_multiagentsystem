# Multi-Agent Scaffolding System for Higher Education Research

A modular, experiment-ready prototype of a multi-agent scaffolding system for higher education research. This system implements a hierarchical multi-agent architecture with a lead/orchestrator agent and specialized sub-agents, each operationalizing a specific "Design Feature" (DF) and associated scaffolding type.

## System Overview

The Multi-Agent Scaffolding System (MAS) is designed to provide scaffolded feedback on concept maps, enabling controlled experiments to test the effectiveness of different scaffolding mechanisms in educational settings. The system:

- Allows each Design Feature to be enabled/disabled individually via configuration
- Supports controlled, repeatable interaction flow for experiments
- Provides clear logging, modularity, and expandability
- Never provides direct answers or solutions - all feedback is scaffolded

## Architecture

The system is built with a hierarchical multi-agent architecture:

```
                      ┌─────────────────┐
                      │   Lead Agent    │
                      │  (Orchestrator) │
                      └────────┬────────┘
                               │
                               │
            ┌─────────────────┼──────────-───────┐
            │                 │                  │
┌──────── ──▼────────┐ ┌──────▼───────┐ ┌────────▼────────┐
│ Learner Profiling  │ │ Scaffolding  │ │   Example Map   │
│   Agent (DF1)      │ │Agents(DF1/2) │ │   Agent (DF3)   │
└────────────────────┘ └──────┬───────┘ └─────────────────┘
                              │
                            (DF2)
         ┌──────────────────┬┴┬──────────────────┐
         │                  │ │                  │
┌────────▼────────┐ ┌───────▼─▼──────┐ ┌─────────▼────────┐
│    Strategic    │ │  Conceptual   │ │  Metacognitive   │
│   Scaffolding   │ │  Scaffolding  │ │   Scaffolding    │
└─────────────────┘ └───────────────┘ └──────────────────┘
                                              │
                                     ┌────────▼────────┐
                                     │   Procedural    │
                                     │ Scaffolding(DF4)│
                                     └─────────────────┘
```

### Agent Roles

1. **Lead Agent (Orchestrator)**
   - Controls workflow, phases, user prompts, and sub-agent activation
   - Dispatches user input to active sub-agents
   - Combines sub-agent outputs for user feedback
   - Enforces user reflection/response before providing new suggestions
   - Manages agent lifecycle and feature-flag-based activation/deactivation

2. **DF1: Learner Profiling & ZPD Estimation Agent**
   - Collects learner's prior knowledge, experience, goals via targeted questions
   - Analyzes concept map submissions for completeness and conceptual gaps
   - Estimates learner's Zone of Proximal Development (ZPD)
   - Provides orchestrator with scaffolding recommendations
   - Stores and updates learner profile and ZPD estimate

3. **DF2: Specialized Scaffolding Subagents**
   - **Strategic Scaffolding Agent**: Offers structured support for planning and learning strategies
   - **Conceptual Scaffolding Agent**: Highlights key concepts and relationships, detects gaps
   - **Meta-cognitive Scaffolding Agent**: Prompts learner to plan, monitor, and self-regulate thinking
   - **Procedural Scaffolding Agent**: Guides learners in using external tools and interfaces

4. **DF3: Example Map Agent (Ideal Solution Agent)**
   - Holds domain-expert "gold standard" concept map for assigned topic
   - Compares learner's submission to ideal map without revealing it directly
   - Provides feedback highlighting divergences
   - Always prompts for further independent improvement

5. **DF4: Content Ingestion / Knowledge State Agent**
   - Continuously parses and stores learner's current concept map and uploaded materials
   - Provides context-awareness to other agents based on latest learner state
   - Enables targeted, relevant feedback by tracking changes over time

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/multi-agent-scaffolding.git
   cd multi-agent-scaffolding
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The system is configured using a JSON configuration file. By default, the system looks for `config.json` in the current directory, but you can specify a different path using the `--config` option.

### Example Configuration

```json
{
  "max_rounds": 4,
  "agents": {
    "lead": {
      "type": "lead",
      "name": "Lead Agent",
      "enabled": true
    },
    "learner_profiling": {
      "type": "learner_profiling",
      "name": "Learner Profiling Agent",
      "enabled": true
    },
    "strategic_scaffolding": {
      "type": "strategic_scaffolding",
      "name": "Strategic Scaffolding Agent",
      "enabled": true
    },
    "conceptual_scaffolding": {
      "type": "conceptual_scaffolding",
      "name": "Conceptual Scaffolding Agent",
      "enabled": true
    },
    "metacognitive_scaffolding": {
      "type": "metacognitive_scaffolding",
      "name": "Metacognitive Scaffolding Agent",
      "enabled": true
    },
    "procedural_scaffolding": {
      "type": "procedural_scaffolding",
      "name": "Procedural Scaffolding Agent",
      "enabled": true
    },
    "example_map": {
      "type": "example_map",
      "name": "Example Map Agent",
      "enabled": true
    },
    "content_ingestion": {
      "type": "content_ingestion",
      "name": "Content Ingestion Agent",
      "enabled": true
    }
  },
  "design_features": {
    "df1_learner_profiling": true,
    "df2_scaffolding": true,
    "df3_example_map": true,
    "df4_content_ingestion": true
  },
  "logging": {
    "log_dir": "logs",
    "log_level": "INFO"
  },
  "output_dir": "output"
}
```

### Enabling/Disabling Design Features

You can enable or disable individual design features using the `design_features` section of the configuration file. This allows for ablation studies to test the effectiveness of different scaffolding mechanisms.

You can also use the CLI to configure the system:

```bash
python cli.py configure --df1 disable --df2 enable --df3 enable --df4 disable
```

## Usage

The system provides a command-line interface (CLI) for interaction. Here are some common usage examples:

### Testing the System

Before using the system, you can run the comprehensive test suite to verify all components are working correctly:

```bash
cd /path/to/Scaff_MAS
PYTHONPATH=. python MAS/test_imports.py
```

This test will:
1. Verify all module imports work without circular dependencies
2. Instantiate the full multi-agent system with all 8 agents
3. Simulate a complete scaffolding interaction with a sample concept map
4. Display the scaffolding type selected, agent prompts, and system responses

### Interactive Mode

The interactive mode provides a command-line interface for interacting with the real multi-agent system:

```bash
cd /path/to/Scaff_MAS
PYTHONPATH=. python MAS/cli.py interactive
```

In interactive mode, you can use the following commands:
- `process <pdf_path>` - Process a concept map PDF
- `upload <file_path> [type] [name]` - Upload a learning material
- `respond <text>` - Respond to a scaffolding prompt
- `finalize` - Finalize the session and generate summary feedback
- `status` - Show session status
- `config` - Show current configuration
- `help` - Show help message
- `exit` - Exit interactive mode

### Processing a Concept Map

To process a concept map PDF:

```bash
cd /path/to/Scaff_MAS
PYTHONPATH=. python MAS/cli.py process path/to/concept_map.pdf
```

### Uploading Learning Materials

To upload a learning material:

```bash
cd /path/to/Scaff_MAS
PYTHONPATH=. python MAS/cli.py upload path/to/material.pdf --type pdf --name "Learning Material"
```

### Finalizing a Session

To finalize a session and generate summary feedback:

```bash
cd /path/to/Scaff_MAS
PYTHONPATH=. python MAS/cli.py finalize
```

### Running the Demo

The system includes a demo script that simulates a full session with all design features enabled:

```bash
cd /path/to/Scaff_MAS
PYTHONPATH=. python MAS/demo.py
```

The demo script:
1. Creates a sample configuration
2. Initializes the system
3. Simulates learner profile input
4. Simulates concept map submissions for multiple rounds
5. Finalizes the session and generates summary feedback

### Important Notes

- **Always use `PYTHONPATH=.`** when running commands to ensure proper module resolution
- **Run commands from the Scaff_MAS directory** to ensure relative paths work correctly
- The system uses **interactive scaffolding** by default - it will prompt for user responses and adapt based on input
- All scaffolding is **educational** - the system never provides direct answers, only guided questions and prompts

## Experiment Interaction Flow

The system implements the following iterative cycle:

1. **Concept Map Creation:** User creates/submits initial map (PDF)
2. **Agent Interaction:** 
   - Lead agent collects input
   - Active sub-agents analyze and provide scaffolded feedback
   - Learner must respond/reflect before receiving new suggestions
3. **Refinement Rounds:** Repeat steps 1-2 for four total rounds (configurable)
4. **Completion:** Final map submission and summary feedback

## Data Formats

### Input

- **User Input:** Concept maps uploaded as PDF files
- **Internal Processing:** PDFs are parsed and converted to JSON graph format:
  ```json
  {
    "nodes": ["ConceptA", "ConceptB", ...],
    "edges": [
      {"source": "ConceptA", "target": "ConceptB", "relation": "causes"},
      ...
    ]
  }
  ```

### Output

- **Feedback:** Text-based scaffolded feedback from agents
- **Visualization:** Concept maps plotted and saved as PNG/SVG after each round
- **Logs:** Comprehensive session logs in JSON format

## Logging

The system generates comprehensive logs including:
- User inputs with timestamps
- Agent outputs and feedback
- Agent internal reasoning for each sub-agent
- ZPD estimates with round/session timestamps
- Active DFs/feature toggles per session
- Agent invoked (lead or sub-agent type)

Logs are stored in the directory specified in the configuration file (default: `logs`).

## Project Structure

```
MAS/
├── agents/                  # Agent modules
│   ├── base_agent.py        # Base agent class
│   ├── lead_agent.py        # Lead/orchestrator agent
│   ├── learner_profiling_agent.py  # DF1 agent
│   ├── strategic_scaffolding_agent.py  # DF2 strategic agent
│   ├── conceptual_scaffolding_agent.py  # DF2 conceptual agent
│   ├── metacognitive_scaffolding_agent.py  # DF2 metacognitive agent
│   ├── procedural_scaffolding_agent.py  # DF2 procedural agent
│   ├── example_map_agent.py  # DF3 agent
│   ├── content_ingestion_agent.py  # DF4 agent
│   └── agent_factory.py     # Factory for creating agents
├── utils/                   # Utility modules
│   ├── pdf_parser.py        # PDF parsing utilities
│   ├── visualization.py     # Concept map visualization
│   └── logging_utils.py     # Logging utilities
├── cli.py                   # Command-line interface
├── system.py                # Main system class
├── demo.py                  # Demo script
├── config.json              # Configuration file
└── requirements.txt         # Dependencies
```

## Extending the System

The system is designed to be modular and extensible. Here are some ways to extend it:

### Adding a New Agent

1. Create a new agent class that inherits from `BaseAgent`
2. Implement the `_process_impl` method to define the agent's behavior
3. Add the agent to the `agent_factory.py` module
4. Update the configuration file to include the new agent

### Modifying Scaffolding Behavior

Each scaffolding agent has its own implementation of scaffolding behavior. To modify this behavior:

1. Locate the relevant agent module (e.g., `strategic_scaffolding_agent.py`)
2. Modify the methods that generate scaffolded feedback
3. Update the agent's reasoning and decision-making processes as needed

### Adding New Input/Output Formats

To support new input or output formats:

1. Update the `pdf_parser.py` module to support new input formats
2. Update the `visualization.py` module to support new output formats
3. Modify the relevant agent modules to handle the new formats

## Dependencies

- **PDF Parsing:** pdfplumber, PyPDF2
- **Graph Visualization:** networkx, matplotlib, graphviz
- **CLI:** argparse
- **Logging:** Python standard logging
- **OpenAI Agents SDK:** For agent orchestration and LLM integration

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project was developed as a prototype for higher education research on scaffolding mechanisms.
- Special thanks to the OpenAI team for providing the Agents SDK.
