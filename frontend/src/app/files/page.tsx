'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import FileRowActions from './file-row-actions';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { ScrollArea } from '@/components/ui/scroll-area';
import { FolderOpen, FileText, Trash2 } from 'lucide-react';
import { 
  Toast,
  ToastProvider, 
  ToastViewport,
  ToastDescription,
  ToastClose,
} from '@/components/ui/toast';
import LaTeXViewer from "@/components/MarkdownLatexViewer";

const statusColors = {
  uploaded: 'bg-blue-100 text-blue-800',
  processing: 'bg-yellow-100 text-yellow-800',
  complete: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
  metadata_complete: 'bg-green-100 text-green-800',
  processing_queued: 'bg-yellow-100 text-yellow-800',
  unknown: 'bg-gray-100 text-gray-800'
};

const FileContentModal = ({ isOpen, onClose, file }) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContent = async () => {
      if (!file?.id) return;
      
      try {
        setLoading(true);
        const response = await fetch(`/api/files/${file.id}/content`);
        if (!response.ok) throw new Error('Failed to fetch content');
        const data = await response.json();
        setContent(data.content || '');
      } catch (error) {
        console.error('Error fetching content:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, [file?.id]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl h-[80vh] flex flex-col p-0">
        <DialogHeader className="p-6 pb-2">
          <DialogTitle>{file?.name}</DialogTitle>
        </DialogHeader>
        <ScrollArea className="flex-1 p-6 pt-0">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-pulse text-muted-foreground">Loading content...</div>
            </div>
          ) : (
            <pre className="text-sm whitespace-pre-wrap font-mono bg-muted p-4 rounded-lg">
              <LaTeXViewer content={content} />
            </pre>
          )}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

const DocumentTypeBadge = ({ type, subType }) => {
  if (!type) return null;
  
  return (
    <div className="space-y-1">
      <Badge variant="secondary" className="capitalize">
        {type}
      </Badge>
      {subType && (
        <div className="text-xs text-muted-foreground capitalize">
          {subType}
        </div>
      )}
    </div>
  );
};

export default function FileBrowserPage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState(null);
  const [toastState, setToastState] = useState({ open: false, message: '', variant: 'default' });

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/files');
        if (!response.ok) throw new Error('Failed to fetch files');
        const data = await response.json();
        setFiles(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
  
    fetchFiles();
  }, []);

  const formatFileType = (type: string) => {
    if (type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      return 'docx';
    }
    return type.split('/').pop();
  };

  const handleDelete = async (file) => {
    try {
      const response = await fetch(`/api/files/${file.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete file');
      }

      // Remove file from state
      setFiles(files.filter(f => f.id !== file.id));
      setToastState({ 
        open: true, 
        message: "File deleted successfully",
        variant: 'default'
      });
    } catch (error) {
      console.error('Error deleting file:', error);
      setToastState({ 
        open: true, 
        message: "Failed to delete file. Please try again.",
        variant: 'destructive'
      });
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center space-x-4">
          <FolderOpen className="w-8 h-8" />
          <h1 className="text-3xl font-bold">File Browser</h1>
        </div>
        <div className="mt-8 text-center">Loading files...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="flex items-center space-x-4">
          <FolderOpen className="w-8 h-8" />
          <h1 className="text-3xl font-bold">File Browser</h1>
        </div>
        <div className="mt-8 p-4 bg-red-50 text-red-800 rounded-lg">
          Error loading files: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-4">
          <FolderOpen className="w-8 h-8" />
          <h1 className="text-3xl font-bold">File Browser</h1>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Files</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Document Type</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Upload Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {files.map((file) => (
                  <TableRow key={file.id}>
                    <TableCell className="font-medium">{file.name}</TableCell>
                    <TableCell>{formatFileType(file.type)}</TableCell>
                    <TableCell>
                      <DocumentTypeBadge 
                        type={file.metadata?.documentMetadata?.primaryType?.category}
                        subType={file.metadata?.documentMetadata?.primaryType?.subType}
                      />
                    </TableCell>
                    <TableCell>{(file.size / 1024).toFixed(2)} KB</TableCell>
                    <TableCell>{new Date(file.upload_date).toLocaleString()}</TableCell>
                    <TableCell>
                      <Badge className={statusColors[file.status]}>
                        {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <FileRowActions
                        file={file}
                        onViewContent={() => {
                          setSelectedFile(file);
                          setIsModalOpen(true);
                        }}
                        onDeleteClick={() => {
                          setFileToDelete(file);
                          setDeleteDialogOpen(true);
                        }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <FileContentModal 
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedFile(null);
          }}
          file={selectedFile}
        />

        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This will permanently delete {fileToDelete?.name}. This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                className="bg-red-500 hover:bg-red-600"
                onClick={() => {
                  handleDelete(fileToDelete);
                  setDeleteDialogOpen(false);
                }}
              >
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        <ToastProvider>
          <Toast 
            open={toastState.open} 
            onOpenChange={(open) => setToastState(prev => ({ ...prev, open }))}
            variant={toastState.variant}
          >
            <div className="grid gap-1">
              <ToastDescription>{toastState.message}</ToastDescription>
            </div>
            <ToastClose />
          </Toast>
          <ToastViewport />
        </ToastProvider>
      </div>
    </div>
  );
}