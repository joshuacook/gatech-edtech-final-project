// app/relationships/relationships-table.tsx
'use client'

import { useState } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from '@/components/ui/button'
import { Edit, Trash2 } from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

interface Relationship {
  source: string
  target: string
  type: string
  connection_type?: string
  strength: number
  created_at: string
}

interface RelationshipsTableProps {
  relationships: Relationship[]
  onDelete: (source: string, target: string) => void
  onEdit: (relationship: Relationship) => void
}

export default function RelationshipsTable({ 
  relationships,
  onDelete,
  onEdit
}: RelationshipsTableProps) {
  const [deleteConfirm, setDeleteConfirm] = useState<{
    source: string;
    target: string;
  } | null>(null)

  const handleDelete = async (source: string, target: string) => {
    try {
      const response = await fetch(`/api/relationships/${source}/${target}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        onDelete(source, target)
      }
    } catch (error) {
      console.error('Error deleting relationship:', error)
    }
    setDeleteConfirm(null)
  }

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Source</TableHead>
              <TableHead>Target</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Connection</TableHead>
              <TableHead>Strength</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-24">Actions</TableHead>
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
                <TableCell>{new Date(relationship.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onEdit(relationship)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteConfirm({
                        source: relationship.source,
                        target: relationship.target
                      })}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <AlertDialog 
        open={deleteConfirm !== null}
        onOpenChange={() => setDeleteConfirm(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Relationship</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the relationship between
              {deleteConfirm && <> <strong>{deleteConfirm.source}</strong> and <strong>{deleteConfirm.target}</strong></>}?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteConfirm && handleDelete(deleteConfirm.source, deleteConfirm.target)}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}