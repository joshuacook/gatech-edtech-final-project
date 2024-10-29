'use client'

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { NetworkGraphNode } from './types'

interface RelationshipsTableProps {
  relationships: NetworkGraphNode[]
}

export default function RelationshipsTable({ relationships }: RelationshipsTableProps) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Source</TableHead>
            <TableHead>Target</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Connection</TableHead>
            <TableHead>Strength</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {relationships.map((relationship) => (
            <TableRow key={`${relationship.source}-${relationship.target}`}>
              <TableCell>{relationship.source}</TableCell>
              <TableCell>{relationship.target}</TableCell>
              <TableCell>{relationship.type}</TableCell>
              <TableCell>{relationship.connection_type || '-'}</TableCell>
              <TableCell>{(relationship.strength * 100).toFixed(1)}%</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}