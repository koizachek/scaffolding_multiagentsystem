#!/usr/bin/env python3
"""
Test script to verify UUID resolution fix in the scaffolding system.
"""

import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test concept map with UUIDs
test_concept_map = {
    "concepts": [
        {"id": "amg", "text": "Adaptive Market Gatekeeping (AMG)"},
        {"id": "49dd8878-b257-4e55-9e36-0f116ff9d543", "text": "idea1"},
        {"id": "cf4fdf82-98b9-44b8-87ac-a41af891b178", "text": "idea2"},
        {"id": "fce7cffe-8c84-4926-a235-ca706af409a9", "text": "idea3"},
        {"id": "af1f4014-aafc-45bb-a6c2-b1724ee2c955", "text": "idea4"}
    ],
    "relationships": [
        {
            "id": "rel1",
            "source": "af1f4014-aafc-45bb-a6c2-b1724ee2c955",
            "target": "49dd8878-b257-4e55-9e36-0f116ff9d543",
            "text": "enables"
        },
        {
            "id": "rel2",
            "source": "amg",
            "target": "fce7cffe-8c84-4926-a235-ca706af409a9",
            "text": "forces"
        },
        {
            "id": "rel3",
            "source": "cf4fdf82-98b9-44b8-87ac-a41af891b178",
            "target": "amg",
            "text": "prevents"
        }
    ]
}

def test_uuid_resolution():
    """Test the UUID resolution enhancement."""
    print("Testing UUID Resolution Fix")
    print("=" * 50)
    
    # Build ID to text lookup dictionary (as done in streamlit_experimental_session.py)
    id_to_text = {}
    for concept in test_concept_map.get("concepts", []):
        concept_id = concept.get("id")
        concept_text = concept.get("text", concept.get("label", concept_id))
        if concept_id:
            id_to_text[concept_id] = concept_text
    
    print("\nID to Text Mapping:")
    for id_val, text_val in id_to_text.items():
        if '-' in id_val and len(id_val) > 30:  # UUID
            print(f"  {id_val[:8]}... → {text_val}")
        else:
            print(f"  {id_val} → {text_val}")
    
    # Enhance relationships with resolved text labels
    print("\n\nEnhanced Relationships:")
    print("-" * 50)
    enhanced_relationships = []
    for rel in test_concept_map.get("relationships", []):
        enhanced_rel = rel.copy()
        # Add resolved text labels
        enhanced_rel["source_text"] = id_to_text.get(rel.get("source"), rel.get("source"))
        enhanced_rel["target_text"] = id_to_text.get(rel.get("target"), rel.get("target"))
        enhanced_relationships.append(enhanced_rel)
        
        print(f"\nRelationship: {rel.get('id')}")
        print(f"  Original: {rel.get('source')[:8] if len(rel.get('source', '')) > 30 else rel.get('source')} → {rel.get('text')} → {rel.get('target')[:8] if len(rel.get('target', '')) > 30 else rel.get('target')}")
        print(f"  Enhanced: {enhanced_rel['source_text']} → {rel.get('text')} → {enhanced_rel['target_text']}")
    
    # Test what would be shown in prompts
    print("\n\nWhat Agents Would See in Prompts:")
    print("-" * 50)
    for rel in enhanced_relationships:
        source_label = rel.get('source_text', rel.get('source'))
        target_label = rel.get('target_text', rel.get('target'))
        relation_text = rel.get('text', 'relates to')
        print(f"  {source_label} → {relation_text} → {target_label}")
    
    print("\n✅ UUID Resolution Test Complete!")
    print("\nIf the above shows human-readable labels (idea1, idea2, etc.) instead of UUIDs,")
    print("then the fix is working correctly.")

if __name__ == "__main__":
    test_uuid_resolution()
