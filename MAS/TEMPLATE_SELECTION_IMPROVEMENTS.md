# Template Selection Improvements for Scaffolding System

## Date: August 25, 2025

## Overview
Implemented an intelligent template selection system to prevent repetition and provide more context-aware scaffolding responses in the experimental environment.

## Key Problems Addressed

1. **Template Repetition**: Previously, templates were selected randomly, leading to repetitive scaffolding prompts
2. **Lack of Context Awareness**: Follow-ups didn't adapt to user response types (questions vs. statements)
3. **No Usage Tracking**: System didn't track which templates had been used in a conversation
4. **Static Follow-ups**: Follow-up templates were generic and didn't respond to user's actual content

## Implemented Solutions

### 1. Template Usage Tracking
- Added `used_template_indices` and `used_followup_indices` tracking in `ScaffoldingEngine`
- Templates are tracked per scaffolding type to prevent repetition within conversations
- System maintains conversation turn counter for context-aware selection

### 2. Intelligent Template Selection (`scaffolding_utils.py`)

#### New Functions:
- `_select_best_template_index()`: Scores templates based on:
  - Available placeholders that can be filled with actual data
  - Conversation turn (broader questions early, specific ones later)
  - Relevance to current concept map state

- `_fill_template_with_context()`: Dynamically fills placeholders with:
  - Actual concept names from the map
  - Observation about map structure
  - Node and edge counts
  - Specific relationships

- `analyze_user_response_type()`: Analyzes user responses to determine:
  - Is it a question?
  - Does it show confusion?
  - Does it contain concrete ideas?
  - What concepts are mentioned?

### 3. Response-Adaptive Follow-ups

#### Response Type Detection:
- **Questions/Confusion** → Provide another scaffolding prompt from SCAFFOLDING_PROMPT_TEMPLATES
- **Concrete Ideas** → Use SCAFFOLDING_FOLLOWUP_TEMPLATES to build on their thinking
- **Statements** → Select contextually appropriate follow-ups

#### Follow-up Selection:
- `select_appropriate_followup()`: Chooses follow-ups based on:
  - Response type (question, confusion, concrete idea)
  - Mentioned concepts
  - Scaffolding type characteristics
  - Previously used follow-ups (no repetition)

- `_generate_contextual_followup()`: Creates custom follow-ups when all templates exhausted

### 4. Enhanced ScaffoldingEngine (`scaffolding_engine.py`)

#### New Methods:
- `_generate_intelligent_follow_up()`: Replaces random follow-up selection
- `_generate_scaffolding_prompt_for_confusion()`: Provides additional scaffolding when needed
- Template tracking integrated throughout conversation flow

## Usage Flow

### When User Asks a Question or Shows Confusion:
1. System detects response type via `analyze_user_response_type()`
2. Selects another prompt from SCAFFOLDING_PROMPT_TEMPLATES (same type)
3. Ensures no repetition via usage tracking
4. Maintains scaffolding without giving direct answers

### When User Provides Concrete Ideas:
1. System recognizes concrete thinking
2. Switches to SCAFFOLDING_FOLLOWUP_TEMPLATES
3. Selects follow-ups that build on user's ideas
4. Encourages deeper exploration

## Configuration Notes

- **Intensity Levels**: Only "high" and "medium" are used (no "low" scaffolding in experiments)
- **Template Categories**:
  - Strategic: Focus on planning and organization
  - Metacognitive: Focus on self-reflection and learning awareness
  - Procedural: Focus on steps and methods
  - Conceptual: Focus on relationships and understanding

## Testing

Run `python test_template_selection.py` to verify:
- Template non-repetition across turns
- Response type analysis accuracy
- Intelligent follow-up selection
- Full engine integration

## Benefits

1. **Natural Conversation Flow**: Responses adapt to user's actual input
2. **No Repetition**: Each template used only once per conversation
3. **Context Awareness**: Templates selected based on map state and conversation progress
4. **Pedagogical Integrity**: Maintains scaffolding type characteristics while varying content
5. **Scalability**: System handles template exhaustion gracefully

## Future Enhancements

1. **Machine Learning Integration**: Use ML to predict best template based on historical effectiveness
2. **Dynamic Template Generation**: Generate new templates based on conversation context
3. **Multi-turn Memory**: Remember concepts discussed across multiple rounds
4. **Personalization**: Adapt template selection to individual learner patterns
