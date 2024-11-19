import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Eye } from 'lucide-react';

const FileViewer = ({ file }) => {
  const [isOpen, setIsOpen] = useState(false);
  console.log(file);

  // Only show viewer for supported file types
  const supportedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/gif'];
  if (!supportedTypes.includes(file.type)) {
    return null;
  }

  const renderContent = () => {
    if (file.type === 'application/pdf') {
      return (
        <iframe 
          src={file.file_path.replace('/app/filestore', '/files')}
          className="w-full h-full border-0"
          title={file.name}
        />
      );
    }

    if (file.type.startsWith('image/')) {
      return (
        <img 
          src={file.file_path.replace('/app/filestore', '/files')}
          alt={file.name}
          className="max-w-full max-h-full object-contain"
        />
      );
    }
  };

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsOpen(true)}
      >
        <Eye className="h-4 w-4" />
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>{file.name}</DialogTitle>
          </DialogHeader>
          <div className="flex-1 overflow-auto flex items-center justify-center p-4">
            {renderContent()}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default FileViewer;