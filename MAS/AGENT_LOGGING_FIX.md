# Agent Logging Fix - Conversation History Enhancement

## Issue Identified

The JSON logging system was recording all agent responses with a generic `"speaker": "agent"` identifier, making it impossible to determine which specific scaffolding agent (conceptual, procedural, strategic, or metacognitive) provided each response.

### Before Fix
```json
{
  "speaker": "agent",
  "message": "Let's explore the conceptual relationships...",
  "timestamp": "2025-08-02T19:04:57.758408",
  "metadata": {...}
}
```

### After Fix
```json
{
  "speaker": "conceptual_scaffolding",
  "agent_type": "conceptual_scaffolding", 
  "message": "Let's explore the conceptual relationships...",
  "timestamp": "2025-08-02T19:04:57.758408",
  "metadata": {...}
}
```

## Solution Implemented

Modified the `add_to_conversation_history()` method in `MAS/app/streamlit_experimental_session.py` to:

1. **Detect Agent Messages**: When `speaker == "agent"`, automatically determine the specific agent type for the current round
2. **Use Specific Agent ID**: Replace generic "agent" with the actual agent type (e.g., "conceptual_scaffolding")
3. **Add Explicit Agent Type Field**: Include a separate `agent_type` field for clarity
4. **Preserve User Messages**: Keep "user" and other speaker types unchanged

## Code Changes

### Modified Method: `add_to_conversation_history()`

```python
def add_to_conversation_history(self, roundn: int, speaker: str, message: str, metadata: Optional[Dict] = None):
    """Add a message to the conversation history for a specific round."""
    if "conversation_history" not in self.session_data:
        self.session_data["conversation_history"] = {}
    
    round_key = f"round_{roundn}"
    if round_key not in self.session_data["conversation_history"]:
        self.session_data["conversation_history"][round_key] = []
    
    # If speaker is "agent", get the specific agent type for this round
    if speaker == "agent" and roundn < len(self.session_data["agent_sequence"]):
        agent_type = self.session_data["agent_sequence"][roundn]
        speaker_id = agent_type  # Use specific agent type as speaker ID
    else:
        speaker_id = speaker  # Keep "user" or other speakers as-is
    
    conversation_entry = {
        "speaker": speaker_id,  # Now includes specific agent type
        "agent_type": self.session_data["agent_sequence"][roundn] if roundn < len(self.session_data["agent_sequence"]) and speaker == "agent" else None,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    self.session_data["conversation_history"][round_key].append(conversation_entry)
```

## Research Benefits

This fix enables researchers to:

### 1. **Agent-Specific Analysis**
- Analyze effectiveness of each scaffolding agent type
- Compare response patterns across different agents
- Identify which agents generate the most user engagement

### 2. **Conversation Flow Analysis**
- Track multi-turn conversations with specific agents
- Understand how different agent types handle follow-up questions
- Analyze conversation depth by agent type

### 3. **Scaffolding Strategy Evaluation**
- Compare conceptual vs. procedural scaffolding effectiveness
- Analyze strategic vs. metacognitive agent performance
- Identify optimal agent sequences for different learner profiles

### 4. **Statistical Analysis**
- Generate agent-specific metrics for research papers
- Create visualizations showing agent usage patterns
- Perform comparative analysis across experimental conditions

## Example New JSON Structure

```json
{
  "conversation_history": {
    "round_0": [
      {
        "speaker": "procedural_scaffolding",
        "agent_type": "procedural_scaffolding",
        "message": "Let's focus on the procedural aspects...",
        "timestamp": "2025-08-02T19:04:57.758408",
        "metadata": {"conversation_turn": 0}
      },
      {
        "speaker": "user",
        "agent_type": null,
        "message": "I think the process starts with...",
        "timestamp": "2025-08-02T19:05:15.123456",
        "metadata": {"conversation_turn": 0, "final": true}
      }
    ],
    "round_1": [
      {
        "speaker": "metacognitive_scaffolding",
        "agent_type": "metacognitive_scaffolding", 
        "message": "Reflecting on your current concept map...",
        "timestamp": "2025-08-02T19:05:41.117796",
        "metadata": {"conversation_turn": 0}
      }
    ]
  }
}
```

## Backward Compatibility

- Existing JSON files remain valid
- New sessions will use the enhanced logging format
- Analysis scripts can check for the presence of `agent_type` field to handle both formats

## Testing Recommendation

Run a new experimental session to verify the fix:

1. Start a new Streamlit session
2. Complete at least 2 rounds with different agents
3. Check the exported JSON file for proper agent identification
4. Verify that conversation history shows specific agent types

## Impact

This fix transforms the logging system from basic interaction tracking to comprehensive agent-specific research data collection, enabling detailed analysis of multi-agent scaffolding effectiveness.
