# Soil Health DSS - Development Log

This document serves as a persistent history of architectural decisions, new features, and changes made to the DSS to help maintain context across future development sessions.

## August 29, 2026

### 1. Mponela 2026 Analytics Pipeline Integration
- **Objective**: Port the Mponela 2026 framework analysis from R to native Python to allow seamless backend integration.
- **Backend Scripts Created**:
  - `scripts/mponela_extraction.py`: Implemented proximity-based term extraction from PDFs using `pypdf` and `pandas`.
  - `scripts/mponela_clustering.py`: Implemented hierarchical clustering, Z-score normalization, and heatmap generation using `scipy` and `seaborn`.
- **API Updates**: Added `/analytics/mponela/extract` and `/analytics/mponela/cluster` POST endpoints to `api/logic.py` to trigger the Python models and serve the resulting heatmaps to the frontend.

### 2. Global Dual-Track Architecture (Frontend)
- **Objective**: Ensure complete isolation between the specific "Soil health - Mponela et al 2026" study metrics and the broader "Multi-Ontology (Global)" framework.
- **Implementation (`frontend/src/App.js`)**:
  - Introduced a global state `appMode` (`mponela` vs `multi`).
  - Added a global mode switcher at the top of the dashboard.
  - **Database View**: Removed the local ontology toggle. The Principle-Indicator Matrix now strictly renders either the Mponela matrix or the Multi-ontology matrix based on the global `appMode`.
  - **Analytics Engine View**: Split the UI so that Mponela mode exclusively shows the Text Extraction and Clustering model buttons, while the Global mode shows System Operations and NLP extraction.
  - **Results View**: Removed the local `activeWorkflow` toggle buttons. The `activeWorkflow` is now automatically synced with the global `appMode`. Also removed the side-by-side comparison charts, ensuring that Mponela mode only displays Mponela results, and Global mode only displays Current Ontology results.

### 3. Separation of Mponela 2026 and Mponela 2026 Update
- **Objective**: Provide clear UI separation between the original R-based Mponela 2026 results and the new Python-based Mponela 2026 Update results.
- **Implementation (`frontend/src/App.js`)**:
  - Renamed the Analytics Engine tab title to explicitly refer to "Mponela 2026 Update".
  - Added new sub-tabs inside the Results view allowing the user to toggle between "Mponela 2026" and "Mponela 2026 Update" data sources.

---
*(Add future chat session summaries, major bug fixes, or feature additions above this line)*
