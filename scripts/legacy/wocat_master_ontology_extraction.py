import json
import os

OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_master_ontology.json"

# Manually curated standard terms from the questionnaires (based on inspection)
WOCAT_ONTOLOGY = {
    "Practices": {
        "Agronomic Measures": [
            "Mixed cropping", "Intercropping", "Relay cropping", "Cover cropping",
            "Conservation agriculture", "Compost application", "Manure application", 
            "Mulching", "Trash lines", "Green manure", "Crop rotation",
            "Zero tillage", "Minimum tillage", "Contour tillage",
            "Breaking compacted subsoil", "Deep ripping", "Double digging",
            "Seed selection", "Seed banks", "Improved varieties"
        ],
        "Vegetative Measures": [
            "Agroforestry", "Windbreaks", "Shelterbelts", "Afforestation", "Hedges", "Live fences",
            "Grass strips", "Vegetation strips", "Fire breaks", "Selective clearing"
        ],
        "Structural Measures": [
            "Bench terraces", "Forward-sloping terraces", "Earth bunds", "Stone bunds",
            "Semi-circular bunds", "Diversion ditches", "Drainage channels",
            "Waterways", "Retention ditches", "Infiltration pits", "Micro-catchments",
            "Flood control dams", "Irrigation dams", "Sand dams", "Sand dune stabilization",
            "Gully plugs", "Check dams", "Rooftop water harvesting", "Water tanks"
        ],
        "Management Measures": [
            "Area closure", "Resting", "Controlled access", "Rotational grazing",
            "Adjusting stocking rates", "Stall feeding", "Managed fallow",
            "Integrated pest management", "Organic agriculture", "Waste management"
        ]
    },
    "Indicators": {
        "Socio-economic": [
            "Crop production", "Crop quality", "Fodder production", "Fodder quality",
            "Animal production", "Wood production", "Risk of production failure",
            "Product diversity", "Production area", "Land management efficiency",
            "Energy generation", "Farm income", "Diversity of income sources",
            "Economic disparities", "Workload"
        ],
        "Ecological - Water": [
            "Drinking water availability", "Drinking water quality", 
            "Water availability for livestock", "Irrigation water availability",
            "Water quantity", "Surface runoff", "Water drainage", 
            "Groundwater recharge", "Evaporation"
        ],
        "Ecological - Soil": [
            "Soil moisture", "Soil cover", "Soil loss", "Soil accumulation",
            "Soil crusting", "Soil compaction", "Nutrient cycling", 
            "Salinity", "Soil organic matter", "Soil acidity"
        ],
        "Ecological - Biodiversity": [
            "Vegetation cover", "Biomass", "Plant diversity", 
            "Invasive species", "Animal diversity", "Beneficial species", 
            "Habitat diversity", "Pests and diseases"
        ],
        "Sociocultural": [
            "Food security", "Self-sufficiency", "Health situation",
            "Land use rights", "Water use rights", "SLM knowledge",
            "Community institutions", "Conflict mitigation", "Social equity"
        ],
        "Climate & Disaster": [
            "Flood impacts", "Landslides", "Drought impacts", 
            "Cyclones/Rain storms", "Greenhouse gas emissions", 
            "Fire risk", "Micro-climate"
        ]
    },
    "Metrics": [
        "t/ha", "kg/ha", "mm", "m a.s.l.", "USD", "Person days", 
        "Percentage (%)", "pH", "EC (Salinity)", "Count/m2"
    ],
    "Agroecological_Mapping": {
        "1. Recycling": ["Nutrient cycling", "Waste management", "Compost application", "Manure application"],
        "2. Input Reduction": ["Expenses on inputs", "Integrated pest management", "Organic agriculture", "Green manure"],
        "3. Soil Health": ["Soil moisture", "Soil cover", "Soil loss", "Soil organic matter", "Minimum tillage", "Mulching"],
        "4. Animal Health": ["Animal production", "Water availability for livestock", "Stall feeding", "Rotational grazing"],
        "5. Biodiversity": ["Plant diversity", "Animal diversity", "Habitat diversity", "Agroforestry", "Windbreaks"],
        "6. Synergy": ["Integrated crop-livestock management", "Intercropping", "Agroforestry"],
        "7. Economic Diversification": ["Product diversity", "Diversity of income sources", "Non-wood forest production"],
        "8. Social Values": ["Food security", "Health situation", "Social equity", "Cultural opportunities"],
        "9. Connectivity": ["Community institutions", "Market orientation", "Advisory service"],
        "10. Governance": ["Land use rights", "Water use rights", "Security of tenure", "Conflict mitigation"],
        "11. Participation": ["Stakeholder involvement", "Local community involvement", "Decision-making"],
        "12. Land & Natural Resource Governance": ["Area closure", "Controlled access", "Land tenure governance"],
        "13. Fairness": ["Economic disparities", "Situation of disadvantaged groups", "Gender equality"]
    }
}

def main():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(WOCAT_ONTOLOGY, f, indent=4)
    print(f"Master WOCAT Ontology created at {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
