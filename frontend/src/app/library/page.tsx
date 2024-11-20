"use client"
import React, { useState, useEffect } from 'react';
import { 
  Library,
  Upload,
  Search,
  Filter,
  ArrowUpDown,
  FileText,
  Trash2,
  MessageSquare,
  Image,
  Table as TableIcon,
  AlertCircle,
  Book,
  File,
  X
} from 'lucide-react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  CardDescription 
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
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
import {
  Toast,
  ToastProvider,
  ToastViewport,
  ToastDescription,
  ToastClose,
} from '@/components/ui/toast';
import FileRowActions from './file-row-actions';
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

const UploadModal = ({ isOpen, onClose, onUploadComplete }) => {
  const [uploadingFile, setUploadingFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState(null);

  const handleFileSelect = (event) => {
    const file = event?.target?.files?.[0];
    if (file) {
      setUploadingFile(file);
      setUploadProgress(0);
      setUploadStatus(null);
    }
  };

  const handleUpload = async () => {
    if (!uploadingFile) return;

    const formData = new FormData();
    formData.append('file', uploadingFile);

    try {
      setUploadStatus('uploading');
      setUploadProgress(0);

      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      setUploadProgress(100);
      setUploadStatus('complete');

      // Wait a bit before closing to show completion
      setTimeout(() => {
        onUploadComplete();
        onClose();
        setUploadingFile(null);
        setUploadProgress(0);
        setUploadStatus(null);
      }, 1000);

    } catch (err) {
      setUploadStatus('error');
      console.error('Upload error:', err);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer.files[0];
    if (file) {
      setUploadingFile(file);
      setUploadProgress(0);
      setUploadStatus(null);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Upload Documents</DialogTitle>
          <DialogDescription>
            Add new materials to the course library
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6 py-4">
          <div 
            className="border-2 border-dashed rounded-lg p-8 text-center space-y-4"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <Input
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.doc,.docx,.txt,.md"
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="flex flex-col items-center justify-center cursor-pointer"
            >
              <FileText className="w-12 h-12 text-muted-foreground mb-4" />
              <span className="text-lg font-medium">
                Drop files here or click to upload
              </span>
              <span className="text-sm text-muted-foreground">
                Supports PDF, DOC, DOCX, TXT, and MD files
              </span>
            </label>
          </div>

          {uploadingFile && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                <div className="flex items-center space-x-4">
                  <File className="w-6 h-6" />
                  <div>
                    <p className="font-medium">{uploadingFile.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {(uploadingFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                </div>
                <Button 
                  onClick={handleUpload} 
                  disabled={uploadStatus === 'uploading'}
                >
                  {uploadStatus === 'uploading' ? 'Uploading...' : 'Upload'}
                </Button>
              </div>

              {uploadStatus === 'uploading' && (
                <div className="space-y-2">
                  <Progress value={uploadProgress} />
                  <p className="text-sm text-center text-muted-foreground">
                    Uploading... {uploadProgress}%
                  </p>
                </div>
              )}

              {uploadStatus === 'complete' && (
                <div className="bg-green-50 p-4 rounded-lg text-green-800">
                  File uploaded successfully!
                </div>
              )}

              {uploadStatus === 'error' && (
                <div className="bg-red-50 p-4 rounded-lg text-red-800">
                  Upload failed. Please try again.
                </div>
              )}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

const FileContentModal = ({ isOpen, onClose, file }) => {
  // ... existing FileContentModal component code ...
};

const DocumentTypeBadge = ({ type, subType }) => {
  // ... existing DocumentTypeBadge component code ...
};

export default function LibraryPage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isFileModalOpen, setIsFileModalOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState(null);
  const [toastState, setToastState] = useState({ open: false, message: '', variant: 'default' });

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

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleUploadComplete = async () => {
    setToastState({
      open: true,
      message: 'File uploaded successfully',
      variant: 'default'
    });
    await fetchFiles();
  };

  const formatFileType = (type) => {
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
          <Library className="w-8 h-8" />
          <h1 className="text-3xl font-bold">Document Library</h1>
        </div>
        <div className="mt-8 text-center">Loading files...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="flex items-center space-x-4">
          <Library className="w-8 h-8" />
          <h1 className="text-3xl font-bold">Document Library</h1>
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
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Library className="w-8 h-8" />
            <div>
              <h1 className="text-3xl font-bold">Document Library</h1>
              <p className="text-sm text-muted-foreground">
                Course materials and references
              </p>
            </div>
          </div>
          <Button 
            onClick={() => setIsUploadModalOpen(true)}
            className="flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            Upload
          </Button>
        </div>

        {/* File Browser */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Files</CardTitle>
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-2 px-4 py-2 border rounded-md">
                  <Filter className="w-4 h-4" />
                  Filters
                </button>
                <button className="flex items-center gap-2 px-4 py-2 border rounded-md">
                  <ArrowUpDown className="w-4 h-4" />
                  Sort
                </button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input 
                  className="w-full pl-10 pr-4 py-2 border rounded-md" 
                  placeholder="Search files..."
                />
              </div>
            </div>

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
                          setIsFileModalOpen(true);
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

        <UploadModal 
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          onUploadComplete={handleUploadComplete}
        />

        <FileContentModal 
          isOpen={isFileModalOpen}
          onClose={() => {
            setIsFileModalOpen(false);
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