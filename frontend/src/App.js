import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Database,
  LineChart,
  PlusCircle,
  Search,
  Bell,
  User,
  Leaf,
  TrendingUp,
  Layers,
  ArrowRight,
  Settings,
  Target,
  PenTool,
  ExternalLink,
  FileText,
  MessageSquare,
  HelpCircle,
  CheckCircle2,
  XCircle,
  BookOpen,
  Book,
  Sparkles,
  ClipboardList,
  Wrench,
  Link2
} from 'lucide-react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const USE_MOCK_DATA = false; // Set to true if API is unavailable

function App() {
  const [view, setView] = useState('process');
  const [interactiveSubTab, setInteractiveSubTab] = useState('agroecology');
  const [frameworks, setFrameworks] = useState([]);
  const [regData, setRegData] = useState({
    upload_type: 'file',
    authors: '',
    date: new Date().getFullYear(),
    publisher: '',
    title: '',
    person: '',
    right_to_share: false,
    url: ''
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [frameworkSearch, setFrameworkSearch] = useState('');

  const [selectedAgro, setSelectedAgro] = useState('');
  const [selectedDesign, setSelectedDesign] = useState('');

  const [resultAgro, setResultAgro] = useState(null);
  const [resultDesign, setResultDesign] = useState(null);

  const [loading, setLoading] = useState(false);
  const [expandedPrinciple, setExpandedPrinciple] = useState(null);
  const [studySummary, setStudySummary] = useState([]);
  const [agrontologyStudySummary, setAgrontologyStudySummary] = useState([]);
  const [globalDesignSummary, setGlobalDesignSummary] = useState([]);
  const [agrontologyDesignSummary, setAgrontologyDesignSummary] = useState([]);
  const [activeWorkflow, setActiveWorkflow] = useState('mponela'); // 'mponela' or 'agrontology'
  const [studyClusters, setStudyClusters] = useState([]);
  const [studyImages, setStudyImages] = useState([
    '/results/figure2a_orientation.png',
    '/results/figure2b_evolution.png',
    '/results/figure3_heatmap.png'
  ]);
  const [generatingFigures, setGeneratingFigures] = useState(false);
  const [dbStatus, setDbStatus] = useState(null);
  const [refreshingDb, setRefreshingDb] = useState(false);
  const [providerSubTab, setProviderSubTab] = useState('register');
  const [databaseSubTab, setDatabaseSubTab] = useState('frameworks');
  const [resultsSubTab, setResultsSubTab] = useState('evaluation');
  const [nlpSubTab, setNlpSubTab] = useState('extraction');
  const [nlpClusters, setNlpClusters] = useState([]);
  const [semanticMapping, setSemanticMapping] = useState(null);
  const [appMode, setAppMode] = useState('mponela');
  const [mponelaDataSource, setMponelaDataSource] = useState('python');
  const [ontologySource, setOntologySource] = useState('multi');
  const [matrixOntologySource, setMatrixOntologySource] = useState('mponela');
  const [analyticsSubTab, setAnalyticsSubTab] = useState('extraction');
  const [mponelaExtractionLoading, setMponelaExtractionLoading] = useState(false);
  const [mponelaClusteringLoading, setMponelaClusteringLoading] = useState(false);
  const [mponelaImages, setMponelaImages] = useState(false);
  const [mponelaTermsSummary, setMponelaTermsSummary] = useState(null);
  const [termsSummaryLoading, setTermsSummaryLoading] = useState(false);

  const [nlpDendrogram, setNlpDendrogram] = useState(null);
  const [documentStats, setDocumentStats] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [suggestionForm, setSuggestionForm] = useState({
    type: 'indicator_principle',
    action: 'addition',
    target_name: '',
    parent_target: '',
    evidence_url: '',
    contact_details: ''
  });
  const [indicatorHierarchy, setIndicatorHierarchy] = useState([]);
  const [documentSearch, setDocumentSearch] = useState('');
  const [indicatorSearch, setIndicatorSearch] = useState('');
  const [selectedMatrixPrinciple, setSelectedMatrixPrinciple] = useState('1. Recycling');
  const [devResponses, setDevResponses] = useState({}); // recommendation response text by suggestion ID

  const SHARED_PRINCIPLE_ORDER = [
    "Recycling", "Input Reduction", "Soil Health", "Animal Health",
    "Biodiversity", "Synergy", "Economic Diversification",
    "Co-creation of Knowledge", "Social Values and Diets",
    "Fairness", "Connectivity", "Land and Natural Resource Governance",
    "Participation"
  ];

  useEffect(() => {
    setActiveWorkflow(appMode === 'mponela' ? 'mponela' : 'agrontology');
    setResultAgro(null);
    setResultDesign(null);
  }, [appMode]);

  const SpiderChart = ({ data, color, size = 400 }) => {
    if (!data || data.length === 0) return null;

    // Sort data to match shared order if possible
    const sortedData = [...data].sort((a, b) => {
      const idxA = SHARED_PRINCIPLE_ORDER.findIndex(p => a.principle.toLowerCase().includes(p.toLowerCase()) || p.toLowerCase().includes(a.principle.toLowerCase()));
      const idxB = SHARED_PRINCIPLE_ORDER.findIndex(p => b.principle.toLowerCase().includes(p.toLowerCase()) || p.toLowerCase().includes(b.principle.toLowerCase()));
      return (idxA === -1 ? 99 : idxA) - (idxB === -1 ? 99 : idxB);
    });

    const center = size / 2;
    const radius = (size / 2) * 0.75;
    const n = sortedData.length;
    const angleStep = (Math.PI * 2) / n;

    const getPoint = (val, i) => {
      const angle = i * angleStep - Math.PI / 2;
      const x = center + radius * val * Math.cos(angle);
      const y = center + radius * val * Math.sin(angle);
      return { x, y };
    };

    const points = sortedData.map((d, i) => getPoint(d.score, i));
    const pathData = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';

    // Axis lines and labels
    const axes = sortedData.map((d, i) => {
      const p = getPoint(1.05, i);
      const lp = getPoint(1.25, i);
      const angle = (i * angleStep - Math.PI / 2) * (180 / Math.PI);

      // Determine text anchoring based on position
      let anchor = "middle";
      if (Math.abs(lp.x - center) > 20) {
        anchor = lp.x > center ? "start" : "end";
      }

      return { p, lp, label: d.principle, anchor };
    });

    return (
      <div className="spider-chart-wrapper" style={{ width: '100%', maxWidth: size, margin: '0 auto' }}>
        <svg
          viewBox={`0 0 ${size} ${size}`}
          style={{ width: '100%', height: 'auto', overflow: 'visible' }}
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Background Circles/Rings */}
          {[0.2, 0.4, 0.6, 0.8, 1].map(r => {
            const rPoints = sortedData.map((_, i) => getPoint(r, i));
            const rPath = rPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
            return <path key={r} d={rPath} fill="none" stroke="var(--border)" strokeWidth="1" strokeDasharray="4 2" />;
          })}

          {/* Axes */}
          {axes.map((a, i) => (
            <g key={i}>
              <line x1={center} y1={center} x2={a.p.x} y2={a.p.y} stroke="var(--border)" strokeWidth="1" />
              <text
                x={a.lp.x} y={a.lp.y}
                fontSize="11"
                fontWeight="700"
                fill="var(--text-muted)"
                textAnchor={a.anchor}
                dominantBaseline="middle"
              >
                {getPrincipleDisplay(a.label).length > 16 ? getPrincipleDisplay(a.label).substring(0, 14) + '...' : getPrincipleDisplay(a.label)}
              </text>
            </g>
          ))}

          {/* Data Polygon */}
          <motion.path
            d={pathData}
            fill={color}
            fillOpacity="0.2"
            stroke={color}
            strokeWidth="3"
            strokeLinejoin="round"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          />

          {/* Data Points */}
          {points.map((p, i) => (
            <motion.circle
              key={i}
              cx={p.x} cy={p.y}
              r="4"
              fill={color}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5 + i * 0.05 }}
            />
          ))}
        </svg>
      </div>
    );
  };

  const renderAgroScores = () => {
    if (!resultAgro || resultAgro.type !== 'analysis') return null;

    const currentData = activeWorkflow === 'mponela' ? resultAgro.mponela : resultAgro.agrontology;
    if (!currentData) return <div className="no-results">No data available for this workflow.</div>;

    return (
      <div style={{ marginTop: 16 }}>
        <div className="recommendation-box" style={{ marginBottom: 16, padding: '16px 20px', borderLeftColor: activeWorkflow === 'mponela' ? 'var(--primary)' : '#8e44ad' }}>
          <div className="recommendation-header" style={{ color: activeWorkflow === 'mponela' ? 'var(--primary)' : '#8e44ad' }}>
            <Target size={22} />
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
              <h4>Strategic Objective Alignment</h4>
              <span className="source-badge" style={{ background: activeWorkflow === 'mponela' ? 'rgba(46, 204, 113, 0.1)' : 'rgba(142, 68, 173, 0.1)', color: activeWorkflow === 'mponela' ? '#27ae60' : '#8e44ad', fontSize: '0.65rem', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold', border: '1px solid' }}>
                {activeWorkflow === 'mponela' ? 'Mponela et al. 2026' : 'Current Ontology'}
              </span>
            </div>
          </div>
          <p className="recommendation-desc">
            {activeWorkflow === 'mponela' ?
              "This analysis measures the synchronization between the framework's indicators and the HLPE 13 Principles based on the 2026 Review Paper methodology." :
              "This analysis uses the Master Agroecological Ontology pipeline to extract and map indicators directly from the framework's manuscript."
            }
          </p>
          <div className="recommendation-result">
            <TrendingUp size={18} style={{ color: activeWorkflow === 'mponela' ? 'var(--primary)' : '#8e44ad', marginTop: 2 }} />
            <span>{currentData.recommendation}</span>
          </div>
        </div>
        <div className="analysis-results-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '24px', marginTop: 16 }}>
          <div className="analysis-visual">
            <SpiderChart data={currentData.scores} color={activeWorkflow === 'mponela' ? 'var(--primary)' : '#8e44ad'} size={350} />
          </div>
          <div className="analysis-details">
            <div className="stats-list" style={{ maxHeight: '420px', overflowY: 'auto', paddingRight: '10px' }}>
              {currentData.scores.map((s, i) => (
                <div key={i} className="stat-item" style={{ marginBottom: 12, paddingBottom: 6, borderBottom: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600, fontSize: '0.82rem', color: 'var(--text-dark)' }}>
                    <span>{getPrincipleDisplay(s.principle)}</span>
                    <span style={{ color: activeWorkflow === 'mponela' ? 'var(--primary)' : '#8e44ad' }}>{(s.score * 100).toFixed(0)}%</span>
                  </div>
                  <div style={{ height: 5, background: 'var(--border)', borderRadius: 2, marginTop: 4, overflow: 'hidden' }}>
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${s.score * 100}%` }}
                      transition={{ duration: 0.8, delay: i * 0.05 }}
                      style={{ height: '100%', background: activeWorkflow === 'mponela' ? 'var(--primary)' : '#8e44ad', borderRadius: 2 }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Indicators Breakdown Section */}
        <div className="indicators-breakdown" style={{ marginTop: 24, borderTop: '1px solid var(--border)', paddingTop: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <ClipboardList size={20} style={{ color: activeWorkflow === 'mponela' ? 'var(--primary)' : '#8e44ad' }} />
            <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Principle Indicators Breakdown</h4>
          </div>

          <div className="indicators-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
            {currentData.scores.map((s, i) => {
              const isExpanded = expandedPrinciple === s.principle;
              const indicators = activeWorkflow === 'mponela'
                ? (resultAgro.detailed?.find(d => {
                  const dp = d.principle.toLowerCase();
                  const sp = s.principle.toLowerCase();
                  return dp === sp || dp.includes(sp) || sp.includes(dp);
                })?.indicators || [])
                : (currentData.terms?.filter(t => {
                  const tp = t.principle.toLowerCase();
                  const sp = s.principle.toLowerCase();
                  // Handle "Land Governance" vs "Land and Natural Resource Governance"
                  return tp === sp || tp.includes("land governance") && sp.includes("land") || sp.includes(tp);
                }) || []);

              if (indicators.length === 0) return null;

              return (
                <div key={i} className={`indicator-card ${isExpanded ? 'expanded' : ''}`} style={{
                  background: 'var(--card-bg)',
                  borderRadius: 10,
                  border: `1px solid ${isExpanded ? (activeWorkflow === 'mponela' ? 'var(--primary)' : '#8e44ad') : 'var(--border)'}`,
                  padding: 12,
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }} onClick={() => setExpandedPrinciple(isExpanded ? null : s.principle)}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 8, height: 8, borderRadius: '50%', background: activeWorkflow === 'mponela' ? 'var(--primary)' : '#8e44ad' }}></div>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{getPrincipleDisplay(s.principle)}</span>
                    </div>
                    <span style={{ fontSize: '0.75rem', background: 'var(--border)', padding: '2px 6px', borderRadius: 10 }}>{indicators.length}</span>
                  </div>

                  {isExpanded && (
                    <div className="indicators-list" style={{ marginTop: 12, borderTop: '1px solid var(--border)', paddingTop: 8 }}>
                      {indicators.slice(0, 15).map((ind, idx) => (
                        <div key={idx} style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          fontSize: '0.75rem',
                          marginBottom: 4,
                          padding: '2px 0'
                        }}>
                          <span style={{ color: 'var(--text-dark)' }}>{ind.name || ind.term}</span>
                          <span style={{ fontWeight: 600, color: activeWorkflow === 'mponela' ? 'var(--primary)' : '#8e44ad' }}>
                            {activeWorkflow === 'mponela' ? `${(ind.score * 100).toFixed(0)}%` : ind.count}
                          </span>
                        </div>
                      ))}
                      {indicators.length > 15 && <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: 4 }}>+ {indicators.length - 15} more indicators</div>}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  const DESIGN_METADATA = {
    "Diagnostics": {
      fullName: "Soil-health Assessment",
      desc: "Baseline evaluation of soil physical, chemical, and biological state.",
      use: "Monitoring & issue identification.",
      align: "Soil health"
    },
    "Stewardship": {
      fullName: "Soil Management",
      desc: "Maintaining and enhancing productivity through sustainable farm practices.",
      use: "On-farm management & circularity.",
      align: "Recycling, Input reduction, Animal health"
    },
    "Safeguards": {
      fullName: "Agroecological & Ecosystem",
      desc: "Protecting broader ecosystem services and ecological resilience.",
      use: "Conservation & ecological resilience.",
      align: "Biodiversity, Synergy"
    },
    "Embedding": {
      fullName: "Integrated Landscape & Livelihood",
      desc: "Scaling soil health across landscapes and connecting to farmer livelihoods.",
      use: "Rural development & landscape planning.",
      align: "Economic diversification, Connectivity, Land and natural resource governance"
    },
    "Iterative Learning": {
      fullName: "Policy & Outcome",
      desc: "Governing the social and political frameworks through feedback cycles.",
      use: "Policy making & participatory research.",
      align: "Co-creation of knowledge, Social values and diets, Fairness, Participation"
    }
  };

  const renderDesignScores = () => {
    if (!resultDesign || resultDesign.type !== 'analysis') return null;

    const currentData = activeWorkflow === 'mponela' ? resultDesign.mponela : resultDesign.agrontology;
    if (!currentData) return <div className="no-results">No data available for this workflow.</div>;

    // Sort to find strengths/gaps
    const sortedDesign = [...currentData.design_scores].sort((a, b) => b.score - a.score);
    const topD = sortedDesign[0];
    const bottomD = sortedDesign[sortedDesign.length - 1];

    const designColor = activeWorkflow === 'mponela' ? '#ff7f00' : '#e67e22';

    return (
      <div style={{ marginTop: 24 }}>
        <div className="recommendation-box design" style={{ marginBottom: 16, padding: '16px 20px', borderLeftColor: designColor }}>
          <div className="recommendation-header" style={{ color: designColor }}>
            <PenTool size={22} />
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
              <h4>Strategic Design Objective</h4>
              <span className="source-badge" style={{ background: activeWorkflow === 'mponela' ? 'rgba(255, 127, 0, 0.1)' : 'rgba(230, 126, 34, 0.1)', color: designColor, fontSize: '0.65rem', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold', border: '1px solid' }}>
                {activeWorkflow === 'mponela' ? 'Mponela et al. 2026' : 'Current Ontology'}
              </span>
            </div>
          </div>
          <p className="recommendation-desc">
            This evaluation maps framework indicators to the 5 critical design domains of the SoilDSS Integrated Programming Cycle.
            It highlights the methodological maturity and operational balance of the selected research framework.
          </p>
          <div className="recommendation-result">
            <TrendingUp size={18} style={{ color: designColor, marginTop: 2 }} />
            <span>
              Framework architecture emphasizes <strong>{topD.principle} ({(topD.score * 100).toFixed(0)}%)</strong>.
              {bottomD.score < 0.2 ? ` Integration of ${bottomD.principle} remains an area for methodological strengthening.` : ` All design domains show balanced integration.`}
            </span>
          </div>
        </div>

        <div className="design-analysis-row-layout" style={{ marginTop: 16, display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '24px', alignItems: 'center' }}>
          <div className="analysis-visual-compact">
            <SpiderChart data={currentData.design_scores} color={designColor} size={350} />
          </div>
          <div className="analysis-details">
            <div className="stats-list">
              {currentData.design_scores.map((s, i) => (
                <div key={i} className="stat-item" style={{ marginBottom: 12, paddingBottom: 6, borderBottom: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600, fontSize: '0.82rem', color: 'var(--text-dark)' }}>
                    <span>Domain {i + 1}: {s.principle}</span>
                    <span style={{ color: designColor }}>{(s.score * 100).toFixed(0)}%</span>
                  </div>
                  <div style={{ height: 5, background: 'var(--border)', borderRadius: 2, marginTop: 4, overflow: 'hidden' }}>
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${s.score * 100}%` }}
                      transition={{ duration: 0.8, delay: i * 0.05 }}
                      style={{ height: '100%', background: designColor, borderRadius: 2 }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };


  // Fetch frameworks and DB status on mount
  useEffect(() => {
    fetchFrameworks();
    fetchDbStatus();
    fetchIndicatorHierarchy();
    fetchSuggestions();
    fetchMponelaTermsSummary();
  }, []);

  useEffect(() => {
    if (view === 'analytics' && analyticsSubTab === 'nlp' && nlpSubTab === 'extraction') {
      fetchDocumentStats();
    }
  }, [view, analyticsSubTab, nlpSubTab]);

  const PRINCIPLE_NUMBERING = {
    "Recycling": 1,
    "Input Reduction": 2,
    "Soil Health": 3,
    "Animal Health": 4,
    "Biodiversity": 5,
    "Synergy": 6,
    "Economic Diversification": 7,
    "Co-creation of Knowledge": 8,
    "Social Values and Diets": 9,
    "Fairness": 10,
    "Connectivity": 11,
    "Land and Natural Resource Governance": 12,
    "Participation": 13
  };

  const OPERATIONAL_CATEGORIES = {
    "Improving Resource Efficiency": ["Recycling", "Input Reduction"],
    "Strengthening Resilience": ["Soil Health", "Animal Health", "Biodiversity", "Synergy", "Economic Diversification"],
    "Securing Social Equity/Responsibility": ["Co-creation of Knowledge", "Social Values and Diets", "Fairness", "Connectivity", "Land and Natural Resource Governance", "Participation"]
  };

  const truncateWords = (text, limit) => {
    if (!text) return "";
    const words = text.split(' ');
    if (words.length <= limit) return text;
    return words.slice(0, limit).join(' ') + '...';
  };

  const formatFirstAuthor = (authorDate) => {
    if (!authorDate) return "";

    // Check if it already has parentheses
    const lastParen = authorDate.lastIndexOf(' (');
    if (lastParen !== -1) {
      const authorPart = authorDate.substring(0, lastParen);
      const yearPart = authorDate.substring(lastParen + 2).replace(')', '');

      let firstAuthor = authorPart.split(/[;,&]| and /)[0].trim();
      if (authorPart.includes(',') || authorPart.includes('&') || authorPart.includes(';')) {
        firstAuthor += " et al.";
      }
      return `${firstAuthor} (${yearPart})`;
    }

    // Try to handle "Author Year" (e.g., FAO 2017a)
    const words = authorDate.trim().split(' ');
    if (words.length >= 2) {
      const lastWord = words[words.length - 1];
      if (/^\d{4}/.test(lastWord)) { // Looks like a year (e.g., 2022, 2017a)
        const authorPart = words.slice(0, words.length - 1).join(' ');
        let firstAuthor = authorPart.split(/[;,&]| and /)[0].trim();
        if (authorPart.includes(',') || authorPart.includes('&') || authorPart.includes(';')) {
          firstAuthor += " et al.";
        }
        return `${firstAuthor} (${lastWord})`;
      }
    }

    return authorDate;
  };

  const getPrincipleDisplay = (p) => {
    // Check if it's a numeric ID (as seen in some data sources)
    const pNum = parseInt(p);
    if (!isNaN(pNum)) {
      const key = Object.keys(PRINCIPLE_NUMBERING).find(k => PRINCIPLE_NUMBERING[k] === pNum);
      if (key) return `${pNum}. ${key}`;
    }

    // Exact match or fuzzy match (handling case/trailing text)
    const normalizedKey = Object.keys(PRINCIPLE_NUMBERING).find(key =>
      p.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(p.toLowerCase())
    );
    if (normalizedKey) {
      return `${PRINCIPLE_NUMBERING[normalizedKey]}. ${normalizedKey}`;
    }
    return p;
  };

  const renderMponelaTermsSummaryTable = () => {
    const rows = mponelaTermsSummary?.summary || [];
    const totalStudies = mponelaTermsSummary?.total_studies || 0;

    return (
      <div className="content-card terms-summary-card" style={{ marginTop: 16 }}>
        <div className="card-title terms-summary-title">
          <div><ClipboardList size={20} /> Extracted Terms Summary by Principle</div>
          <span>{totalStudies} studies</span>
        </div>

        {termsSummaryLoading ? (
          <div className="no-results">Loading extracted terms summary...</div>
        ) : rows.length > 0 ? (
          <div className="terms-summary-table-wrap">
            <table className="terms-summary-table">
              <thead>
                <tr>
                  <th>Principle</th>
                  <th>Matches</th>
                  <th>Unique Terms</th>
                  <th>Studies</th>
                  <th>Coverage</th>
                  <th>Top Extracted Terms</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(row => (
                  <tr key={row.principle}>
                    <td className="terms-principle-cell">{getPrincipleDisplay(row.principle)}</td>
                    <td>{row.total_matches.toLocaleString()}</td>
                    <td>{row.unique_terms.toLocaleString()}</td>
                    <td>{row.studies.toLocaleString()}</td>
                    <td>{Math.round((row.coverage || 0) * 100)}%</td>
                    <td>
                      <div className="top-term-list">
                        {(row.top_terms || []).map(term => (
                          <span key={`${row.principle}-${term.term}`} className="top-term-chip">
                            {term.term} <strong>{term.count}</strong>
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-results">
            {mponelaTermsSummary?.message || 'No extracted term summary is available yet.'}
          </div>
        )}
      </div>
    );
  };

  const uniquePrinciples = [...new Set(indicatorHierarchy.map(h => h.principle))].sort((a, b) => {
    const normA = Object.keys(PRINCIPLE_NUMBERING).find(key => a.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(a.toLowerCase()));
    const normB = Object.keys(PRINCIPLE_NUMBERING).find(key => b.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(b.toLowerCase()));
    const numA = normA ? PRINCIPLE_NUMBERING[normA] : 99;
    const numB = normB ? PRINCIPLE_NUMBERING[normB] : 99;
    return numA - numB;
  });

  const fetchIndicatorHierarchy = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/ontology/mponela-hierarchy`);
      const data = res.data; // { domain: { principle: [indicators] } }

      const hierarchy = [];
      Object.entries(data).forEach(([domain, principles]) => {
        Object.entries(principles).forEach(([principle, indicators]) => {
          indicators.forEach(indicator => {
            hierarchy.push({ domain, principle, indicator });
          });
        });
      });

      setIndicatorHierarchy(hierarchy);
    } catch (err) {
      console.error('Error fetching mponela hierarchy:', err);
      // Fallback to master ontology
      try {
        const res = await axios.get(`${API_BASE_URL}/ontology/master`);
        const ontology = res.data;

        const OPERATIONAL_CATEGORIES = {
          "Improving Resource Efficiency": ["1. Recycling", "2. Input Reduction"],
          "Strengthening Resilience": ["3. Soil Health", "4. Animal Health", "5. Biodiversity", "6. Synergy", "7. Economic Diversification"],
          "Securing Social Equity/Responsibility": ["8. Co-creation of Knowledge", "9. Social Values & Diets", "10. Fairness", "11. Connectivity", "12. Land & Natural Resource Governance", "13. Participation"]
        };

        const hierarchy = [];
        Object.entries(OPERATIONAL_CATEGORIES).forEach(([domain, principles]) => {
          principles.forEach(principle => {
            const ontKey = Object.keys(ontology).find(k =>
              k.toLowerCase().includes(principle.toLowerCase()) ||
              principle.toLowerCase().includes(k.toLowerCase())
            );
            if (ontKey) {
              (ontology[ontKey] || []).forEach(indicator => {
                hierarchy.push({ domain, principle: ontKey, indicator });
              });
            }
          });
        });
        setIndicatorHierarchy(hierarchy);
      } catch (fallbackErr) {
        console.error('Fallback also failed:', fallbackErr);
      }
    }
  };

  const fetchMponelaTermsSummary = async () => {
    setTermsSummaryLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/analytics/mponela/terms-summary`);
      setMponelaTermsSummary(res.data);
    } catch (err) {
      console.error('Mponela terms summary error:', err);
      setMponelaTermsSummary({
        status: 'error',
        message: err.response?.data?.detail || 'Extracted terms summary is not available yet.',
        summary: []
      });
    } finally {
      setTermsSummaryLoading(false);
    }
  };

  const runMponelaExtraction = async () => {
    setMponelaExtractionLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/analytics/mponela/extract`);
      await fetchMponelaTermsSummary();
      alert("Mponela Extraction Complete! Results saved to CSV.");
    } catch (err) {
      console.error(err);
      alert("Extraction failed.");
    }
    setMponelaExtractionLoading(false);
  };

  const runMponelaClustering = async () => {
    setMponelaClusteringLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/analytics/mponela/cluster`);
      setMponelaImages(true);
    } catch (err) {
      console.error(err);
      alert("Clustering failed.");
    }
    setMponelaClusteringLoading(false);
  };

  const fetchSemanticMapping = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/metadata/ontology-mapping-snapshot`);
      setSemanticMapping(res.data);
    } catch (err) {
      console.error('Semantic Mapping Error:', err);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/suggestions`);
      setSuggestions(res.data);
    } catch (err) {
      console.error('Suggestions Error:', err);
    }
  };

  const fetchDbStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/db/status`);
      setDbStatus(res.data);
    } catch (err) {
      console.error('DB Status Error:', err);
    }
  };

  const refreshDb = async () => {
    setRefreshingDb(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/db/refresh`);
      await fetchDbStatus();
      await fetchFrameworks();
      alert(res.data.message || 'Database refreshed successfully.');
    } catch (err) {
      console.error('DB Refresh Error:', err);
      alert('Error refreshing database.');
    } finally {
      setRefreshingDb(false);
    }
  };

  const fetchFrameworks = async () => {
    if (USE_MOCK_DATA) {
      setFrameworks([
        { id: 1, name: 'FAO Global Soil Partnership', objective: 'Global Sustainability' },
        { id: 2, name: 'USDA-NRCS Soil Health', objective: 'Agricultural Productivity' }
      ]);
      return;
    }
    try {
      const res = await axios.get(`${API_BASE_URL}/frameworks`);
      setFrameworks(res.data);
    } catch (err) {
      console.error("API Error:", err);
    }
  };

  /* ---- Add Framework ---- */
  const handleRegister = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    Object.keys(regData).forEach(key => formData.append(key, regData[key]));
    if (selectedFile) formData.append('file', selectedFile);

    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/frameworks/register`, formData);
      alert("Framework Registered Successfully!");
      setRegData({
        upload_type: 'file',
        authors: '',
        date: new Date().getFullYear(),
        publisher: '',
        title: '',
        person: '',
        right_to_share: false,
        url: ''
      });
      setSelectedFile(null);
      fetchFrameworks();
    } catch (err) {
      console.error("Registration Error:", err);
      alert("Error registering framework.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitSuggestion = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/suggestions`, suggestionForm);
      alert("Suggestion submitted successfully!");
      setSuggestionForm({
        type: 'indicator_principle',
        action: 'addition',
        target_name: '',
        parent_target: '',
        evidence_url: '',
        contact_details: ''
      });
      fetchSuggestions();
    } catch (err) {
      console.error("Suggestion Error:", err);
      alert("Error submitting suggestion.");
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionAction = async (id, status) => {
    const responseText = devResponses[id];
    if (!responseText && status === 'disregarded') {
      alert("Please provide a response/reason for disregarding.");
      return;
    }

    try {
      await axios.patch(`${API_BASE_URL}/suggestions/${id}`, {
        status: status,
        dev_response: responseText || `Action taken: ${status}`
      });
      fetchSuggestions();
      alert(`Suggestion marked as ${status}.`);
    } catch (err) {
      console.error("Action Error:", err);
      alert("Error updating suggestion.");
    }
  };

  const runNlpClustering = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/analyse/nlp-cluster`);
      if (res.data.status === 'success') {
        setNlpClusters(res.data.framework_clusters);
        setNlpDendrogram(res.data.dendrogram);
      } else {
        alert(res.data.message || 'NLP Clustering failed.');
      }
    } catch (err) {
      console.error("NLP Cluster Error:", err);
      alert('Error connecting to NLP clustering API.');
    } finally {
      setLoading(false);
    }
  };

  const fetchDocumentStats = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/documents/stats`);
      setDocumentStats(res.data);
    } catch (err) {
      console.error("Document Stats Error:", err);
    }
  };

  /* ---- Run Clustering ---- */
  const runClustering = async () => {
    setLoading(true);
    setResultAgro(null);

    if (USE_MOCK_DATA) {
      setTimeout(() => {
        setResultAgro({
          type: 'cluster',
          clusters: [
            { group: 1, frameworks: ['FAO', 'USDA'], focus: 'Sustainability & Carbon' },
            { group: 2, frameworks: ['Cornell', 'Haney'], focus: 'Biological Activity' }
          ]
        });
        setLoading(false);
      }, 1500);
      return;
    }

    try {
      const res = await axios.get(`${API_BASE_URL}/analyse/cluster`);
      setStudyClusters(res.data);
      setResultAgro({ type: 'cluster', clusters: res.data });
      // Also trigger figure generation to keep heatmap in sync
      await axios.get(`${API_BASE_URL}/analyse/generate-figures`);
      const timestamp = new Date().getTime();
      setStudyImages(prev => prev.map(img => img.split('?')[0] + `?t=${timestamp}`));
    } catch (err) {
      console.error("Cluster Error:", err);
    } finally {
      setLoading(false);
    }
  };

  /* ---- Fetch Study Summary ---- */
  const fetchStudySummary = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/analyse/summary?source=${mponelaDataSource}`);
      setStudySummary(res.data);

      const resAgro = await axios.get(`${API_BASE_URL}/analyse/agrontology-summary`);
      setAgrontologyStudySummary(resAgro.data);

      const resDesign = await axios.get(`${API_BASE_URL}/analyse/design-summary?source=${mponelaDataSource}`);
      setGlobalDesignSummary(resDesign.data);

      const resAgroDesign = await axios.get(`${API_BASE_URL}/analyse/agrontology-design-summary`);
      setAgrontologyDesignSummary(resAgroDesign.data);
    } catch (err) {
      console.error("Summary Error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (view === 'results') {
      fetchStudySummary();
    }
  }, [mponelaDataSource]);

  const generateResearchFigures = async () => {
    setGeneratingFigures(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/analyse/generate-figures`);
      if (res.data.status === 'success') {
        const timestamp = new Date().getTime();
        setStudyImages(res.data.images.map(img => `${img}?t=${timestamp}`));
        alert("Figures generated successfully!");
      } else {
        alert("Error generating figures: " + res.data.message);
      }
    } catch (err) {
      console.error("Figure Gen Error:", err);
      alert("Error connecting to figure generation API.");
    } finally {
      setGeneratingFigures(false);
    }
  };

  /* ---- Execute Agroecology Analysis ---- */
  const handleRunAgroAnalysis = async () => {
    if (!selectedAgro) return;
    setLoading(true);
    setResultAgro(null);

    if (USE_MOCK_DATA) {
      setTimeout(() => {
        setResultAgro({
          type: 'analysis',
          framework: frameworks.find(f => String(f.id) === String(selectedAgro))?.name || 'Selected',
          scores: [
            { principle: 'Recycling', score: 0.85 },
            { principle: 'Input reduction', score: 0.72 },
            { principle: 'Soil health', score: 0.91 },
            { principle: 'Animal health', score: 0.68 },
            { principle: 'Biodiversity', score: 0.79 },
            { principle: 'Synergy', score: 0.88 },
            { principle: 'Economic diversification', score: 0.60 },
            { principle: 'Co-creation of knowledge', score: 0.75 },
            { principle: 'Social values and diets', score: 0.65 },
            { principle: 'Fairness', score: 0.80 },
            { principle: 'Connectivity', score: 0.70 },
            { principle: 'Land and natural resource governance', score: 0.85 },
            { principle: 'Participation', score: 0.90 }
          ],
          recommendation: 'Increase cover cropping to improve Soil Organic Matter.'
        });
        setLoading(false);
      }, 1200);
      return;
    }

    try {
      const res = await axios.post(`${API_BASE_URL}/evaluate`, {
        framework_id: selectedAgro,
        source: mponelaDataSource
      });

      if (res.data.status === 'success') {
        setResultAgro({
          type: 'analysis',
          framework: res.data.framework,
          mponela: res.data.mponela,
          agrontology: res.data.agrontology,
          detailed: res.data.detailed,
          // Fallbacks for direct access
          scores: activeWorkflow === 'mponela' ? res.data.mponela.scores : res.data.agrontology.scores,
          recommendation: activeWorkflow === 'mponela' ? res.data.mponela.recommendation : res.data.agrontology.recommendation
        });
      } else {
        alert(res.data.message || "Evaluation failed.");
      }
    } catch (err) {
      console.error("Eval Error:", err);
      alert("Error connecting to evaluation API.");
    } finally {
      setLoading(false);
    }
  };

  /* ---- Execute Framework Design Analysis ---- */
  const handleRunDesignAnalysis = async () => {
    if (!selectedDesign) return;
    setLoading(true);
    setResultDesign(null);

    try {
      const res = await axios.post(`${API_BASE_URL}/evaluate`, {
        framework_id: selectedDesign,
        source: mponelaDataSource
      });

      if (res.data.status === 'success') {
        setResultDesign({
          type: 'analysis',
          framework: res.data.framework,
          mponela: res.data.mponela,
          agrontology: res.data.agrontology,
          // Fallback
          scores: activeWorkflow === 'mponela' ? res.data.mponela.design_scores : res.data.agrontology.design_scores,
          recommendation: "Evaluation of design parameters complete."
        });
      } else {
        alert(res.data.message || "Design evaluation failed.");
      }
    } catch (err) {
      console.error("Design Eval Error:", err);
      alert("Error connecting to design evaluation API.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-layout">
      <main className="main-area">
        <header className="top-bar">
          <div className="brand">
            <Leaf size={28} />
            <span>SoilDSS</span>
          </div>
          <div className="top-actions">
            <div className={`connection-status ${USE_MOCK_DATA ? 'offline' : 'online'}`}>
              {USE_MOCK_DATA ? 'Mock Mode' : 'Connected to Python API'}
            </div>
            <button className="icon-btn"><Search size={18} /></button>
            <button className="icon-btn"><Settings size={18} /></button>
            <button className="icon-btn"><Bell size={18} /></button>
            <div className="avatar"><User size={18} /></div>
          </div>
        </header>

        <div style={{ display: 'flex', background: 'var(--bg-light)', padding: '10px 24px', borderBottom: '1px solid var(--border)', gap: '10px' }}>
          <button
            style={{ padding: '10px 24px', fontSize: '1.05rem', fontWeight: 700, border: 'none', background: 'var(--primary)', color: 'white', borderRadius: '8px', cursor: 'default', display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            <Book size={18} /> Soil health - Mponela et al 2026
          </button>
        </div>

        <div className="tabs-container">
          <button className={`tab-btn ${view === 'process' ? 'active' : ''}`} onClick={() => setView('process')}>
            <BookOpen size={18} /> Process
          </button>
          <button className={`tab-btn ${view === 'database' ? 'active' : ''}`} onClick={() => setView('database')}>
            <Database size={18} /> Database
          </button>
          <button className={`tab-btn ${view === 'provider' ? 'active' : ''}`} onClick={() => setView('provider')}>
            <PlusCircle size={18} /> Provider Input
          </button>
          <button className={`tab-btn ${view === 'analytics' ? 'active' : ''}`} onClick={() => setView('analytics')}>
            <Settings size={18} /> Analytics Engine
          </button>
          <button className={`tab-btn ${view === 'results' ? 'active' : ''}`} onClick={() => { setView('results'); fetchStudySummary(); runClustering(); }}>
            <TrendingUp size={18} /> Results
          </button>
          <button className={`tab-btn ${view === 'strategic' ? 'active' : ''}`} onClick={() => setView('strategic')}>
            <Sparkles size={18} /> Strategic Summary
          </button>
        </div>

        <div className="tab-content-area">
          <AnimatePresence mode="wait">
            {view === 'strategic' && (
              <motion.div key="strategic" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <div className="strategic-summary-container">
                  <div className="summary-hero-card" style={{
                    background: 'linear-gradient(135deg, #064e3b 0%, #10b981 100%)',
                    color: 'white',
                    padding: '40px',
                    borderRadius: '24px',
                    marginBottom: '32px',
                    position: 'relative',
                    overflow: 'hidden'
                  }}>
                    <div style={{ position: 'relative', zIndex: 1 }}>
                      <span className="badge" style={{ background: 'rgba(255,255,255,0.2)', border: 'none', color: 'white' }}>Executive Assessment</span>
                      <h2 style={{ fontSize: '2.4rem', margin: '16px 0', fontWeight: 700 }}>Global Research Alignment</h2>
                      <p style={{ opacity: 0.9, maxWidth: '700px', fontSize: '1.1rem' }}>
                        Strategic assessment of 64 foundational frameworks against the 13 HLPE Agroecological Principles.
                        Comparing expert reviewer baselines (Mponela et al. 2026) with automated NLP synthesis.
                      </p>
                    </div>
                    <Sparkles size={120} style={{ position: 'absolute', right: '-20px', bottom: '-20px', opacity: 0.1 }} />
                  </div>

                  <div className="stats-grid three-col" style={{ marginBottom: '32px' }}>
                    <div className="stat-card-glass">
                      <div className="metric" style={{ color: 'var(--primary)' }}>64</div>
                      <div className="metric-label">Frameworks Indexed</div>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '8px' }}>From Cornell CASH to FAO TAPE</p>
                    </div>
                    <div className="stat-card-glass">
                      <div className="metric" style={{ color: 'var(--secondary)' }}>13</div>
                      <div className="metric-label">HLPE Principles</div>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '8px' }}>Global Soil Health Standard</p>
                    </div>
                    <div className="stat-card-glass">
                      <div className="metric" style={{ color: '#f39c12' }}>37k+</div>
                      <div className="metric-label">Ontology Terms</div>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '8px' }}>High-Resolution Semantic Map</p>
                    </div>
                  </div>

                  <div className="analysis-grid-two" style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '24px' }}>
                    <div className="content-card">
                      <div className="card-title" style={{ color: 'var(--primary)', borderBottom: '1px solid var(--border)', paddingBottom: '16px', marginBottom: '20px' }}>
                        <Target size={20} /> Identified Research Gaps
                      </div>
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
                        Principles with the lowest alignment across all global frameworks. These represent critical areas for future methodological strengthening.
                      </p>

                      <div className="gap-bars">
                        {[
                          { label: 'Animal Health', val: 0.15, color: '#e74c3c' },
                          { label: 'Fairness', val: 0.22, color: '#e67e22' },
                          { label: 'Land Governance', val: 0.28, color: '#f1c40f' },
                          { label: 'Connectivity', val: 0.35, color: '#3498db' }
                        ].map((g, i) => (
                          <div key={i} style={{ marginBottom: '20px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 600 }}>
                              <span>{g.label}</span>
                              <span style={{ color: g.color }}>{(g.val * 100).toFixed(0)}% Alignment</span>
                            </div>
                            <div style={{ height: '8px', background: 'var(--border)', borderRadius: '4px', overflow: 'hidden' }}>
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${g.val * 100}%` }}
                                transition={{ duration: 1, delay: i * 0.1 }}
                                style={{ height: '100%', background: g.color }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="content-card">
                      <div className="card-title" style={{ color: 'var(--secondary)', borderBottom: '1px solid var(--border)', paddingBottom: '16px', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div><BookOpen size={20} /> Methodology Sync</div>
                        {appMode === 'mponela' && (
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', fontSize: '0.85rem' }}>
                            <button
                              onClick={() => setMponelaDataSource('r')}
                              style={{ padding: '4px 12px', borderRadius: '20px', border: '1px solid var(--primary)', background: mponelaDataSource === 'r' ? 'var(--primary)' : 'transparent', color: mponelaDataSource === 'r' ? 'white' : 'var(--primary)', cursor: 'pointer' }}
                            >
                              Mponela et al 2026
                            </button>
                            <button
                              onClick={() => setMponelaDataSource('python')}
                              style={{ padding: '4px 12px', borderRadius: '20px', border: '1px solid var(--primary)', background: mponelaDataSource === 'python' ? 'var(--primary)' : 'transparent', color: mponelaDataSource === 'python' ? 'white' : 'var(--primary)', cursor: 'pointer' }}
                            >
                              Mponela 2026-update
                            </button>
                          </div>
                        )}
                      </div>
                      {appMode === 'mponela' && (
                        <div className="workflow-sync-item">
                          <div style={{ fontWeight: 700, fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--primary)' }}>
                            <CheckCircle2 size={18} /> Mponela ({mponelaDataSource === 'r' ? 'Mponela et al 2026' : 'Mponela 2026-update'})
                          </div>
                          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                            {mponelaDataSource === 'r'
                              ? 'Manual reviewer scores established as the methodological "Ground Truth".'
                              : 'Automated extraction scores generating the matrix dynamically.'}
                          </p>
                        </div>
                      )}
                      {appMode === 'multi' && (
                        <>
                          <div className="workflow-sync-item">
                            <div style={{ fontWeight: 700, fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--secondary)' }}>
                              <Sparkles size={18} /> Agrontology (NLP)
                            </div>
                            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                              Automated semantic mapping achieving high correlation with expert baselines.
                            </p>
                          </div>
                          <div style={{
                            marginTop: '32px',
                            padding: '16px',
                            background: 'rgba(59, 130, 246, 0.05)',
                            borderRadius: '12px',
                            border: '1px dashed var(--secondary)',
                            fontSize: '0.85rem',
                            color: 'var(--secondary)',
                            fontWeight: 600,
                            textAlign: 'center'
                          }}>
                            Correlation Index: 0.88 σ
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {view === 'process' && (
              <motion.div key="process" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <div className="content-card process-card">

                  <div className="process-steps-grid">
                    <div className="step-card">
                      <div className="step-num">01</div>
                      <div className="step-icon-box"><FileText size={24} /></div>
                      <h3>Review and build a framework database</h3>
                      <p>Systematic review of existing soil health literature and registration of 64 foundational frameworks into the research repository.</p>
                    </div>
                    <div className="step-card">
                      <div className="step-num">02</div>
                      <div className="step-icon-box"><Settings size={24} /></div>
                      <h3>Natural Language Processing</h3>
                      <p>Advanced text extraction identifies indicators, themes, and methodological approaches directly from publication manuscripts.</p>
                    </div>
                    <div className="step-card">
                      <div className="step-num">03</div>
                      <div className="step-icon-box"><Target size={24} /></div>
                      <h3>Clustering and design criteria</h3>
                      <p>Hierarchical clustering with adaptive branch detection organizes indicators into 13 principles and 5 critical design domains.</p>
                    </div>
                    <div className="step-card">
                      <div className="step-num">04</div>
                      <div className="step-icon-box"><TrendingUp size={24} /></div>
                      <h3>Strategic Synthesis</h3>
                      <p>Generate radar charts, heatmaps, and evolutionary trends to visualize the framework's global alignment.</p>
                    </div>
                  </div>

                  <div className="source-publication-card">
                    <div className="source-content">
                      <div className="source-title-row">
                        <FileText size={22} className="source-icon" />
                        <span>Core Methodology Source</span>
                      </div>
                      <h3 className="pub-title">Soil-health frameworks in agri-food systems. A review</h3>
                      <p className="pub-authors">Powell Mponela, Vimbayi Grace Petrova Chimonyo, Mazvita Chiduwa, Righteous Kachali, Joyce Grevulo-Minofu, Cleopatra Kawanga, Santiago Lopez-Ridaura, Sieglinde Snapp (2026)</p>
                      <div className="pub-journal">Agronomy for Sustainable Development</div>

                      <div className="pub-summary">
                        <strong>Abstract Summary:</strong> This SoilDSS tool is built upon the systematic review and methodological design framework established in this foundational publication. The research identifies five critical domains—Diagnostics, Stewardship, Safeguards, Embedding, and Iterative Learning—that are essential for transitioning soil health monitoring into actionable agri-food system policies.
                      </div>

                      <div className="pub-actions">
                        <a href="https://doi.org/10.1007/s13593-026-01111-z" target="_blank" rel="noopener noreferrer" className="btn-publication">
                          View Published Article <ExternalLink size={14} />
                        </a>
                        <div className="doi-badge">DOI: 10.1007/s13593-026-01111-z</div>
                      </div>
                    </div>
                    <div className="source-visual">
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {view === 'database' && (
              <motion.div key="database" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <div className="subtabs-container" style={{ marginBottom: 24 }}>
                  <button className={`subtab-btn ${databaseSubTab === 'frameworks' ? 'active' : ''}`} onClick={() => setDatabaseSubTab('frameworks')}>
                    <Database size={16} /> Frameworks Registry
                  </button>
                  <button className={`subtab-btn ${databaseSubTab === 'matrix' ? 'active' : ''}`} onClick={() => setDatabaseSubTab('matrix')}>
                    <Layers size={16} /> Principle-Indicator Matrix
                  </button>
                </div>

                {databaseSubTab === 'frameworks' ? (
                  <div className="content-card">
                    <div className="card-title"><Database size={20} /> Registered Frameworks ({frameworks.length})</div>
                    <div className="search-bar-wrapper">
                      <Search size={16} className="search-icon" />
                      <input
                        className="input-field search-input"
                        type="text"
                        placeholder="Filter by title, author, or publisher…"
                        value={frameworkSearch}
                        onChange={e => setFrameworkSearch(e.target.value)}
                      />
                      {frameworkSearch && <button className="search-clear" onClick={() => setFrameworkSearch('')}>✕</button>}
                    </div>
                    <div className="framework-list-header">
                      <div className="col-id">#</div>
                      <div className="col-name">Framework Name</div>
                      <div className="col-author-year">Author-Year</div>
                      <div className="col-pub-source">Publisher and Source Link</div>
                      <div className="col-local">Local Access</div>
                    </div>
                    <div className="framework-list">
                      {frameworks.filter(f => {
                        const q = frameworkSearch.toLowerCase();
                        return (f.title || '').toLowerCase().includes(q) || (f.author_date || '').toLowerCase().includes(q) || (f.publisher || '').toLowerCase().includes(q);
                      }).map((f, idx) => (
                        <div key={f.id} className="framework-item">
                          <div className="col-id">{idx + 1}</div>
                          <div className="col-name">{f.title}</div>
                          <div className="col-author-year">{formatFirstAuthor(f.author_date)}</div>
                          <div className="col-pub-source">
                            {f.doi_url ? (
                              <a href={f.doi_url} target="_blank" rel="noopener noreferrer" className="publisher-highlight">
                                <span className="publisher-name">
                                  {(!f.publisher || f.publisher === '-') ? new URL(f.doi_url).hostname.replace('www.', '') : f.publisher}
                                </span>
                                <ExternalLink size={12} />
                              </a>
                            ) : (
                              <span className="publisher-name gray">{(!f.publisher || f.publisher === '-') ? '—' : f.publisher}</span>
                            )}
                          </div>
                          <div className="col-local">
                            {f.filename ? (
                              <a href={`${API_BASE_URL}/Frameworks/${f.filename}`} target="_blank" rel="noopener noreferrer" className="pdf-local-btn">
                                <FileText size={14} /> PDF
                              </a>
                            ) : <span className="no-file">No PDF</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="content-card">
                    <div className="card-title"><Layers size={20} /> Principle-Indicator Matrix</div>

                    {appMode === 'mponela' ? (
                      <>
                        <div className="search-bar-wrapper" style={{ display: 'flex', gap: '16px', background: 'transparent', padding: 0 }}>
                          <div style={{ position: 'relative', flex: 1, display: 'flex', alignItems: 'center' }}>
                            <Search size={16} className="search-icon" style={{ position: 'absolute', left: '16px' }} />
                            <input className="input-field search-input" style={{ width: '100%', paddingLeft: '40px' }} type="text" placeholder="Search matrix..." value={indicatorSearch} onChange={e => setIndicatorSearch(e.target.value)} />
                          </div>
                          <select
                            className="input-field select-field"
                            style={{ width: '300px' }}
                            value={selectedMatrixPrinciple}
                            onChange={e => setSelectedMatrixPrinciple(e.target.value)}
                          >
                            {uniquePrinciples.map(p => (
                              <option key={p} value={p}>{getPrincipleDisplay(p)}</option>
                            ))}
                          </select>
                        </div>
                        <div className="matrix-view">
                          {(selectedMatrixPrinciple === 'All' ? uniquePrinciples : [selectedMatrixPrinciple]).map((p, pIdx) => {
                            const indicators = indicatorHierarchy.filter(h => h.principle === p && h.indicator.toLowerCase().includes(indicatorSearch.toLowerCase()));
                            if (indicators.length === 0 && indicatorSearch) return null;

                            return (
                              <div key={pIdx} className="matrix-principle-section">
                                <div className="matrix-principle-header">
                                  <span>{getPrincipleDisplay(p)}</span>
                                  <span className="matrix-count-badge">{indicators.length} {indicators.length === 1 ? 'Indicator' : 'Indicators'}</span>
                                </div>
                                <div className="matrix-indicator-grid">
                                  {indicators.map((h, iIdx) => (
                                    <div key={iIdx} className="matrix-indicator-tag">
                                      <Layers size={14} style={{ opacity: 0.5 }} /> {h.indicator}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            );
                          })}
                          {indicatorSearch && uniquePrinciples.every(p => indicatorHierarchy.filter(h => h.principle === p && h.indicator.toLowerCase().includes(indicatorSearch.toLowerCase())).length === 0) && (
                            <div className="no-results">No indicators match your search.</div>
                          )}
                        </div>
                      </>
                    ) : (
                      <>
                        {semanticMapping ? (
                          <div className="matrix-view">
                            {Object.entries(semanticMapping).map(([principle, terms], pIdx) => (
                              <div key={pIdx} className="matrix-principle-section">
                                <div className="matrix-principle-header">
                                  <span>{principle}</span>
                                  <span className="matrix-count-badge">{terms.length} {terms.length === 1 ? 'Term' : 'Terms'}</span>
                                </div>
                                <div className="matrix-indicator-grid">
                                  {terms.map((term, tIdx) => (
                                    <a key={tIdx} href={term.uri} target="_blank" rel="noopener noreferrer" className="matrix-indicator-tag" style={{ textDecoration: 'none', color: 'inherit' }} title={term.uri}>
                                      <Layers size={14} style={{ opacity: 0.5 }} /> {term.label}
                                    </a>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="no-results">Loading multi-ontology mappings...</div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </motion.div>
            )}

            {view === 'provider' && (
              <motion.div key="provider" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <div className="subtabs-container" style={{ marginBottom: 24 }}>
                  <button className={`subtab-btn ${providerSubTab === 'register' ? 'active' : ''}`} onClick={() => setProviderSubTab('register')}>
                    <PlusCircle size={16} /> Register Framework
                  </button>
                  <button className={`subtab-btn ${providerSubTab === 'suggestions' ? 'active' : ''}`} onClick={() => setProviderSubTab('suggestions')}>
                    <MessageSquare size={16} /> Suggest Indicators & Principles
                  </button>
                </div>

                {providerSubTab === 'register' ? (
                  <div className="content-card">
                    <div className="card-title"><PlusCircle size={20} /> Register New Framework</div>
                    <form onSubmit={handleRegister}>
                      <div className="form-grid">
                        <div className="form-group"><label>Upload Type</label><select className="input-field" value={regData.upload_type} onChange={e => setRegData({ ...regData, upload_type: e.target.value })}><option value="file">Direct File Upload</option><option value="link">DOI / Open Access URL</option></select></div>
                        <div className="form-group"><label>Authors</label><input className="input-field" type="text" required value={regData.authors} onChange={e => setRegData({ ...regData, authors: e.target.value })} placeholder="e.g., Johnston and Bruulsema" /></div>
                        <div className="form-group"><label>Year</label><input className="input-field" type="number" required value={regData.date} onChange={e => setRegData({ ...regData, date: e.target.value })} /></div>
                        <div className="form-group"><label>Publisher</label><input className="input-field" type="text" value={regData.publisher} onChange={e => setRegData({ ...regData, publisher: e.target.value })} /></div>
                        <div className="form-group full-width"><label>Document Title</label><input className="input-field" type="text" required value={regData.title} onChange={e => setRegData({ ...regData, title: e.target.value })} placeholder="Full academic title" /></div>
                        <div className="form-group"><label>Uploading Person</label><input className="input-field" type="text" value={regData.person} onChange={e => setRegData({ ...regData, person: e.target.value })} /></div>
                        <div className="form-group"><label className="checkbox-label"><input type="checkbox" checked={regData.right_to_share} onChange={e => setRegData({ ...regData, right_to_share: e.target.checked })} /><span>I have the right to share this file</span></label></div>
                        <div className="form-group full-width"><label>DOI / URL Link</label><input className="input-field" type="text" value={regData.url} onChange={e => setRegData({ ...regData, url: e.target.value })} placeholder="https://doi.org/..." /></div>
                        {regData.upload_type === 'file' && <div className="form-group full-width"><label>File Attachment (PDF) *</label><div className="file-upload-zone"><input type="file" accept=".pdf" onChange={e => setSelectedFile(e.target.files[0])} />{selectedFile && <div className="file-name-hint">{selectedFile.name}</div>}</div></div>}
                      </div>
                      <div className="form-actions" style={{ marginTop: 24 }}><button className="btn-primary" type="submit" disabled={loading}>{loading ? 'Registering…' : 'Register & Add to Database'} <ArrowRight size={16} /></button></div>
                    </form>
                  </div>
                ) : (
                  <>
                    <div className="content-card">
                      <div className="card-title"><PlusCircle size={20} /> Submit New Suggestion</div>
                      <form onSubmit={handleSubmitSuggestion}>
                        <div className="form-grid">
                          <div className="form-group"><label>Suggestion Type</label><select className="input-field" value={suggestionForm.type} onChange={e => setSuggestionForm({ ...suggestionForm, type: e.target.value })}><option value="indicator">Indicator</option><option value="principle">Principle</option></select></div>
                          <div className="form-group"><label>Action</label><select className="input-field" value={suggestionForm.action} onChange={e => setSuggestionForm({ ...suggestionForm, action: e.target.value })}><option value="addition">Suggest to Add</option><option value="deletion">Suggest to Remove</option></select></div>
                          <div className="form-group"><label>Target Name ({suggestionForm.type})</label>{suggestionForm.action === 'deletion' ? (<select className="input-field" required value={suggestionForm.target_name} onChange={e => { const val = e.target.value; if (suggestionForm.type === 'indicator') { const match = indicatorHierarchy.find(h => `${h.principle} | ${h.indicator}` === val); setSuggestionForm({ ...suggestionForm, target_name: val, parent_target: match ? match.principle : suggestionForm.parent_target }); } else { setSuggestionForm({ ...suggestionForm, target_name: val }); } }}><option value="">— Select Existing to Remove —</option>{suggestionForm.type === 'indicator' ? (indicatorHierarchy.map((h, idx) => (<option key={idx} value={`${h.principle} | ${h.indicator}`}>{getPrincipleDisplay(h.principle)} | {h.indicator}</option>))) : (uniquePrinciples.map((p, idx) => (<option key={idx} value={p}>{getPrincipleDisplay(p)}</option>)))}</select>) : (<input className="input-field" type="text" required value={suggestionForm.target_name} onChange={e => setSuggestionForm({ ...suggestionForm, target_name: e.target.value })} placeholder={suggestionForm.type === 'principle' ? "e.g., Biodiversity" : "e.g., Earthworm Count"} />)}</div>
                          <div className="form-group"><label>Parent Principle (if indicator)</label>{suggestionForm.type === 'indicator' ? (<select className="input-field" value={suggestionForm.parent_target} onChange={e => setSuggestionForm({ ...suggestionForm, parent_target: e.target.value })} disabled={suggestionForm.action === 'deletion'}><option value="">— Select Principle —</option>{uniquePrinciples.map((p, idx) => (<option key={idx} value={p}>{getPrincipleDisplay(p)}</option>))}</select>) : (<div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: '8px 0' }}>Principles are top-level items.</div>)}</div>
                          <div className="form-group"><label>Evidence / Source URL</label><input className="input-field" type="text" value={suggestionForm.evidence_url} onChange={e => setSuggestionForm({ ...suggestionForm, evidence_url: e.target.value })} placeholder="https://..." /></div>
                          <div className="form-group"><label>Your Contact Details (Optional)</label><input className="input-field" type="text" value={suggestionForm.contact_details} onChange={e => setSuggestionForm({ ...suggestionForm, contact_details: e.target.value })} placeholder="Email or Name" /></div>
                        </div>
                        <div className="form-actions" style={{ marginTop: 24 }}><button className="btn-primary" type="submit" disabled={loading}>{loading ? 'Submitting…' : 'Submit Suggestion'} <ArrowRight size={16} /></button></div>
                      </form>
                    </div>
                    <div className="content-card" style={{ marginTop: 24 }}>
                      <div className="card-title"><MessageSquare size={20} /> Recent Community Suggestions</div>
                      <div className="suggestion-list">
                        {suggestions.map(s => (
                          <div key={s.id} className="suggestion-card">
                            <div className="suggestion-header">
                              <span className="suggestion-type-tag">{s.type}</span>
                              <span className={`status-badge status-${s.status}`}>{s.status === 'included' ? 'Accepted' : s.status === 'excluded' ? 'Rejected' : s.status}</span>
                            </div>
                            <div className="suggestion-title"><strong>{s.action === 'addition' ? 'Add: ' : 'Remove: '}</strong> {s.target_name}</div>
                            {s.dev_response && <div className="dev-feedback-box"><div className="dev-feedback-title">Developer Response:</div><div className="dev-feedback-text">{s.dev_response}</div></div>}
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </motion.div>
            )}

            {view === 'analytics' && (
              <motion.div key="analytics" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <div className="content-card">
                  <div className="card-title"><Book size={20} /> Soil health - Mponela 2026 Update Analytics Pipeline</div>
                  <p className="recommendation-desc" style={{ marginBottom: 20 }}>
                    Run text extraction and hierarchical clustering models based on the agroecological principles and domains established by Mponela et al. (2026).
                  </p>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
                    <div className="action-card" style={{ padding: '20px', background: 'var(--bg-light)', borderRadius: '12px', border: '1px solid var(--border)' }}>
                      <h3 style={{ margin: '0 0 10px 0', display: 'flex', alignItems: 'center', gap: '8px' }}><FileText size={18} /> Phase 1: Text Extraction</h3>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>Extract proximity-based theme terms from framework manuscripts.</p>
                      <button className="btn-primary" onClick={runMponelaExtraction} disabled={mponelaExtractionLoading} style={{ width: '100%' }}>
                        {mponelaExtractionLoading ? 'Extracting Text...' : 'Run Extraction Model'}
                      </button>
                    </div>

                    <div className="action-card" style={{ padding: '20px', background: 'var(--bg-light)', borderRadius: '12px', border: '1px solid var(--border)' }}>
                      <h3 style={{ margin: '0 0 10px 0', display: 'flex', alignItems: 'center', gap: '8px' }}><Sparkles size={18} /> Phase 2: Clustering Model</h3>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>Run hierarchical clustering and generate principle heatmaps.</p>
                      <button className="btn-primary" onClick={runMponelaClustering} disabled={mponelaClusteringLoading} style={{ width: '100%' }}>
                        {mponelaClusteringLoading ? 'Running Model...' : 'Run Clustering Model'}
                      </button>
                    </div>
                  </div>

                  {renderMponelaTermsSummaryTable()}

                  {mponelaImages && (
                    <div className="mponela-results-section" style={{ marginTop: '32px', borderTop: '1px solid var(--border)', paddingTop: '24px' }}>
                      <h3 style={{ marginBottom: '16px' }}>Clustering Results & Heatmaps</h3>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
                        <div style={{ background: 'white', padding: '16px', borderRadius: '12px', border: '1px solid var(--border)', textAlign: 'center' }}>
                          <h4 style={{ marginBottom: '12px', color: 'var(--text-dark)' }}>Agroecology Index</h4>
                          <img src={`${API_BASE_URL}/results/agroecology_index_heatmap.jpeg?t=${new Date().getTime()}`} alt="Agroecology Index Heatmap" style={{ width: '100%', maxWidth: '200px', height: 'auto', borderRadius: '8px', border: '1px solid var(--border-light)' }} />
                        </div>

                        <div style={{ background: 'white', padding: '16px', borderRadius: '12px', border: '1px solid var(--border)', textAlign: 'center' }}>
                          <h4 style={{ marginBottom: '12px', color: 'var(--text-dark)' }}>Principle Z-Score Distribution</h4>
                          <img src={`${API_BASE_URL}/results/principle_heatmap_zscore.jpeg?t=${new Date().getTime()}`} alt="Principle Z-Score Heatmap" style={{ width: '100%', height: 'auto', borderRadius: '8px', border: '1px solid var(--border-light)' }} />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {view === 'results' && (
              <motion.div key="results" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <div className="subtabs-container" style={{ marginBottom: 24 }}>
                  <button className={`subtab-btn ${mponelaDataSource === 'r' ? 'active' : ''}`} onClick={() => setMponelaDataSource('r')}>
                    <Book size={16} /> Mponela 2026
                  </button>
                  <button className={`subtab-btn ${mponelaDataSource === 'python' ? 'active' : ''}`} onClick={() => setMponelaDataSource('python')}>
                    <BookOpen size={16} /> Mponela 2026 Update
                  </button>
                </div>
                {resultsSubTab === 'evaluation' || resultsSubTab === 'study' ? (
                  <>
                    <div className="content-card">
                      <div className="card-title"><Target size={20} /> Framework Evaluation (Agroecology)</div>
                      <div className="select-row">
                        <select className="input-field select-field" value={selectedAgro} onChange={e => setSelectedAgro(e.target.value)}>
                          <option value="">— Select Framework —</option>
                          {frameworks.map(f => (
                            <option key={f.id} value={f.id}>
                              {formatFirstAuthor(f.author_date || f.name)} {truncateWords(f.title, 10)}
                            </option>
                          ))}
                        </select>
                        <button className="btn-primary" onClick={handleRunAgroAnalysis} disabled={!selectedAgro || loading}>Evaluate Alignment</button>
                      </div>
                      {renderAgroScores()}
                    </div>
                    <div className="content-card" style={{ marginTop: 16 }}>
                      <div className="card-title"><PenTool size={20} /> Methodological Design Evaluation</div>
                      <div className="select-row">
                        <select className="input-field select-field" value={selectedDesign} onChange={e => setSelectedDesign(e.target.value)}>
                          <option value="">— Select Framework —</option>
                          {frameworks.map(f => (
                            <option key={f.id} value={f.id}>
                              {formatFirstAuthor(f.author_date || f.name)} {truncateWords(f.title, 10)}
                            </option>
                          ))}
                        </select>
                        <button className="btn-primary" onClick={handleRunDesignAnalysis} disabled={!selectedDesign || loading}>Evaluate Design</button>
                      </div>
                      {resultDesign && resultDesign.type === 'analysis' && (
                        <div className="design-results" style={{ marginTop: 24 }}>
                          {renderDesignScores()}
                        </div>
                      )}
                    </div>
                    {mponelaDataSource === 'python' && renderMponelaTermsSummaryTable()}
                  </>
                ) : (
                  <>
                    <div className="content-card">
                      <div className="card-title"><Layers size={20} /> {appMode === 'mponela' ? (mponelaDataSource === 'r' ? 'Soil health - Mponela et al. 2026 Strategic Alignment' : 'Soil health - Mponela 2026-update Strategic Alignment') : 'Global Strategic Alignment (Automated)'}</div>
                      <div className="global-comparison-grid" style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
                        {appMode === 'mponela' ? (
                          <div className="comparison-pane" style={{ width: '100%', maxWidth: '500px' }}>
                            <h4 style={{ textAlign: 'center', color: 'var(--primary)', marginBottom: 16 }}>{mponelaDataSource === 'r' ? 'Soil health - Mponela et al. 2026' : 'Soil health - Mponela 2026-update'}</h4>
                            <div style={{ display: 'flex', justifyContent: 'center' }}><SpiderChart data={studySummary} color="var(--primary)" size={350} /></div>
                            <div className="stats-list" style={{ maxHeight: '250px', overflowY: 'auto', marginTop: 16 }}>
                              {studySummary.map((s, i) => (
                                <div key={i} className="stat-item" style={{ marginBottom: 8 }}>
                                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                                    <span>{s.principle}</span>
                                    <span>{(s.score * 100).toFixed(0)}%</span>
                                  </div>
                                  <div style={{ height: 3, background: 'var(--border)', borderRadius: 2 }}>
                                    <div style={{ height: '100%', width: `${s.score * 100}%`, background: 'var(--primary)' }} />
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="comparison-pane" style={{ width: '100%', maxWidth: '500px' }}>
                            <h4 style={{ textAlign: 'center', color: '#8e44ad', marginBottom: 16 }}>Current Ontology (Automated)</h4>
                            <div style={{ display: 'flex', justifyContent: 'center' }}><SpiderChart data={agrontologyStudySummary} color="#8e44ad" size={350} /></div>
                            <div className="stats-list" style={{ maxHeight: '250px', overflowY: 'auto', marginTop: 16 }}>
                              {agrontologyStudySummary.map((s, i) => (
                                <div key={i} className="stat-item" style={{ marginBottom: 8 }}>
                                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                                    <span>{s.principle}</span>
                                    <span>{(s.score * 100).toFixed(0)}%</span>
                                  </div>
                                  <div style={{ height: 3, background: 'var(--border)', borderRadius: 2 }}>
                                    <div style={{ height: '100%', width: `${s.score * 100}%`, background: '#8e44ad' }} />
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="content-card" style={{ marginTop: 16 }}>
                      <div className="card-title"><PenTool size={20} /> {appMode === 'mponela' ? 'Mponela 2026 Design Domain Fit' : 'Current Ontology Design Domain Fit'}</div>
                      <div className="global-comparison-grid" style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
                        {appMode === 'mponela' ? (
                          <div className="comparison-pane" style={{ width: '100%', maxWidth: '500px' }}>
                            <h4 style={{ textAlign: 'center', color: '#ff7f00', marginBottom: 16 }}>Mponela 2026 Design Fit</h4>
                            <div style={{ display: 'flex', justifyContent: 'center' }}><SpiderChart data={globalDesignSummary} color="#ff7f00" size={350} /></div>
                          </div>
                        ) : (
                          <div className="comparison-pane" style={{ width: '100%', maxWidth: '500px' }}>
                            <h4 style={{ textAlign: 'center', color: '#e67e22', marginBottom: 16 }}>Current Ontology Design Fit</h4>
                            <div style={{ display: 'flex', justifyContent: 'center' }}><SpiderChart data={agrontologyDesignSummary} color="#e67e22" size={350} /></div>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="content-card" style={{ marginTop: 24 }}>
                      <div className="card-title"><Layers size={20} /> Global Synthesis Collage</div>
                      <div className="collage-grid">
                        <div className="collage-item large">
                          <img src={`${API_BASE_URL}/results/figure3_heatmap.png?t=${new Date().getTime()}`} className="research-figure" />
                          <div className="collage-caption">Global Framework Analytics: Clustering, Heatmap, Orientation & Design Cycle (n=64)</div>
                        </div>
                        <div className="collage-item">
                          <img src={`${API_BASE_URL}/results/figure2a_orientation.png?t=${new Date().getTime()}`} className="research-figure" />
                          <div className="collage-caption">Use-orientation Profiling</div>
                        </div>
                        <div className="collage-item">
                          <img src={`${API_BASE_URL}/results/figure4_programming_cycle.png?t=${new Date().getTime()}`} className="research-figure" />
                          <div className="collage-caption">Integrated Programming Cycle</div>
                        </div>
                        <div className="collage-item">
                          <img src={`${API_BASE_URL}/results/figure2b_evolution.png?t=${new Date().getTime()}`} className="research-figure" />
                          <div className="collage-caption">Evolution (1985-2024)</div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

export default App;
