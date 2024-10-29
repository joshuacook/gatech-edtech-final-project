// app/relationships/network-graph.tsx
'use client'

import React, { useCallback, useEffect, useRef } from 'react'
import dynamic from 'next/dynamic'
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false })

interface Node {
  id: string
  name: string
  val: number
}

interface Link {
  source: string
  target: string
  value: number
  type: string
  connection_type?: string
}

interface NetworkGraphProps {
  relationships: Array<{
    source: string
    target: string
    type: string
    connection_type?: string
    strength: number
  }>
}

export default function NetworkGraph({ relationships }: NetworkGraphProps) {
  const graphRef = useRef()

  const nodes: Node[] = Array.from(
    new Set(
      relationships.flatMap(r => [r.source, r.target])
    )
  ).map(id => ({
    id,
    name: id,
    val: relationships.filter(r => r.source === id || r.target === id).length
  }))

  const links: Link[] = relationships.map(r => ({
    source: r.source,
    target: r.target,
    value: r.strength,
    type: r.type,
    connection_type: r.connection_type
  }))

  const data = {
    nodes,
    links
  }

  const handleNodeClick = useCallback((node: Node) => {
    // Handle node click - could zoom in, show details, etc.
    console.log('Clicked node:', node)
  }, [])

  const handleLinkClick = useCallback((link: Link) => {
    // Handle link click - could show relationship details, etc.
    console.log('Clicked link:', link)
  }, [])

  return (
    <ForceGraph2D
      ref={graphRef}
      graphData={data}
      nodeLabel="name"
      nodeColor="var(--primary)"
      nodeRelSize={6}
      linkWidth={link => (link.value as number) * 2}
      linkLabel={link => `${link.type}${link.connection_type ? ` (${link.connection_type})` : ''}`}
      linkColor={() => "var(--muted-foreground)"}
      onNodeClick={handleNodeClick}
      onLinkClick={handleLinkClick}
      width={800}
      height={600}
    />
  )
}