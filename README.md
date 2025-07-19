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
            ┌──────────────────┼─────────────────┐
            │                  │                 │
┌───────────▼────────┐ ┌───────▼──────┐ ┌────────▼────────┐
│ Learner Profiling  │ │ Scaffolding  │ │   Example Map   │
│   Agent (DF1)      │ │Agents(DF1/2) │ │   Agent (DF3)   │
└────────────────────┘ └──────┬───────┘ └─────────────────┘
                              │
                            (DF2)
         ┌───────────────────┬┴─────────────────┐
         │                  │                   │
┌────────▼────────┐ ┌───────▼───────┐ ┌─────────▼────────┐
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

<img width="1758" height="966" alt="prozess_orchestrierung" src="https://github.com/user-attachments/assets/c9ed1230-8d53-4580-ab86-28b409433f7b" />

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

The system provides multiple interfaces for different use cases:

### Interactive Experimental Session (Recommended)

For conducting real experimental studies with live user interaction:

```bash
python MAS/experimental_demo.py
```

This launches the **Interactive Experimental Platform** which:

1. **Mode Selection**: Prompts user to choose between experimental or demo mode
2. **Learner Profile Creation**: Collects user information through guided questions:
   - Name, background, prior knowledge
   - Confidence level, interests, goals
   - Automatically initializes ZPD level at "medium"
3. **Randomized Agent Sequence**: Generates unique, non-repeating order of 4 scaffolding agents:
   - Conceptual Scaffolding
   - Strategic Scaffolding  
   - Metacognitive Scaffolding
   - Procedural Scaffolding
4. **Interactive Rounds**: 4 timed rounds (7 minutes each) with 2-minute breaks
5. **Cumulative Concept Mapping**: Users build upon their concept map each round using Mermaid.js syntax
6. **Real-time OpenAI Integration**: Live scaffolding responses based on user input and concept maps
7. **Comprehensive Logging**: All interactions, timings, and data saved for research analysis

#### Setting Up API Keys

For experimental mode with OpenAI integration, set your API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

#### Data Export

The system automatically exports session data in two formats:
- **JSON**: Complete session data with metadata (`experimental_session_[name]_[timestamp].json`)
- **CSV**: Flattened data for statistical analysis (`experimental_results_[name]_[timestamp].csv`)

### Testing the System

Before using the system, run the comprehensive test suite:

```bash
cd /path/to/Scaff_MAS
PYTHONPATH=. python MAS/test_imports.py
```

This test will:
1. Verify all module imports work without circular dependencies
2. Instantiate the full multi-agent system with all 8 agents
3. Simulate a complete scaffolding interaction with a sample concept map
4. Display the scaffolding type selected, agent prompts, and system responses

### Legacy CLI Interface

The original CLI interface is still available for programmatic usage:

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

### Demo Mode

For showcasing scaffolding prompts without live user interaction:

```bash
cd /path/to/Scaff_MAS
PYTHONPATH=. python MAS/demo.py
```

**Note**: Demo mode only showcases scaffolding prompts and system capabilities. Real experimental studies require the interactive experimental session with live user input.

### Important Notes

- **Use `python MAS/experimental_demo.py`** for real experimental studies
- **Demo mode** is only for showcasing system capabilities
- **Experimental mode requires OpenAI API key** for live scaffolding responses
- **All user I/O is managed by CLINE** - no placeholder console prompts
- **Agent sequences are randomized** per participant for experimental validity
- **No sample data is loaded** - all profiles and interactions are user-driven
- **Concept maps are cumulative** - users extend their maps each round (no overwrites)

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


## Acknowledgments

- This project was developed as a prototype for higher education research on scaffolding mechanisms.
