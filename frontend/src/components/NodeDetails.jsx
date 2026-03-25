import { useState, useEffect } from 'react'
import { getNodeNeighbors } from '../services/api'

const TYPE_COLORS = {
  Customer: '#3B82F6',
  SalesOrder: '#10B981',
  SalesOrderItem: '#6366F1',
  Delivery: '#F59E0B',
  BillingDocument: '#EF4444',
  JournalEntry: '#8B5CF6',
  Payment: '#14B8A6',
  Product: '#F97316',
}

const TYPE_ICONS = {
  Customer: '👤',
  SalesOrder: '📋',
  SalesOrderItem: '📦',
  Delivery: '🚚',
  BillingDocument: '🧾',
  JournalEntry: '📒',
  Payment: '💳',
  Product: '🏷️',
}

export default function NodeDetails({ node, onClose, onNodeSelect }) {
  const [neighbors, setNeighbors] = useState([])
  const [loadingNeighbors, setLoadingNeighbors] = useState(false)
  const [showAll, setShowAll] = useState(false)

  useEffect(() => {
    if (!node) return
    setLoadingNeighbors(true)
    setShowAll(false)
    getNodeNeighbors(node.id)
      .then(r => setNeighbors(r.data.neighbors || []))
      .catch(() => setNeighbors([]))
      .finally(() => setLoadingNeighbors(false))
  }, [node?.id])

  if (!node) return null

  const color = TYPE_COLORS[node.entity_type] || '#94A3B8'
  const icon = TYPE_ICONS[node.entity_type] || '●'
  const props = node.properties || {}
  const propEntries = Object.entries(props).filter(([, v]) => v !== null && v !== '' && v !== undefined)
  const HIDDEN_THRESHOLD = 8
  const visibleProps = showAll ? propEntries : propEntries.slice(0, HIDDEN_THRESHOLD)

  const styles = {
    panel: {
      position: 'absolute',
      top: 12,
      left: 12,
      width: 300,
      background: '#fff',
      border: '1px solid #E2E8F0',
      borderRadius: 12,
      boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
      fontFamily: "'IBM Plex Mono', 'Fira Code', monospace",
      fontSize: 12,
      zIndex: 100,
      overflow: 'hidden',
      maxHeight: 'calc(100vh - 100px)',
      display: 'flex',
      flexDirection: 'column',
    },
    header: {
      padding: '12px 14px',
      background: color + '18',
      borderBottom: `2px solid ${color}40`,
      display: 'flex',
      alignItems: 'center',
      gap: 8,
    },
    entityBadge: {
      background: color,
      color: '#fff',
      borderRadius: 6,
      padding: '2px 8px',
      fontSize: 11,
      fontWeight: 700,
      letterSpacing: '0.05em',
    },
    closeBtn: {
      marginLeft: 'auto',
      background: 'none',
      border: 'none',
      cursor: 'pointer',
      color: '#64748B',
      fontSize: 16,
      lineHeight: 1,
      padding: '2px 4px',
      borderRadius: 4,
    },
    body: {
      padding: '10px 14px',
      overflowY: 'auto',
      flex: 1,
    },
    row: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      padding: '4px 0',
      borderBottom: '1px solid #F1F5F9',
      gap: 8,
    },
    key: {
      color: '#64748B',
      flexShrink: 0,
      maxWidth: '45%',
    },
    val: {
      color: '#1E293B',
      textAlign: 'right',
      wordBreak: 'break-all',
      fontWeight: 600,
    },
    sectionTitle: {
      color: '#94A3B8',
      fontSize: 10,
      fontWeight: 700,
      letterSpacing: '0.1em',
      textTransform: 'uppercase',
      margin: '10px 0 6px',
    },
    neighborChip: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 4,
      background: '#F8FAFC',
      border: '1px solid #E2E8F0',
      borderRadius: 6,
      padding: '3px 8px',
      marginBottom: 4,
      marginRight: 4,
      cursor: 'pointer',
      fontSize: 11,
      transition: 'all 0.15s',
    },
    dot: {
      width: 8,
      height: 8,
      borderRadius: '50%',
      flexShrink: 0,
    },
    showMoreBtn: {
      background: 'none',
      border: 'none',
      color: color,
      cursor: 'pointer',
      fontSize: 11,
      fontWeight: 700,
      padding: '4px 0',
      marginTop: 2,
    },
    connCount: {
      background: '#F1F5F9',
      borderRadius: 999,
      padding: '2px 8px',
      fontSize: 10,
      color: '#64748B',
      fontWeight: 700,
    }
  }

  return (
    <div style={styles.panel}>
      <div style={styles.header}>
        <span style={{ fontSize: 18 }}>{icon}</span>
        <div>
          <div style={styles.entityBadge}>{node.entity_type}</div>
          <div style={{ color: '#1E293B', fontWeight: 700, marginTop: 2, fontSize: 13 }}>
            {node.label}
          </div>
        </div>
        <button style={styles.closeBtn} onClick={onClose}>✕</button>
      </div>

      <div style={styles.body}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
          <div style={styles.sectionTitle}>Properties</div>
          <span style={styles.connCount}>{node.connections ?? 0} connections</span>
        </div>

        {visibleProps.map(([k, v]) => (
          <div key={k} style={styles.row}>
            <span style={styles.key}>{k}</span>
            <span style={styles.val}>
              {typeof v === 'boolean' ? (v ? 'Yes' : 'No') : String(v).length > 30 ? String(v).slice(0, 30) + '…' : String(v)}
            </span>
          </div>
        ))}

        {propEntries.length > HIDDEN_THRESHOLD && (
          <button style={styles.showMoreBtn} onClick={() => setShowAll(p => !p)}>
            {showAll ? '▲ Show less' : `▼ Show ${propEntries.length - HIDDEN_THRESHOLD} more fields`}
          </button>
        )}

        <div style={styles.sectionTitle}>
          Connected Nodes {loadingNeighbors ? '…' : `(${neighbors.length})`}
        </div>

        {loadingNeighbors ? (
          <div style={{ color: '#94A3B8', fontSize: 11 }}>Loading…</div>
        ) : neighbors.length === 0 ? (
          <div style={{ color: '#94A3B8', fontSize: 11 }}>No connections in current graph view</div>
        ) : (
          <div>
            {neighbors.slice(0, 12).map(n => {
              const nColor = TYPE_COLORS[n.data?.entity_type] || '#94A3B8'
              return (
                <span
                  key={n.data?.id}
                  style={styles.neighborChip}
                  onClick={() => onNodeSelect && onNodeSelect(n.data?.id)}
                  title={n.data?.label}
                >
                  <span style={{ ...styles.dot, background: nColor }} />
                  {n.data?.label?.slice(0, 18) || n.data?.id}
                </span>
              )
            })}
            {neighbors.length > 12 && (
              <div style={{ color: '#94A3B8', fontSize: 10, marginTop: 4 }}>
                +{neighbors.length - 12} more
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
