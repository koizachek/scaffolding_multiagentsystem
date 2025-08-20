"""
Task Content for International Market Entry Study
This module contains all task descriptions, materials, and content for the AMG experiment.
"""

STUDY_TITLE = "International Market Entry of a German Software Start-up"

STUDY_INTRODUCTION = """
Thank you for participating in this study! Today, you will create a concept map – a visual representation of concepts and their relationships. You can think of a concept map like a map of cities (= concepts) connected by roads (= relationships).

**A concept map consists of:**
- **Labeled nodes:** The concepts, represented as circles
- **Labeled edges:** Arrows connecting the concepts  
- **Relationships:** Each arrow is labeled with the type of relationship

**Example:** [Market Analysis] ---enables---> [Identification of Target Markets]
"""

TASK_DESCRIPTION = """
## Task Description

This study examines the challenges a start-up must overcome when expanding internationally. Various factors play a role, and they influence each other.

**Important:** This expansion takes place under the Adaptive Market Gatekeeping (AMG) standard. The core concept you must include in your analysis is **Adaptive Market Gatekeeping (AMG)**. It was developed in 2023 by a working group of the OECD (Organisation for Economic Co-operation and Development).

### What is AMG?

Imagine you want to enter a new market with your start-up – for example, in China or the US. The already established companies in this market want to protect their position. AMG describes how these "incumbents" collectively and in real time change the rules of the game to make market entry more difficult for newcomers. The following mechanisms are included:

- **Dynamic adaptation:** Established firms monitor new start-ups and flexibly adjust their defensive strategies
- **Rule-changing:** They use their influence to alter industry standards, certification requirements, or informal market rules to their advantage
- **Network control:** They control key suppliers, distribution channels, or partner networks
- **Resource blocking:** They tie up scarce resources (e.g., skilled workers, production capacity)

### Example:
The German software start-up "Veyra" wants to enter the Japanese market. Through AMG, local competitors can:
- Introduce new technical standards that only their products meet
- Secure exclusive agreements with key distributors
- Temporarily lower prices to make market entry unprofitable for the start-up

## Your Task

Use the interface provided to create a concept map that shows how the following concepts are interconnected in the international market entry of the software start-up. Highlight how the start-up can navigate AMG.

### Available concepts to be included (with your own concrete naming):

1. Market Analysis (investigation of potential markets)
2. Target Markets (selected countries/regions for expansion)
3. Competitive Environment (situation of competitors in the target market)
4. Entry Barriers (obstacles to market entry)
5. Legal Framework (laws, regulations)
6. Start-up Resources (capital, staff, know-how)
7. Entry Strategies (paths to market):
   - Export (shipping goods from home country)
   - Joint Venture (partnership with local company)
   - Direct Investment (establishing own subsidiary)
8. Financing (available capital)
9. Marketing Strategy (how to attract customers?)
10. Success Factors (what determines success?)
11. AMG (Adaptive Market Gatekeeping – see above)

### Requirements

- Use all relevant, concrete concepts (e.g., use "Credit" as a node when talking about "Financing")
- Connect the concepts with labeled arrows. Examples of labels: influences, enables, prevents, is a prerequisite for, reinforces, reduces, etc.
- Create at least 10 connections, and more if they make sense
- Pay special attention to: How does AMG affect the other factors

### Format

You will work on this task in 5 rounds (approx. 5–10 minutes each). In each round, you can expand and refine your map.

**Tip:** Start with the obvious connections and then gradually add more complex relationships. Remember: AMG is a mechanism used by established firms – consider how it impacts the various aspects of market entry.
"""

EXTRA_MATERIALS = """
## Concepts with Descriptions

**1. Market Analysis** – The systematic process of collecting and evaluating information about potential markets. It typically covers market size, expected growth, customer demand, and relevant economic, social, and technological trends.

**2. Target Markets** – Specific countries, regions, or customer segments selected for entry after evaluating market attractiveness. These are the priority areas where the start-up intends to allocate resources and adapt its offerings.

**3. Competitive Environment** – The structure and dynamics of competitors in the target market, including the number of rivals, their relative market shares, strategies, and potential new entrants. It reflects the level of rivalry and the availability of alternatives for customers.

**4. Entry Barriers** – Structural or regulatory obstacles that make it difficult for a new firm to enter a market. Examples include high initial investment, strong brand loyalty of existing players, complex regulations, or limited distribution channels.

**5. Legal Framework** – The set of national and international laws, regulations, and standards that govern business activity in the target market. It includes commercial law, labor law, taxation, intellectual property, and industry-specific rules.

**6. Start-up Resources** – The financial, human, and knowledge-based assets that a start-up can draw upon. These include capital reserves, skilled staff, managerial expertise, technological know-how, and access to professional networks.

**7. Entry Strategies** – The strategic approaches by which a company enters a new market. Each strategy implies different levels of risk, control, and resource commitment.
   - **Export** – Entering the foreign market by shipping goods directly from the home country, with minimal local presence.
   - **Joint Venture** – Forming a cooperative arrangement with a local company to share resources, risks, and market knowledge.
   - **Direct Investment** – Establishing a wholly owned subsidiary or branch in the foreign market, allowing full control but requiring high investment.

**8. Financing** – The methods by which a start-up secures the capital required for market entry. This may involve equity financing (investors), debt financing (loans), or alternative funding sources such as venture capital or grants.

**9. Marketing Strategy** – The coordinated set of actions designed to attract, reach, and retain customers in the target market. It includes product positioning, pricing, promotion, and distribution decisions tailored to local conditions.

**10. Success Factors** – The key determinants that increase the likelihood of success in a new market. Common factors include product-market fit, adaptability to local needs, reliable partners, competitive pricing, and efficient supply chains.

**11. AMG (Adaptive Market Gatekeeping)** – A hypothetical mechanism designed to regulate and evaluate entry into new markets. It functions as a dynamic filter that adapts to contextual conditions, determining whether a firm can access or progress in a specific environment.
"""

# Initial concept map for the AMG task
INITIAL_CONCEPT_MAP = {
    "elements": [
        {
            "data": {
                "id": "amg",
                "label": "Adaptive Market Gatekeeping (AMG)",
                "x": 400,
                "y": 300
            }
        }
    ]
}

# Expert concept map for AMG task (for comparison and assessment)
EXPERT_CONCEPT_MAP = {
    "nodes": [
        "AMG", "Market Analysis", "Target Markets", "Competitive Environment",
        "Entry Barriers", "Legal Framework", "Start-up Resources", 
        "Export Strategy", "Joint Venture", "Direct Investment",
        "Financing", "Marketing Strategy", "Success Factors",
        "Dynamic Adaptation", "Rule-changing", "Network Control", "Resource Blocking"
    ],
    "edges": [
        {"source": "Market Analysis", "target": "Target Markets", "relation": "enables"},
        {"source": "AMG", "target": "Entry Barriers", "relation": "increases"},
        {"source": "Competitive Environment", "target": "AMG", "relation": "activates"},
        {"source": "AMG", "target": "Legal Framework", "relation": "influences"},
        {"source": "Start-up Resources", "target": "Entry Strategies", "relation": "determines"},
        {"source": "AMG", "target": "Network Control", "relation": "implements"},
        {"source": "Network Control", "target": "Marketing Strategy", "relation": "restricts"},
        {"source": "AMG", "target": "Resource Blocking", "relation": "utilizes"},
        {"source": "Resource Blocking", "target": "Start-up Resources", "relation": "reduces"},
        {"source": "Financing", "target": "Direct Investment", "relation": "enables"},
        {"source": "Legal Framework", "target": "Joint Venture", "relation": "regulates"},
        {"source": "AMG", "target": "Success Factors", "relation": "challenges"},
        {"source": "Dynamic Adaptation", "target": "Entry Strategies", "relation": "counters"},
        {"source": "Rule-changing", "target": "Legal Framework", "relation": "modifies"},
        {"source": "Target Markets", "target": "Marketing Strategy", "relation": "shapes"}
    ]
}
