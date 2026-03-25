import { useEffect, useRef, useState, useCallback } from 'react'
import cytoscape from 'cytoscape'
import fcose from 'cytoscape-fcose'
import NodeDetails from './NodeDetails'

cytoscape.use(fcose)

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

const ENTITY_ORDER = [
  'Customer', 'SalesOrder', 'Product', 'SalesOrderItem',
  'Delivery', 'BillingDocument', 'JournalEntry', 'Payment'
]

export default function GraphView({ graphData, highlightedNodes = [], onNodeClick }) {
  const containerRef = useRef(null)
  const cyRef = useRef(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [stats, setStats] = useState({ nodes: 0, edges: 0 })
  const [filterType, setFilterType] = useState('All')
  const [loading, setLoading] = useState(false)

  const initCy = useCallback((elements) => {
    if (!containerRef.current) return
    if (cyRef.current) {
      cyRef.current.destroy()
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(color)',
            'border-color': 'data(color)',
            'border-width': 2,
            'border-opacity': 0.6,
            'label': 'data(label)',
            'font-size': 9,
            'font-family': "'IBM Plex Mono', monospace",
            'color': '#1E293B',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 3,
            'text-max-width': 80,
            'text-wrap': 'ellipsis',
            'width': 'mapData(degree, 1, 20, 12, 36)',
            'height': 'mapData(degree, 1, 20, 12, 36)',
            'opacity': 0.9,
          },
        },
        {
          selector: 'node[entity_type = "Customer"]',
          style: { shape: 'ellipse' },
        },
        {
          selector: 'node[entity_type = "SalesOrder"]',
          style: { shape: 'roundrectangle' },
        },
        {
          selector: 'node[entity_type = "BillingDocument"]',
          style: { shape: 'diamond' },
        },
        {
          selector: 'node[entity_type = "JournalEntry"]',
          style: { shape: 'pentagon' },
        },
        {
          selector: 'node[entity_type = "Payment"]',
          style: { shape: 'hexagon' },
        },
        {
          selector: 'node[entity_type = "Delivery"]',
          style: { shape: 'tag' },
        },
        {
          selector: 'node[entity_type = "Product"]',
          style: { shape: 'star' },
        },
        {
          selector: 'edge',
          style: {
            'line-color': '#CBD5E1',
            'target-arrow-color': '#CBD5E1',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'width': 1.2,
            'arrow-scale': 0.8,
            'opacity': 0.5,
          },
        },
        {
          selector: 'node.highlighted',
          style: {
            'border-width': 4,
            'border-color': '#FBBF24',
            'border-opacity': 1,
            'background-color': '#FBBF24',
            'opacity': 1,
            'z-index': 999,
          },
        },
        {
          selector: 'node.selected',
          style: {
            'border-width': 3,
            'border-color': '#1E293B',
            'border-opacity': 1,
            'opacity': 1,
            'z-index': 9999,
          },
        },
        {
          selector: 'node.faded',
          style: { opacity: 0.15 },
        },
        {
          selector: 'edge.faded',
          style: { opacity: 0.05 },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 3,
            'border-color': '#1E293B',
          },
        },
      ],
      layout: {
        name: 'fcose',
        quality: 'proof',
        randomize: true,
        animate: true,
        animationDuration: 800,
        nodeRepulsion: 6000,
        idealEdgeLength: 80,
        edgeElasticity: 0.45,
        nestingFactor: 0.1,
        gravity: 0.25,
        numIter: 2500,
        tilingPaddingVertical: 10,
        tilingPaddingHorizontal: 10,
        gravityRangeCompound: 1.5,
        gravityCompound: 1.0,
        gravityRange: 3.8,
      },
      wheelSensitivity: 0.3,
      minZoom: 0.05,
      maxZoom: 5,
    })

    cy.on('tap', 'node', (evt) => {
      const node = evt.target
      const nodeData = {
        id: node.id(),
        entity_type: node.data('entity_type'),
        label: node.data('label'),
        properties: node.data('properties'),
        connections: node.degree(),
      }

      // Fade/unfade
      cy.elements().addClass('faded')
      node.removeClass('faded').addClass('selected')
      node.neighborhood().removeClass('faded')

      setSelectedNode(nodeData)
      if (onNodeClick) onNodeClick(nodeData)
    })

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        cy.elements().removeClass('faded selected highlighted')
        setSelectedNode(null)
      }
    })

    cy.on('mouseover', 'node', (evt) => {
      containerRef.current.style.cursor = 'pointer'
      evt.target.style('opacity', 1)
    })

    cy.on('mouseout', 'node', () => {
      containerRef.current.style.cursor = 'default'
    })

    cyRef.current = cy
    setStats({ nodes: cy.nodes().length, edges: cy.edges().length })
  }, [onNodeClick])

  // Build graph
  useEffect(() => {
    if (!graphData?.nodes?.length) return
    setLoading(true)

    let nodes = graphData.nodes
    let edges = graphData.edges

    if (filterType !== 'All') {
      const visibleIds = new Set(
        nodes.filter(n => n.data.entity_type === filterType).map(n => n.data.id)
      )
      nodes = nodes.filter(n => visibleIds.has(n.data.id))
      edges = edges.filter(e => visibleIds.has(e.data.source) && visibleIds.has(e.data.target))
    }

    // Add degree to each node
    const degreeMap = {}
    edges.forEach(e => {
      degreeMap[e.data.source] = (degreeMap[e.data.source] || 0) + 1
      degreeMap[e.data.target] = (degreeMap[e.data.target] || 0) + 1
    })
    const enrichedNodes = nodes.map(n => ({
      data: { ...n.data, degree: degreeMap[n.data.id] || 1 }
    }))

    setTimeout(() => {
      initCy([...enrichedNodes, ...edges])
      setLoading(false)
    }, 50)
  }, [graphData, filterType, initCy])

  // Highlight nodes from query
  useEffect(() => {
    if (!cyRef.current || !highlightedNodes?.length) return
    cyRef.current.elements().removeClass('highlighted')
    highlightedNodes.forEach(nid => {
      const el = cyRef.current.$(`#${CSS.escape(nid)}`)
      if (el.length) {
        el.addClass('highlighted')
      }
    })
    if (highlightedNodes.length > 0) {
      const first = cyRef.current.$(`#${CSS.escape(highlightedNodes[0])}`)
      if (first.length) {
        cyRef.current.animate({ center: { eles: first }, zoom: 1.5 }, { duration: 600 })
      }
    }
  }, [highlightedNodes])

  const handleFitView = () => cyRef.current?.fit(undefined, 30)
  const handleZoomIn = () => cyRef.current?.zoom({ level: (cyRef.current.zoom() * 1.3), renderedPosition: { x: containerRef.current.offsetWidth / 2, y: containerRef.current.offsetHeight / 2 } })
  const handleZoomOut = () => cyRef.current?.zoom({ level: (cyRef.current.zoom() * 0.75), renderedPosition: { x: containerRef.current.offsetWidth / 2, y: containerRef.current.offsetHeight / 2 } })

  const entityCounts = {}
  graphData?.nodes?.forEach(n => {
    const t = n.data.entity_type
    entityCounts[t] = (entityCounts[t] || 0) + 1
  })

  const s = {
    wrapper: { position: 'relative', width: '100%', height: '100%', background: '#F8FAFC' },
    cy: { width: '100%', height: '100%' },
    topBar: {
      position: 'absolute', top: 12, right: 12, zIndex: 50,
      display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-end',
    },
    filterRow: {
      display: 'flex', gap: 4, flexWrap: 'wrap', justifyContent: 'flex-end', maxWidth: 380,
    },
    filterChip: (active, color) => ({
      padding: '3px 10px', borderRadius: 99, border: `1.5px solid ${color}`,
      background: active ? color : 'white', color: active ? 'white' : color,
      fontSize: 11, fontWeight: 700, cursor: 'pointer', fontFamily: 'monospace',
      transition: 'all 0.15s',
    }),
    controls: {
      display: 'flex', gap: 4,
    },
    btn: {
      background: 'white', border: '1px solid #E2E8F0', borderRadius: 8,
      padding: '6px 12px', fontSize: 12, cursor: 'pointer', color: '#1E293B',
      fontFamily: 'monospace', fontWeight: 600, boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
    },
    statsBar: {
      position: 'absolute', bottom: 12, left: '50%', transform: 'translateX(-50%)',
      background: 'white', border: '1px solid #E2E8F0', borderRadius: 99,
      padding: '4px 14px', fontSize: 11, color: '#64748B', fontFamily: 'monospace',
      display: 'flex', gap: 12, boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
    },
    loadingOverlay: {
      position: 'absolute', inset: 0, background: 'rgba(248,250,252,0.85)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 14, color: '#64748B', fontFamily: 'monospace', zIndex: 200,
    },
    emptyState: {
      position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', color: '#94A3B8',
      fontFamily: 'monospace', gap: 8,
    },
  }

  return (
    <div style={s.wrapper}>
      <div ref={containerRef} style={s.cy} />

      {loading && (
        <div style={s.loadingOverlay}>
          <span style={{ fontSize: 24, marginRight: 10 }}>⚙️</span> Laying out graph…
        </div>
      )}

      {!graphData?.nodes?.length && !loading && (
        <div style={s.emptyState}>
          <div style={{ fontSize: 40 }}>🕸️</div>
          <div style={{ fontWeight: 700, fontSize: 16, color: '#64748B' }}>No graph data</div>
          <div style={{ fontSize: 12 }}>Click "Load Data" to initialize the dataset</div>
        </div>
      )}

      {/* Top-right controls */}
      {graphData?.nodes?.length > 0 && (
        <div style={s.topBar}>
          <div style={s.filterRow}>
            <button
              style={s.filterChip(filterType === 'All', '#64748B')}
              onClick={() => setFilterType('All')}
            >All</button>
            {ENTITY_ORDER.filter(t => entityCounts[t]).map(t => (
              <button
                key={t}
                style={s.filterChip(filterType === t, TYPE_COLORS[t])}
                onClick={() => setFilterType(t)}
              >
                {t} <span style={{ opacity: 0.7 }}>({entityCounts[t] || 0})</span>
              </button>
            ))}
          </div>
          <div style={s.controls}>
            <button style={s.btn} onClick={handleZoomIn} title="Zoom in">＋</button>
            <button style={s.btn} onClick={handleZoomOut} title="Zoom out">－</button>
            <button style={s.btn} onClick={handleFitView} title="Fit view">⊡ Fit</button>
          </div>
        </div>
      )}

      {/* Node detail panel */}
      {selectedNode && (
        <NodeDetails
          node={selectedNode}
          onClose={() => {
            setSelectedNode(null)
            cyRef.current?.elements().removeClass('faded selected')
          }}
          onNodeSelect={(id) => {
            const el = cyRef.current?.$(`#${CSS.escape(id)}`)
            if (el?.length) {
              el.trigger('tap')
              cyRef.current.animate({ center: { eles: el }, zoom: 2 }, { duration: 500 })
            }
          }}
        />
      )}

      {/* Stats bar */}
      {stats.nodes > 0 && (
        <div style={s.statsBar}>
          <span>🔵 {stats.nodes} nodes</span>
          <span>⟶ {stats.edges} edges</span>
          {highlightedNodes.length > 0 && (
            <span style={{ color: '#FBBF24', fontWeight: 700 }}>
              ★ {highlightedNodes.length} highlighted
            </span>
          )}
        </div>
      )}
    </div>
  )
}
