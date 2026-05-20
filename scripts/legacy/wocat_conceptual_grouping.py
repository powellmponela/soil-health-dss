import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\raw_questionnaire_terms.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_conceptual_ontology.json"

PURGE_PHRASES = [
    r"^very negative", r"^very positive", r"^slightly negative", r"^slightly positive",
    r"^negative", r"^positive", r"^is ", r"^are ", r"^do ", r"^does ", r"^how ", 
    r"^what ", r"^which ", r"^who ", r"^when ", r"^why ", r"^name of", r"^level of",
    r"^if ", r"^how can", r"^state if", r"^the ", r"^to ", r"^as part of", 
    r"^assessment of", r"^its ", r"^their ", r"^all ", r"^also ", r"^and ",
    r"^choose ", r"^type of approach", r"^yes ", r"^no ", r"^none$", r"^taken$",
    r"^short term", r"^long term", r"^average annual rainfall", r"^implementing agencies",
    r"^tenure opportunities", r"^total cost", r"^usually one", r"^several answers",
    r"^data captured", r"^data stored", r"^declaration on", r"^describe", r"^defines?",
    r"^help us to improve", r"^indicate", r"^provide", r"^fill in", r"^summarize",
    r"^the next", r"^the following", r"ies in which the",
    r"weakened\s+strengthened", r"worsened\s+improved", r"yes\s+no", r"no\s+yes",
    r"^whether", r"^is a", r"^is a set of",
    r"qcat\.wocat\.net", r"^recurrent activities", r"^programme based", r"^project$",
    r"^origin and composition", r"^per technology area",
    r"^welcome to wocat", r"^you are free to", r"^were other incentives", r"^where do you turn", 
    r"refers to", r"^which file", r"^how to",
    r"^tick ", r"^only one answer", r"^one answer per question", r"^maximal",
    r"^for definitions", r"^questionnaire on", r"^refer to questions", r"^reference to",
    r"^references", r"^filename of", r"^first name", r"^last name", r"^explanation of terms",
    r"^diagnosis phase", r"^testing phase", r"^did the approach", r"^differentiate",
    r"^during the discussion", r"^main aims", r"^main categories", r"^maintain confidentiality",
    r"^may require", r"^one or a", r"^only one tick", r"^researchable issues",
    r"^introduction to the questionnaire", r"^they also provide", r"^they are commonly",
    r"^use the slm measures", r"^changes due to", r"^comments", r"^description of",
    r"^detailed description", r"^for tropics", r"^for which", r"^general comments",
    r"^has land use changed", r"^has the technology", r"^have institutions",
    r"fields do landholders have", r"date of data collection", r"^links to relevant",
    r"^list establishment", r"^list maintenance", r"^locally used name", r"^loss of bio-productive",
    r"^main motivation", r"^main purpose", r"^main types of land", r"^make sure participants",
    r"^notes on implementation", r"^number of sites", r"^parties to review", r"^please read",
    r"^questionnaire on", r"^short description", r"^specification of the", r"^specification required",
    r"^supported file", r"^table of contents", r"^technical drawing", r"^technical specifications",
    r"^technologies documented", r"^technology belongs", r"^technology copes", r"^technology or approach",
    r"^videos of the", r"^was research part",
    r"^it further provides", r"^prindex has developed", r"^natural resources are almost never",
    r"^improve access", r"^aims at", r"^available from where", r"^\d+-\d+% of all income", r"^>\s*\d+%",
    r"^was ", r"^annual budget", r"^most important factors affecting costs", r"^less than \d+%",
    r"^help identify", r"^improved ground", r"^including soils", r"^incr\.", r"^increased decreased",
    r"^increased reduced", r"^interviews with", r"^institutional arrangements", r"^institutions involved",
    r"^international organization",
    r"increased decreased", r"decreased increased", r"reduced improved", r"improved reduced",
    r"^has\b", r"^have\b", r"^had\b", r"^approach phase", r"^implementation phase",
    r"by-nc-sa", r"creativecommons", r"legalcode", r"years ago", r"^type of", r"^types of", r"^please\b",
    r"^specification required",
    r"^sensitivity of the technology", r"^slope in degrees", r"present in the community",
    r"^land use type", r"^land use before", r"^technology copes well",
    r"\d+([.,]\d+)?\s*-\s*\d+", r"[<>]\s*\d+", r"\d+\s*(ha|m a\.s\.l|mm|%|m|sites)\b",
    r"^address of", r"^approach can be", r"^approach is to be", r"^approach on the",
    r"^approach that were", r"^approach was documented", r"^assess what the potential",
    r"^background information",
    r"^contact address", r"^conditions regarding the use", r"^classification of the", r"^conditions enabling",
    r"^for other categories see", r"^give further details", r"^give name of", r"^good photos are",
    r"^includes both artificial", r"^includes the following", r"^it helps identify",
    r"^not recorded", r"^not relevant", r"^not applicable", r"^select land use", r"^select one or more",
    r"^photos of the", r"^illustrating the main", r"^many of the questions", r"^not manipulated",
    r"^on what basis", r"^per technology unit",
    r"-$", r"\s+-$", r"^capacity for long-", r"bench terraces ; forward-", r"^change , selecting",
    r"^for agricultural use only", r"^not recorded", r"^small-scale medium-scale", r"^lowest local administrative",
    r"see https", r"copes poorly", r"copes well",
    r"^fao,", r"^slm$", r"^full license terms", r"^further specification", r"^general information",
    r"^general regarding", r"^given the complexity", r"^goal of the technology", r"^identify local",
    r"^in part", r"^introduction of the", r"^jointly define", r"^photos should be", r"^potential for spread",
    r"^given the complexity", r"^flow chart", r"^source of information", r"^sources of information",
    r"aims at$", r"aims at managing$", r"^select degradation type", r"^degradation types$",
    r"excelsa", r"angustifolia", r"cunninghamii", r"indica", r"aegyptiaca", r"eucalyptus", r"acacia", r"teak",
    r"mahogany", r"pinus", r"caribaea", r"oocarpa", r"patula", r"radiata", r"macrophylla", r"grandis",
    r"ivorensis", r"superba", r"xylocapa", r"mauritiana", r"casuarina", r"equisetifolia", r"junghuhniana",
    r"cordia", r"alliadora", r"oak", r"cupressus", r"lusitanica", r"dalbergia", r"sissoo", r"gmelina",
    r"arborea", r"grevillea", r"robusta", r"hevea", r"brasiliensis", r"leucaena", r"leucocephala",
    r"mimosa", r"scabrella", r"sclerocarya", r"birrea", r"abies", r"acer", r"ailanthus", r"araucaria",
    r"azadirachta", r"balanites", r"cedrus", r"erythrina", r"fraxinus", r"haloxylon", r"juniperus",
    r"khaya", r"larix", r"picea", r"populus", r"prosopis", r"salix", r"tectona", r"terminalia", r"xylia",
    r"ziziphus", r"gmelina",
    r"^about the wocat documentation", r"aims at$", r"aims at managing$",
    r"^by whom from", r"^time of conducting"
]

GENERIC_WORDS = [
    "input", "high", "low", "total", "average", "other", "remarks", "details", 
    "yes", "no", "the", "and", "for", "their", "this", "that", "with", "from",
    "water", "land", "soil", "project", "improve", "heavy", "group", "groups",
    "good", "excess", "evaluation", "deep", "cover", "codes", "a little",
    "quality", "monitoring", "on average", "country", "date", "dates", "list",
    "exposure", "following", "collected", "collecting", "above-ground c", "natural",
    "recorded", "specified", "suitable", "unsuitable", "uncertain", "usable",
    "other stakeholders", "composition of discussion", "improved", "increased", "decreased",
    "increased production", "increased profit", "rich", "resting", "reliable", "research",
    "researchers", "regional", "national", "reduced", "legalcode", "land use type",
    "address of", "background information", "contact address", "climatic", "asses", "build",
    "capacities", "coarse", "concave", "fine", "gentle", "greatly", "ground", "hindering",
    "light", "medium", "moderate", "moderately", "opinions", "possible solutions",
    "protection", "safeguard", "situation", "voluntary", "workload", "enabling", "ability",
    "agricultural", "annual", "possible", "potential", "relative", "single", "various",
    "processes", "restriction on", "degradation"
]

CONCEPTS = {
    "Crops & Products": ["crop", "maize", "cotton", "vegetable", "wheat", "rice", "tobacco", "sorghum", "millet", "barley", "oat", "sorghum", "seed", "seedlings", "yield", "cropping", "fruits", "pome fruits", "main products"],
    "Management Practices": ["tillage", "rotation", "cropping", "forestry", "grazing", "harvesting", "planting", "fallow", "nurseries", "check dam", "terrace", "bund", "mulching", "residue", "trench", "closure", "compost", "manure", "agroforestry", "silviculture", "silvipastoral", "ripping", "subsoil", "conservation agriculture", "felling", "clearing", "stabilization", "husbandry", "application of", "cut-and-carry", "land preparation", "removal of deadwood", "shelterbelt", "establishment activities", "agronomic measures"],
    "Project Impacts & Socio-Economics": ["impact", "security", "food security", "income", "profit", "benefit", "wealth", "poverty", "economic", "social", "sociocultural", "aesthetic", "prestige", "well-being", "self-sufficiency", "access to services", "establishment costs", "financial services", "financing", "market orientation", "participation", "recreation", "risk of production failure", "services"],
    "Animal & Livestock Systems": ["animal", "livestock", "cattle", "poultry", "fish", "bee", "honey", "transhumance", "pastoralism", "grazing", "fodder", "breeds", "traction", "rabbit", "silkworm", "mules", "nomadism", "ranching", "sedentary", "semi-nomadic"],
    "Energy & Fuel": ["energy", "stove", "fuel", "generation", "wood", "power", "biomass", "fuelwood"],
    "Biophysical State & Degradation": ["soil", "texture", "depth", "acidity", "crusting", "accumulation", "erosion", "loss", "life", "fertility", "moisture", "organic matter", "siltation", "degradation", "deflation", "reduction of vegetation cover", "sheet"],
    "Water & Aquatic Systems": ["water", "aquifer", "lake", "river", "swamp", "wetland", "drainage", "runoff", "stream", "groundwater", "hydrology", "intakes", "availability", "diversion", "supply", "fetching", "irrigation", "ponds", "seashores", "sea"],
    "Governance & Institutional Development": ["institution", "strengthening", "framework", "regulations", "legal", "policy", "governance", "administration", "district", "village", "government", "coalition", "rules", "enforcement", "norms", "convention", "spaces for dialogue", "state", "land grabbing", "conflict mitigation"],
    "Land Tenure & Rights": ["tenure", "rights", "ownership", "registration", "grabbing", "selling", "land use", "cropland", "pasture", "settlements", "private", "public", "communal", "leased", "land holding", "land owned", "largest land hold", "percentage of landless", "secure"],
    "Vegetation & Biodiversity": ["tree", "forest", "grass", "variety", "biodiversity", "flora", "fauna", "seeds", "seedlings", "shrub", "bush", "evergreen", "deciduous", "dead wood", "nature conservation", "habitat diversity", "species", "breeds", "varieties"],
    "Infrastructure & Technology": ["pipes", "dams", "tanks", "buildings", "roads", "railways", "machinery", "tools", "equipment", "infrastructure", "gabion", "channels", "construction", "mines", "traffic", "compost toilet"],
    "Education & Extension": ["training", "courses", "field days", "demonstration", "visits", "learning", "extension", "capacity building", "on-the-job", "farmer-to-farmer", "schools", "awareness", "advisory", "technical support", "joint field trip", "skills"],
    "Personnel & Roles": ["specialist", "land user", "adviser", "politician", "teacher", "student", "expert", "field staff", "researcher", "authority", "leader", "landowner", "compiler", "resource person", "land holders", "employee", "characteristics", "stakeholder", "women", "youth", "men", "male headed", "individuals or groups", "mixed group", "roles"],
    "Implementation & Methodology": ["phase", "monitoring", "evaluation", "testing", "diagnosis", "survey", "site visit", "documentation", "questionnaire", "interviews", "discussions", "experiments", "adoption", "initiation", "establishment", "activities", "sustainability", "methods", "single cases", "single site", "implementation date"],
    "Social & Legal Status": ["married", "unmarried", "widowed", "elderly", "children", "literacy", "titled", "registered", "female-headed", "male-headed", "patrilineal", "inheritance", "age of land users", "civil status", "land owned", "status"],
    "Agro-Climatic Zones": ["arid", "tropics", "sub-humid", "humid", "temperate", "semi-natural", "natural", "indigenous", "climatological", "altitudinal", "zone", "annual rainfall"],
    "Climate & Natural Hazards": ["climate", "rainfall", "temperature", "season", "drought", "storm", "wind", "humidity", "flood", "landslide", "fire", "hazard", "avalanche", "cyclone", "heatwave", "cold wave", "tornado", "disaster", "sea level rise"],
    "Landscape & Topography": ["slope", "plain", "plateau", "hill", "valley", "mountain", "ridge", "landscape", "topography", "altitude", "hilly", "mountainous", "upland", "lowland", "footslope", "coastal", "protected areas", "rolling", "steep", "altitudinal zone"],
    "Incentives & Support": ["subsidies", "food-for-work", "cash", "payment", "incentive", "material support", "subsidized", "external material"],
    "Environment & Pollution": ["waste", "pollution", "emission", "carbon", "greenhouse", "biocides", "herbicides", "pesticides", "fertilizer", "nutrient", "pollution", "sanitation"]
}

def master_clean(term):
    t_low = term.lower().strip('.? ')
    
    if "breaking compacted subsoil" in t_low and "deep ripping" in t_low:
        return ["deep ripping", "subsoil compaction control"]
    if "costs of inputs needed for establishment" in t_low:
        return ["establishment costs"]
    if "date of implementation" in t_low:
        return ["implementation date"]
    if "framework in place to prevent land grabbing" in t_low:
        return ["land grabbing"]
    if "policy framework for land tenure governance" in t_low:
        return ["land tenure policy framework"]
    if "men in the group" in t_low:
        return ["men"]
    if "mitigate conflicts" in t_low:
        return ["conflict mitigation"]
    if "stakeholders can voice their opinions" in t_low:
        return ["stakeholder opinions"]
    if "managing focus group discussions" in t_low:
        return ["focus group discussions"]
    if "roles of stakeholders" in t_low:
        return ["stakeholder roles"]
    if "status in community" in t_low:
        return ["community status"]
        
    term = re.sub(r'\s+', ' ', term).strip()
    
    # GLOBAL STRIP
    noise_prefixes = [
        "time of conducting", "roles of stakeholders", "managing focus group",
        "improve", "improved", "managing", "increased", "decreased", "conducting",
        "composition of", "time of", "roles of", "many of the questions capture"
    ]
    pattern = r'^(' + '|'.join(map(re.escape, noise_prefixes)) + r')\s+'
    term = re.sub(pattern, '', term, flags=re.IGNORECASE)
    
    noise_suffixes = [
        "involved in the Approach", "in the Approach", "involved", "session", "and", "or", "for",
        "aims at", "aims at managing", "within the", "within", "in the"
    ]
    suffix_pattern = r'\s+(' + '|'.join(map(re.escape, noise_suffixes)) + r')$'
    term = re.sub(suffix_pattern, '', term, flags=re.IGNORECASE)

    if "Accepting the conditions is necessary" in term:
        return ["group discussion"]
    if "Percentage of land holders" in term:
        return ["land holders", "community"]
    if "family system" in term.lower():
        return ["family system", "patrilineal"]
    if "gender roles" in term.lower():
        return ["gender roles"]
    if "gender equality" in term.lower():
        return ["gender equality"]
    if "Status in community local authorities" in term:
        return ["local authorities", "community"]

    term = re.sub(r'\(.*?\)', '', term).strip()
    term = re.sub(r'\(.*$', '', term).strip()
    term = re.sub(r'\[.*?\]', '', term).strip()
    
    parts = re.split(r'/|\+|\s\&\s|;|\sund\s|(?<=[a-z]),\s| and | or ', term)
    cleaned_parts = []
    
    for p in parts:
        p = p.strip('.? ')
        p = re.sub(r'\s+', ' ', p).strip('. ,:; \u2026')
        p = re.sub(r'\s+(within the|within|in the|at the|for)$', '', p, flags=re.IGNORECASE)
        
        p_low = p.lower()
        if p_low.startswith('other'): continue
        is_stop = False
        for pattern in PURGE_PHRASES:
            if re.search(pattern, p_low):
                is_stop = True
                break
        if is_stop: continue
        if p_low in GENERIC_WORDS and p_low != "degradation": continue
        
        p = re.sub(r'\s*\d+\s*$', '', p)
        p = re.sub(r'(\w+)\d+\b', r'\1', p)
        
        if p and len(p) > 2:
            if ":" in p: p = p.split(":")[0].strip()
            if p and len(p) > 2:
                cleaned_parts.append(p)
                
    return cleaned_parts

def main():
    with open(r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\raw_questionnaire_terms.json", 'r', encoding='utf-8') as f:
        raw_terms = json.load(f)

    cleaned_terms = []
    for t in raw_terms:
        cleaned_terms.extend(master_clean(t))
    cleaned_terms = sorted(list(set(cleaned_terms)))
    
    priority_order = list(CONCEPTS.keys())
    
    ontology = {c: [] for c in priority_order}
    ontology["Miscellaneous Technical Terms"] = []
    
    for t in cleaned_terms:
        matched = False
        t_low = t.lower()
        for concept in priority_order:
            keywords = CONCEPTS.get(concept, [])
            if any(re.search(re.escape(kw), t_low) for kw in keywords):
                ontology[concept].append(t)
                matched = True
                break
        if not matched:
            ontology["Miscellaneous Technical Terms"].append(t)
            
    for c in ontology:
        ontology[c] = sorted(list(set(ontology[c])))
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(ontology, f, indent=4)
        
    print(f"Participation Optimization complete. {len(cleaned_terms)} terms mapped.")

if __name__ == "__main__":
    main()
