import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Table as TableIcon } from 'lucide-react';

const TableViewer = ({ file }) => {
    const [selectedTable, setSelectedTable] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [tableContent, setTableContent] = useState('');
    const [loading, setLoading] = useState(false);
  
    // Early return if file has no tables
    if (!file.has_tables || !file.processed_paths?.tables) {
      return null;
    }
  
    const tables = file.processed_paths.tables;
  
    const loadTableContent = async (tableName) => {
      try {
        setLoading(true);
        const response = await fetch(`/api/files/${file.id}/tables/${tableName}`);
        if (!response.ok) throw new Error('Failed to load table');
        const data = await response.json();
        setTableContent(data.content);
      } catch (error) {
        console.error('Error loading table:', error);
      } finally {
        setLoading(false);
      }
    };
  
    return (
      <>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <TableIcon className="h-4 w-4" />
              <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-blue-100 text-blue-600 text-xs flex items-center justify-center">
                {file.table_count}
              </span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            {Object.entries(tables).map(([tableName]) => (
              <DropdownMenuItem
                key={tableName}
                onClick={async () => {
                  setSelectedTable({ name: tableName });
                  setIsModalOpen(true);
                  await loadTableContent(tableName);
                }}
                className="flex items-center gap-2"
              >
                <TableIcon className="h-4 w-4" />
                <span className="truncate">Table {tableName}</span>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
  
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
            <DialogHeader>
              <DialogTitle>{selectedTable?.name}</DialogTitle>
            </DialogHeader>
            <div className="flex-1 overflow-auto flex items-start justify-center p-4">
              {loading ? (
                <div className="flex items-center justify-center w-full h-full">
                  <div className="animate-pulse">Loading table...</div>
                </div>
              ) : (
                <div className="w-full overflow-auto">
                  <div 
                    className="prose max-w-none" 
                    dangerouslySetInnerHTML={{ __html: tableContent }}
                  />
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </>
    );
  };

export default TableViewer;