// app/relationships/network-graph.tsx
'use client'

import React, { useMemo } from 'react'
import ReactFlow, { 
  Node, 
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  ConnectionLineType
} from 'reactflow'
import 'reactflow/dist/style.css'

import { NetworkGraphProps } from './types'

const NODE_TYPES = {
  concept: {
    style: {
      background: 'var(--primary)',
      color: 'var(--primary-foreground)',
      border: 'none',
      borderRadius: '8px',
      padding: '8px 16px',
    }
  }
}

export default function NetworkGraph({ relationships }: NetworkGraphProps) {
  // Transform data into nodes and edges
  const { initialNodes, initialEdges } = useMemo(() => {
    const nodeMap = new Map<string, number>()
    
    // Count node connections
    relationships.forEach((r) => {
      nodeMap.set(r.source, (nodeMap.get(r.source) || 0) + 1)
      nodeMap.set(r.target, (nodeMap.get(r.target) || 0) + 1)
    })

    // Create nodes with random positions
    const nodes: Node[] = Array.from(nodeMap.entries()).map(([id, count]) => ({
      id,
      data: { 
        label: `${id}\n(${count} connection${count !== 1 ? 's' : ''})`,
        connections: count 
      },
      position: {
        x: Math.random() * 800,
        y: Math.random() * 600
      },
      type: 'concept',
      style: {
        ...NODE_TYPES.concept.style,
        fontSize: `${Math.min(16, 12 + count)}px`,
      }
    }))

    // Create edges with styling based on relationship type
    const edges: Edge[] = relationships.map((r, index) => ({
      id: `${r.source}-${r.target}-${index}`,
      source: r.source,
      target: r.target,
      label: `${r.type}${r.connection_type ? ` (${r.connection_type})` : ''}`,
      type: 'smoothstep',
      animated: true,
      style: {
        strokeWidth: Math.max(1, r.strength * 5),
        opacity: Math.max(0.2, r.strength),
      },
      labelStyle: {
        fontSize: '12px',
        fill: 'var(--muted-foreground)',
      },
    }))

    return { initialNodes: nodes, initialEdges: edges }
  }, [relationships])

  
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes) // @ts-ignore
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges) // @ts-ignore

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        connectionLineType={ConnectionLineType.SmoothStep}
        fitView
        attributionPosition="bottom-left"
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  )
}