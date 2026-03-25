import { useState, useEffect, useCallback } from 'react'
import GraphView from '../components/GraphView'
import ChatPanel from '../components/ChatPanel'
import { getGraph, loadData, getHealth } from '../services/api'

export default function Home() {
  const [graphData, setGraphData] = useState(null)
  const [highlightedNodes, setHighlightedNodes] = useState([])
  const [loadingData, setLoadingData] = useState(false)
  const [loadingGraph, setLoadingGraph] = useState(false)
  const [status, setStatus] = useState({ loaded: false, checked: false })
  const [toast, setToast] = useState(null)
  const [chatCollapsed, setChatCollapsed] = useState(false)

  const showToast = (msg, type = 'info') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 4000)
  }

  const fetchGraph = useCallback(async () => {
    setLoadingGraph(true)
    try {
      const res = await getGraph()
      setGraphData(res.data)
    } catch (err) {
      showToast('Failed to load graph: ' + (err.message || 'Unknown error'), 'error')
    } finally {
      setLoadingGraph(false)
    }
  }, [])

  const checkStatus = useCallback(async () => {
    try {
      const res = await getHealth()
      setStatus({ loaded: res.data.data_loaded, checked: true })
      if (res.data.data_loaded) {
        fetchGraph()
      }
    } catch {
      setStatus({ loaded: false, checked: true })
    }
  }, [fetchGraph])

  useEffect(() => {
    checkStatus()
  }, [checkStatus])

  const handleLoadData = async () => {
    setLoadingData(true)
    showToast('Loading dataset… this may take 30–60 seconds', 'info')
    try {
      const res = await loadData()
      const counts = res.data.row_counts
      const total = Object.values(counts).reduce((a, b) => a + b, 0)
      showToast(`✓ Loaded ${total.toLocaleString()} records across ${Object.keys(counts).length} tables`, 'success')
      await fetchGraph()
      setStatus({ loaded: true, checked: true })
    } catch (err) {
      showToast('Load failed: ' + (err.response?.data?.detail || err.message), 'error')
    } finally {
      setLoadingData(false)
    }
  }

  const handleQueryResult = (data) => {
    if (data?.highlighted_nodes?.length) {
      setHighlightedNodes(data.highlighted_nodes)
    } else {
      setHighlightedNodes([])
    }
  }

  const toastColors = { info: '#3B82F6', success: '#10B981', error: '#EF4444' }

  const s = {
    root: {
      width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column',
      background: '#F8FAFC', fontFamily: "'IBM Plex Sans', system-ui, sans-serif",
      overflow: 'hidden',
    },
    topNav: {
      height: 48, background: '#fff', borderBottom: '1px solid #E2E8F0',
      display: 'flex', alignItems: 'center', padding: '0 18px',
      flexShrink: 0, gap: 12, zIndex: 100,
    },
    breadcrumb: {
      display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: '#94A3B8',
    },
    crumbSep: { color: '#CBD5E1', fontWeight: 300 },
    crumbActive: { color: '#0F172A', fontWeight: 700 },
    navActions: { marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 },
    loadBtn: {
      padding: '6px 14px', borderRadius: 8, border: '1.5px solid #0F172A',
      background: loadingData ? '#F1F5F9' : '#0F172A',
      color: loadingData ? '#94A3B8' : '#fff', fontWeight: 700,
      fontSize: 12, cursor: loadingData ? 'not-allowed' : 'pointer',
      transition: 'all 0.15s', fontFamily: 'monospace',
    },
    refreshBtn: {
      padding: '6px 14px', borderRadius: 8, border: '1.5px solid #E2E8F0',
      background: '#fff', color: '#475569', fontWeight: 700,
      fontSize: 12, cursor: 'pointer', fontFamily: 'monospace',
    },
    body: {
      flex: 1, display: 'flex', overflow: 'hidden',
    },
    graphPanel: {
      flex: 1, position: 'relative', overflow: 'hidden',
    },
    chatSidebar: {
      width: chatCollapsed ? 48 : 380,
      minWidth: chatCollapsed ? 48 : 380,
      borderLeft: '1px solid #E2E8F0',
      background: '#fff',
      display: 'flex', flexDirection: 'column',
      overflow: 'hidden', transition: 'width 0.25s, min-width 0.25s',
      position: 'relative',
    },
    collapseBtn: {
      position: 'absolute', top: 12, left: chatCollapsed ? 8 : 'auto', right: chatCollapsed ? 'auto' : 8,
      zIndex: 10, background: '#F8FAFC', border: '1px solid #E2E8F0',
      borderRadius: 6, width: 28, height: 28, display: 'flex',
      alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
      fontSize: 14, color: '#64748B',
    },
    graphLoadOverlay: {
      position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10,
      fontFamily: 'monospace', color: '#64748B', fontSize: 13,
    },
    spinner: {
      width: 32, height: 32, border: '3px solid #E2E8F0',
      borderTopColor: '#0F172A', borderRadius: '50%',
      animation: 'spin 0.8s linear infinite',
    },
    toast: toast ? {
      position: 'fixed', bottom: 20, left: '50%', transform: 'translateX(-50%)',
      background: '#0F172A', color: '#fff', padding: '10px 18px', borderRadius: 10,
      fontSize: 12, fontFamily: 'monospace', zIndex: 9999,
      borderLeft: `4px solid ${toastColors[toast.type] || '#3B82F6'}`,
      boxShadow: '0 4px 16px rgba(0,0,0,0.2)', maxWidth: 420, textAlign: 'center',
    } : { display: 'none' },
  }

  return (
    <div style={s.root}>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;700;800&display=swap');
      `}</style>

      {/* Top nav */}
      <div style={s.topNav}>
        <div style={s.breadcrumb}>
          <span>⊞</span>
          <span style={s.crumbSep}>/</span>
          <span>Mapping</span>
          <span style={s.crumbSep}>/</span>
          <span style={s.crumbActive}>Order to Cash</span>
        </div>

        {graphData && (
          <div style={{
            fontSize: 11, fontFamily: 'monospace', color: '#94A3B8',
            background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: 6, padding: '2px 10px',
          }}>
            {graphData.total_nodes} nodes · {graphData.total_edges} edges
          </div>
        )}

        <div style={s.navActions}>
          {graphData && (
            <button style={s.refreshBtn} onClick={fetchGraph} disabled={loadingGraph}>
              {loadingGraph ? '⟳ …' : '⟳ Refresh Graph'}
            </button>
          )}
          <button style={s.loadBtn} onClick={handleLoadData} disabled={loadingData}>
            {loadingData ? '⏳ Loading…' : status.loaded ? '⟳ Reload Data' : '▶ Load Data'}
          </button>
        </div>
      </div>

      {/* Main body */}
      <div style={s.body}>
        {/* Graph panel */}
        <div style={s.graphPanel}>
          {loadingGraph && !graphData && (
            <div style={s.graphLoadOverlay}>
              <div style={s.spinner} />
              <span>Building graph layout…</span>
            </div>
          )}
          <GraphView
            graphData={graphData}
            highlightedNodes={highlightedNodes}
            onNodeClick={(node) => { /* optionally sync with chat */ }}
          />
        </div>

        {/* Chat sidebar */}
        <div style={s.chatSidebar}>
          <button
            style={s.collapseBtn}
            onClick={() => setChatCollapsed(p => !p)}
            title={chatCollapsed ? 'Open chat' : 'Collapse chat'}
          >
            {chatCollapsed ? '◀' : '▶'}
          </button>
          {!chatCollapsed && (
            <ChatPanel onQueryResult={handleQueryResult} />
          )}
        </div>
      </div>

      {/* Toast */}
      {toast && <div style={s.toast}>{toast.msg}</div>}
    </div>
  )
}
