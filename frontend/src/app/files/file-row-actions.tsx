import React from 'react';
import { Button } from '@/components/ui/button';
import { FileText, Trash2 } from 'lucide-react';
import ImageViewer from './ImageViewer';
import TableViewer from './TableViewer';

const FileRowActions = ({ file, onViewContent, onDeleteClick }) => {
  const { has_tables, table_count } = file;

  return (
    <div className="flex justify-end space-x-2">
      <ImageViewer file={file} />
      {has_tables && <TableViewer file={file} />}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onViewContent(file)}
      >
        <FileText className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onDeleteClick(file)}
      >
        <Trash2 className="h-4 w-4 text-red-500" />
      </Button>
    </div>
  );
};

export default FileRowActions;