# UUID Resolution Fix for Multi-Agent Scaffolding System

## Problem Statement
The system was displaying UUIDs instead of human-readable text labels in:
1. Agent prompts and scaffolding responses
2. Conversation logs and experimental data
3. Research output files

### Example of the Issue
**Before Fix:**
```
"Looking at the connections you've made, such as 'amg → forces → fce7cffe-8c84-4926-a235-ca706af409a9'"
```

**After Fix:**
```
"Looking at the connections you've made, such as 'Adaptive Market Gatekeeping (AMG) → forces → idea3'"
```

## Root Cause
The concept map relationships stored source and target as UUIDs, but there was no resolution mechanism to convert these UUIDs to human-readable text labels before:
1. Passing data to AI agents
2. Logging interactions
3. Displaying in prompts

## Solution Implemented

### 1. Core Enhancement in `streamlit_experimental_session.py`
Added UUID resolution in the `get_agent_response` method:

```python
# Build ID to text lookup dictionary
id_to_text = {}
for concept in internal_format.get("concepts", []):
    concept_id = concept.get("id")
    concept_text = concept.get("text", concept.get("label", concept_id))
    if concept_id:
        id_to_text[concept_id] = concept_text

# Enhance relationships with resolved text labels
enhanced_relationships = []
for rel in internal_format.get("relationships", []):
    enhanced_rel = rel.copy()
    # Add resolved text labels
    enhanced_rel["source_text"] = id_to_text.get(rel.get("source"), rel.get("source"))
    enhanced_rel["target_text"] = id_to_text.get(rel.get("target"), rel.get("target"))
    enhanced_relationships.append(enhanced_rel)

# Update internal format with enhanced relationships
internal_format["relationships"] = enhanced_relationships
```

### 2. Supporting Enhancement in `scaffolding_utils.py`
Enhanced the `enhance_concept_map_with_labels` function to:
- Build comprehensive ID-to-text mappings
- Add `source_text` and `target_text` fields to relationships
- Preserve original IDs for traceability

### 3. AI API Enhancement in `ai_api.py`
Updated `_build_scaffolding_prompt` to:
- Use enhanced labels when available
- Fallback gracefully if labels are missing
- Detect and avoid displaying UUIDs in prompts

## Files Modified
1. `MAS/app/streamlit_experimental_session.py` - Main fix implementation
2. `MAS/utils/scaffolding_utils.py` - Supporting utilities
3. `MAS/utils/ai_api.py` - Prompt building enhancement
4. `MAS/core/scaffolding_engine.py` - Core engine updates

## Testing
Run the test script to verify the fix:
```bash
cd MAS
python test_uuid_fix.py
```

Expected output should show human-readable labels instead of UUIDs.

## Benefits
1. **Improved Readability**: Researchers can now understand logs without UUID lookups
2. **Better AI Responses**: Agents generate more meaningful scaffolding with readable concept names
3. **Enhanced Research Data**: Experimental outputs are more interpretable
4. **Maintained Traceability**: Original UUIDs are preserved alongside readable labels

## Data Structure
Enhanced relationships now include both IDs and labels:
```json
{
  "id": "rel-123",
  "source": "fce7cffe-8c84-4926-a235-ca706af409a9",
  "target": "amg",
  "text": "prevents",
  "source_text": "idea3",
  "target_text": "Adaptive Market Gatekeeping (AMG)"
}
```

## Agent Repetition Issue
The agent repetition issue was also addressed by ensuring proper conversation history tracking and avoiding duplicate response generation. The fix ensures that:
1. Each conversation turn is properly tracked
2. Previous responses are considered when generating new ones
3. The AI context includes full conversation history

## Verification
To verify the fix is working in production:
1. Run an experimental session
2. Check the generated JSON logs in `MAS/experimental_data/`
3. Look for agent responses - they should reference concept names, not UUIDs
4. Verify that agents don't repeat the same message multiple times

## Future Improvements
Consider implementing:
1. Validation to ensure all UUIDs have corresponding text labels
2. Warning logs when UUID resolution fails
3. Automatic cleanup of orphaned UUIDs
4. Enhanced concept name validation

## Rollback Instructions
If issues arise, the previous behavior can be restored by:
1. Removing the UUID resolution code block from `streamlit_experimental_session.py`
2. Reverting the `enhance_concept_map_with_labels` function in `scaffolding_utils.py`
3. Removing the label resolution logic from `ai_api.py`

---
*Fix implemented: August 25, 2025*
*Author: System Enhancement Team*
