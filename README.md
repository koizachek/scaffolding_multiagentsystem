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
└────────────────────┘ └───────┬──────┘ └─────────────────┘
                               │
                             (DF2)
          ┌────────────────────┴─────────────────┐
          │                   │                  │
 ┌────────▼────────┐ ┌─────-──▼──────┐ ┌─────────▼────────┐
 │    Strategic    │ │  Conceptual   │ │  Metacognitive   │
 │   Scaffolding   │ │  Scaffolding  │ │   Scaffolding    │
 └─────────────────┘ └───────────────┘ └──────────────────┘
                                                 │
                                        ┌────────▼────────┐
                                        │   Procedural    │
                                        │ Scaffolding(DF4)│
                                        └─────────────────┘
```

### Roles

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

## Research Goals

This system enables researchers to study:
- **Scaffolding Effectiveness**: Compare different types of educational scaffolding (conceptual, strategic, metacognitive, procedural)
- **Learner Adaptation**: How learners respond to personalized scaffolding based on their profiles
- **Concept Map Evolution**: Track how concept maps develop through scaffolded interactions
- **Agent-Specific Analysis**: Analyze which scaffolding agents are most effective for different learners

## Recent Updates (August 2025)

### Enhanced Experimental Environment
- **Fixed Scaffolding Sequence**: Implemented hardcoded agent order for consistent experimental conditions
  - Round 0: Baseline (no scaffolding)
  - Rounds 1-4: Fixed sequence of scaffolding agents
- **Task-Specific Configuration**: Modular scaffolding configuration system for different research domains
- **Copy Protection**: Added comprehensive copy protection for task content to prevent external assistance
- **Improved Background Assessment**: Enhanced knowledge assessment aligned with task domains

### Key Features
- **Personalized learner profiling** with adaptive scaffolding levels
- **Multi-turn conversations** (up to 5 exchanges per round)
- **Comprehensive research data logging** with agent-specific tracking
- **Interactive concept map editor** with real-time feedback
- **Protected task display** preventing content copying

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for experimental mode)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/koizachek/scaffolding_multiagentsystem.git
   cd scaffolding_multiagentsystem
   ```

2. Install dependencies:
   ```bash
   pip install -r MAS/requirements.txt
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file in the `MAS/` directory:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Running Experiments

### Launch the Web Interface

1. **Navigate to the app directory:**
   ```bash
   cd MAS/app
   ```

2. **Start the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to (for example) `http://localhost:8501`

### Experiment Flow

#### 1. Mode Selection
- **Experimental Mode**: Real AI scaffolding with data logging (requires API key)
- **Demo Mode**: Static responses for testing (no API key needed)

#### 2. Learner Profile Creation (Experimental Mode)
The system collects:
- Personal background and prior knowledge
- Confidence level in concept mapping
- Learning goals and interests
- **Automatic scaffolding level assignment** based on background knowledge

#### 3. Five-Round Experiment
Each participant completes **5 rounds** with a fixed scaffolding sequence:

**Round Structure:**
- **Round 0 (Baseline)**: Initial concept map creation without scaffolding
- **Rounds 1-4**: Scaffolding rounds with fixed agent sequence

**Each Scaffolding Round Includes:**
1. **Concept Map Building**: Interactive editor for creating/extending concept maps
2. **Agent Scaffolding**: Personalized feedback from assigned agent
3. **Multi-turn Conversation**: Up to 5 exchanges for clarification and deeper scaffolding
4. **Reflection**: Opportunity to revise concept map based on scaffolding

**Fixed Agent Sequence (Rounds 1-4):**
1. Conceptual Scaffolding Agent
2. Procedural Scaffolding Agent  
3. Strategic Scaffolding Agent
4. Metacognitive Scaffolding Agent

#### 4. Data Export
Automatic generation of research files:
- **JSON**: Complete session data (`experimental_session_[name]_[timestamp].json`)

Export Logic:
1. Real-time logging → /MAS/app/logs/ (detailed events)
2. Session completion → /MAS/experimental_data/ (research files)
3. Database export → MongoDB (structured queries)
4. Streamlit state → /MAS/app/MAS/logs/ (UI data)

## Research Data

### What Gets Logged

**Participant Data:**
- Complete learner profile responses
- Background knowledge assessment scores
- Assigned scaffolding levels

**Interaction Data:**
- **Agent-specific conversation history** (identifies which agent provided each response)
- Multi-turn conversation exchanges
- Concept map evolution across all rounds
- Response times and engagement patterns

**Performance Metrics:**
- Concept map complexity (nodes/edges)
- Learning progression indicators
- Scaffolding effectiveness measures

### Enhanced Agent Logging

The system provides detailed agent-specific tracking:

```json
{
  "conversation_history": {
    "round_0": [
      {
        "speaker": "conceptual_scaffolding",
        "agent_type": "conceptual_scaffolding",
        "message": "I notice your concept map focuses on...",
        "timestamp": "2025-08-02T19:04:57.758408"
      }
    ]
  }
}
```

This enables researchers to:
- Analyze effectiveness of each scaffolding type
- Compare response patterns across agents
- Track conversation depth by agent type
- Generate agent-specific research metrics

## Data Storage

**Experimental Data**: `MAS/experimental_data/`
- All session files are automatically saved here
- JSON format for complete data
- CSV format for statistical analysis

**System Logs**: `MAS/app/logs/`
- Technical system logs
- Error tracking and debugging information

## Interactive Concept Map Editor

### Features
- **Visual concept creation**: Click to add concepts
- **Relationship building**: Connect concepts with labeled relationships  
- **Real-time editing**: Modify labels and connections dynamically
- **Cumulative building**: Each round extends the previous map
- **Structure overview**: View node/edge counts and relationships

### Workflow
1. **Add Concepts**: Use the concept creation interface
2. **Create Connections**: Select source and target concepts, add relationship labels
3. **Edit/Delete**: Modify existing elements as needed
4. **Submit**: Save concept map and proceed to agent interaction

## System Architecture

```
MAS/
├── app/                     # Streamlit web interface
│   ├── app.py              # Main application entry point
│   ├── streamlit_experimental_session.py  # Session management
│   ├── conceptmap_component.py  # Concept map editor
│   ├── task_content.py     # Task descriptions and materials
│   ├── task_display.py     # Protected task display module
│   └── contents.json       # UI content and labels
├── config/                 # Configuration modules
│   ├── scaffolding_config.py  # Default scaffolding templates
│   └── [domain]_scaffolding_config.py  # Domain-specific configs
├── agents/                 # AI scaffolding agents
│   ├── conceptual_scaffolding_agent.py
│   ├── strategic_scaffolding_agent.py
│   ├── metacognitive_scaffolding_agent.py
│   ├── procedural_scaffolding_agent.py
│   └── agent_factory.py    # Agent creation and management
├── utils/                  # Core utilities
│   ├── openai_api.py       # AI integration
│   ├── logging_utils.py    # Research data logging
│   └── scaffolding_utils.py # Scaffolding analysis
├── examples/data/          # Reference data
│   └── expert_concept_map.json  # Expert comparison map
├── experimental_data/      # Research session data
└── config.json            # System configuration
```

## Configuration

The system uses `MAS/config.json` for configuration:

```json
{
  "max_rounds": 5,
  "agents": {
    "conceptual_scaffolding": {"enabled": true},
    "strategic_scaffolding": {"enabled": true},
    "metacognitive_scaffolding": {"enabled": true},
    "procedural_scaffolding": {"enabled": true}
  },
  "logging": {
    "log_dir": "logs",
    "log_level": "INFO"
  },
  "client": "openai",
  "primary_model": "gpt-4o",
  "fallback_model": "gpt-4o-mini"
}
```

### Task-Specific Configuration
The system supports modular task configurations through domain-specific config files in `MAS/config/`. Each configuration includes:
- Domain-specific scaffolding prompts
- Tailored assessment criteria
- Custom expert concepts
- Specialized follow-up templates

## Testing the System

Verify system functionality:

```bash
cd /path/to/scaffolding_multiagentsystem
PYTHONPATH=. python MAS/test_imports.py
```

This test:
1. Verifies all module imports
2. Instantiates the multi-agent system
3. Simulates a scaffolding interaction
4. Displays system responses

## Research Applications

### Experimental Studies
- **Scaffolding Effectiveness**: Compare agent types across participants
- **Learner Adaptation**: Study how different profiles respond to scaffolding
- **Conversation Analysis**: Analyze multi-turn scaffolding dialogues
- **Concept Map Development**: Track learning progression through map evolution

### Data Analysis
- **Agent Performance**: Which scaffolding types are most effective?
- **Learner Patterns**: How do different learners engage with scaffolding?
- **Conversation Depth**: What leads to deeper scaffolding interactions?
- **Learning Outcomes**: How do concept maps improve through scaffolding?

## Troubleshooting

### Common Issues

**API Key Problems:**
```bash
export OPENAI_API_KEY="your-key-here"
```

**Port Conflicts:**
```bash
streamlit run app.py --server.port 8502 
```

**Data Not Saving:**
- Check write permissions in MAS directory
- Verify session completion
- Look for error messages in interface

### Browser Requirements
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- JavaScript enabled
- Local storage enabled

## Dependencies

Core requirements (see `MAS/requirements.txt`):
- `streamlit` - Web interface
- `openai` - AI integration  
- `pandas` - Data processing
- `json` - Data serialization
- `datetime` - Timestamp management

## Contributing

This system is designed for educational research. To extend functionality:

1. **Add New Agents**: Create new scaffolding agent classes in `MAS/agents/`
2. **Modify Scaffolding**: Update agent behavior in individual agent files
3. **Enhance UI**: Modify Streamlit components in `MAS/app/`
4. **Extend Logging**: Add new metrics in `MAS/utils/logging_utils.py`

## License

This project is developed for higher education research on scaffolding mechanisms.

## Acknowledgments

Developed as a research prototype for studying multi-agent scaffolding effectiveness in educational settings.
