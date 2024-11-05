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
import Papa from 'papaparse';

const TableViewer = ({ file }) => {
  const [selectedTable, setSelectedTable] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [tableData, setTableData] = useState([]);
  const [tableMeta, setTableMeta] = useState(null);
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState(null);

  // Early return if file has no tables
  if (!file.has_tables || !file.processed_paths?.tables) {
    return null;
  }

  const tables = file.processed_paths.tables;

  const loadTableContent = async (tableName) => {
    try {
      setLoading(true);
      setTableData([]);
      setDebugInfo(null);
      
      // Load table metadata
      const metaResponse = await fetch(`/api/files/${file.id}/tables/metadata`);
      if (!metaResponse.ok) throw new Error('Failed to load table metadata');
      const metadata = await metaResponse.json();
      setTableMeta(metadata[tableName]);

      // Load table CSV data
      const response = await fetch(`/api/files/${file.id}/tables/${tableName}`);
      if (!response.ok) throw new Error('Failed to load table');
      const rawResponse = await response.json();
      const csvText = rawResponse.content;

      // Debug log
      console.log('Raw CSV text:', csvText);
      
      // Parse CSV with explicit configuration
      Papa.parse(csvText, {
        delimiter: ',',
        newline: '\n',
        header: false,
        skipEmptyLines: true,
        complete: (results) => {
          console.log('Parsed results:', results);
          setDebugInfo({
            rowCount: results.data.length,
            firstRowCells: results.data[0]?.length,
            sampleRow: results.data[0]
          });
          setTableData(results.data);
        },
        error: (error) => {
          console.error('Papa Parse error:', error);
          setDebugInfo({ error: error.message });
        }
      });
    } catch (error) {
      console.error('Error loading table:', error);
      setDebugInfo({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const renderTable = () => {
    if (!tableData.length) return null;

    // Debug display
    if (debugInfo) {
      console.log('Debug info:', debugInfo);
    }

    return (
      <div className="space-y-4">
        {debugInfo && (
          <div className="bg-gray-100 p-4 rounded-lg text-sm font-mono">
            <div>Rows: {debugInfo.rowCount}</div>
            <div>Columns: {debugInfo.firstRowCells}</div>
            <div>First row: {JSON.stringify(debugInfo.sampleRow)}</div>
          </div>
        )}
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                {tableData[0]?.map((header, i) => (
                  <th 
                    key={i}
                    className="border border-gray-300 bg-gray-100 px-4 py-2 text-left font-medium"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableData.slice(1).map((row, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  {row.map((cell, j) => (
                    <td 
                      key={j}
                      className="border border-gray-300 px-4 py-2 whitespace-normal break-words"
                    >
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
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
                setSelectedTable(tableName);
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
        <DialogContent className="max-w-6xl h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>
              {selectedTable}
              {tableMeta && (
                <span className="ml-2 text-sm text-gray-500">
                  ({tableMeta.num_rows} rows, {tableMeta.num_cols} columns)
                </span>
              )}
            </DialogTitle>
          </DialogHeader>
          <div className="flex-1 overflow-auto p-4">
            {loading ? (
              <div className="flex items-center justify-center w-full h-full">
                <div className="animate-pulse">Loading table...</div>
              </div>
            ) : (
              renderTable()
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default TableViewer;