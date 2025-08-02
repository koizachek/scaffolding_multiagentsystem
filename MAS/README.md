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

## Streamlit Web Interface

The Multi-Agent Scaffolding System now includes a modern web-based interface built with Streamlit, providing an intuitive graphical alternative to the CLI for conducting scaffolding experiments.

### Overview

The Streamlit interface offers:
- **User-friendly web GUI** for all experiment interactions
- **Interactive concept map editor** with visual feedback
- **Real-time AI-powered scaffolding** (experimental mode)
- **Multi-turn conversation support** with scaffolding agents
- **Comprehensive tutorial system** for concept mapping
- **Automatic data export** and session management
- **Demo mode** for testing without API requirements

### Getting Started with Streamlit

#### Prerequisites

In addition to the base system requirements, you'll need:

```bash
pip install streamlit
```

#### Launching the Web Interface

1. **Navigate to the app directory:**
   ```bash
   cd MAS/app
   ```

2. **Launch the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to the displayed URL (typically `http://localhost:8501`)

#### Environment Setup

For **Experimental Mode** with real AI scaffolding, ensure your OpenAI API key is configured:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file in the `MAS/` directory:
```
OPENAI_API_KEY=your-api-key-here
```

### Using the Web Interface

#### 1. Mode Selection

Upon launching, you'll choose between two modes:

**🔬 Experimental Mode:**
- Real OpenAI-powered scaffolding responses
- Personalized learner profiling
- Complete session logging and data export
- Research-grade experimental data collection
- Requires OpenAI API key

**🎭 Demo Mode:**
- Static demonstration responses
- No API requirements
- Quick system demonstration
- No data logging or export
- Perfect for testing and showcasing

#### 2. Learner Profile Creation (Experimental Mode Only)

The system collects comprehensive learner information through an interactive form:

- **Personal Information:** Name and background
- **Prior Knowledge:** Experience with the topic
- **Confidence Level:** Self-assessed competence
- **Learning Goals:** What you hope to achieve
- **Interests:** Related areas of interest

This profile enables personalized scaffolding throughout the experiment.

#### 3. Interactive Tutorial

Before starting the experiment, participants complete a hands-on concept mapping tutorial covering:

**Step 1: Creating Nodes (Concepts)**
- Click anywhere on the map to create a new concept
- Type the concept label and press Enter
- Practice with example concepts

**Step 2: Creating Edges (Relationships)**
- Click and hold on a node for 1 second (source turns red)
- Click another node to connect them
- Type the relationship label (e.g., "leads to", "causes")
- Practice connecting concepts meaningfully

**Step 3: Editing and Navigation**
- Double-click to edit labels
- Right-click to delete elements
- Drag nodes to reposition them
- Select multiple nodes with Shift

The tutorial can be skipped for experienced users.

#### 4. Experiment Flow

The experiment consists of **4 rounds** with randomized agent order:

**Round Structure:**
1. **Concept Map Creation/Extension**
   - Round 1: Create initial concept map
   - Rounds 2-4: Extend and refine existing map
   - Maps are cumulative (build upon previous rounds)

2. **Agent Scaffolding Interaction**
   - AI agent provides personalized feedback
   - Multi-turn conversation support (up to 5 exchanges per round)
   - Context-aware responses based on your concept map

3. **Reflection and Response**
   - Respond to agent scaffolding
   - Continue conversation for clarification
   - Finish round when ready to proceed

**Agent Types (Randomized Order):**
- **Conceptual Scaffolding:** Highlights key concepts and relationships
- **Strategic Scaffolding:** Offers planning and learning strategies
- **Metacognitive Scaffolding:** Prompts self-regulation and monitoring
- **Procedural Scaffolding:** Guides tool usage and interface navigation

#### 5. Session Completion

After all rounds:
- **Session Summary:** Review your progress and agent interactions
- **Data Export:** Automatic generation of research files (experimental mode)
- **Final Concept Map:** View your completed concept map
- **New Session Option:** Start fresh with a new participant

### Concept Map Editor

The integrated concept map editor provides essential functionality for building and modifying concept maps:

#### Current Features

**✅ Node Management:**
- **Create Nodes:** Click anywhere to add new concepts
- **Edit Labels:** Double-click on nodes to modify text
- **Delete Nodes:** Right-click to remove concepts
- **Move Nodes:** Drag to reposition (basic implementation)

**✅ Edge Management:**
- **Create Connections:** Click and hold source node, then click target
- **Label Relationships:** Add meaningful relationship descriptions
- **Edit Connections:** Double-click edges to modify labels
- **Delete Connections:** Right-click edges to remove

**✅ Visualization:**
- **Real-time Updates:** See changes immediately
- **Structure Overview:** View node and edge counts
- **Text Diagram:** ASCII-style relationship visualization
- **Cumulative Building:** Each round extends the previous map

**✅ Data Management:**
- **JSON Storage:** Structured concept map data
- **Session Persistence:** Maps saved throughout experiment
- **Export Integration:** Automatic inclusion in research data

#### Current Limitations

**❌ Advanced Features Not Yet Implemented:**
- **Zoom Controls:** Cannot zoom in/out of the map
- **Advanced Drag & Drop:** Limited repositioning capabilities
- **Reset Functionality:** No clear-all button
- **Visual Canvas:** Text-based rather than full graphical interface
- **Mouse Wheel Support:** No scroll-based navigation

#### How the Editor Works

**Basic Workflow:**
1. **Adding Concepts:** Use the "➕ Add New Concept" expander
   - Type concept name in text field
   - Click "Add Concept" button
   - Concept appears in the map structure

2. **Creating Connections:** Use the "🔗 Add New Connection" expander
   - Select source concept from dropdown
   - Select target concept from dropdown
   - Type relationship label
   - Click "Add Connection" button

3. **Viewing Structure:** The editor displays:
   - **Node List:** All concepts with labels
   - **Edge List:** All connections with relationships
   - **Text Diagram:** Visual representation of relationships

**Data Format:**
```json
{
  "elements": [
    {
      "data": {
        "id": "concept_1",
        "label": "Learning",
        "x": 200,
        "y": 150
      }
    },
    {
      "data": {
        "id": "edge_1_2",
        "source": "concept_1",
        "target": "concept_2",
        "label": "leads to"
      }
    }
  ]
}
```

### Session Data and Logging

#### Experimental Mode Data Export

The system automatically generates comprehensive research data:

**JSON Export (`experimental_session_[name]_[timestamp].json`):**
- Complete session metadata
- Learner profile information
- Round-by-round concept map evolution
- Agent interaction history
- Multi-turn conversation logs
- Timing information for each round

**CSV Export (`experimental_results_[name]_[timestamp].csv`):**
- Flattened data for statistical analysis
- Participant demographics
- Concept map metrics (node/edge counts)
- Agent sequence and timing
- Response patterns and engagement metrics

#### What Gets Logged

**Participant Data:**
- Learner profile responses
- Randomized agent sequence
- Session start/end times

**Interaction Data:**
- Concept map submissions per round
- Agent scaffolding messages
- User responses to scaffolding
- Multi-turn conversation exchanges
- Round completion times

**System Data:**
- Mode selection (experimental/demo)
- Technical metadata
- Error logs and system events

### Troubleshooting

#### Common Issues

**1. API Key Problems:**
```
Error: OpenAI API key not found
```
**Solution:** Ensure your API key is properly set:
```bash
export OPENAI_API_KEY="your-key-here"
```

**2. Streamlit Port Issues:**
```
Error: Port 8501 is already in use
```
**Solution:** Use a different port:
```bash
streamlit run app.py --server.port 8502
```

**3. Concept Map Not Updating:**
- Refresh the browser page
- Check browser console for JavaScript errors
- Ensure you're clicking "Submit Concept Map" after changes

**4. Session Data Not Saving:**
- Verify write permissions in the MAS directory
- Check that the session completed properly
- Look for error messages in the Streamlit interface

#### Browser Compatibility

**Recommended Browsers:**
- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅

**Known Issues:**
- Internet Explorer not supported
- Some mobile browsers may have limited functionality

### Comparison: CLI vs Web Interface

| Feature | CLI Interface | Web Interface |
|---------|---------------|---------------|
| **User Experience** | Command-line based | Visual, intuitive GUI |
| **Concept Map Input** | PDF upload required | Interactive editor |
| **Real-time Feedback** | Text-based | Visual + text |
| **Tutorial System** | None | Interactive tutorial |
| **Multi-turn Conversations** | Limited | Full support (5 turns) |
| **Data Export** | Manual | Automatic |
| **Setup Complexity** | Higher | Lower |
| **Research Suitability** | Advanced users | All user levels |

### Best Practices

**For Researchers:**
- Use **Experimental Mode** for data collection
- Ensure participants complete the tutorial
- Monitor session completion rates
- Regularly backup exported data files

**For Participants:**
- Complete the tutorial before starting
- Take time to build meaningful concept maps
- Engage actively with agent scaffolding
- Use multi-turn conversations for clarification

**For System Administrators:**
- Monitor API usage and costs
- Ensure adequate server resources
- Regular system updates and maintenance
- Backup configuration files

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
