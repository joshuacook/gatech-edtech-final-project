'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { FolderOpen, File, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import FileDetails from './file-details';

const statusColors = {
  uploaded: 'bg-blue-100 text-blue-800',
  processing: 'bg-yellow-100 text-yellow-800',
  complete: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800'
};

export default function FileBrowserPage() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
    // Set up polling for status updates
    const interval = setInterval(fetchFiles, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

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

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-4">
                <File className="w-5 h-5" />
                <div>
                  <p className="text-sm font-medium">Total Files</p>
                  <p className="text-2xl font-bold">{files.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-4">
                <Clock className="w-5 h-5" />
                <div>
                  <p className="text-sm font-medium">Processing</p>
                  <p className="text-2xl font-bold">
                    {files.filter(f => f.status === 'processing').length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-4">
                <CheckCircle className="w-5 h-5" />
                <div>
                  <p className="text-sm font-medium">Complete</p>
                  <p className="text-2xl font-bold">
                    {files.filter(f => f.status === 'complete').length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-4">
                <AlertCircle className="w-5 h-5" />
                <div>
                  <p className="text-sm font-medium">Errors</p>
                  <p className="text-2xl font-bold">
                    {files.filter(f => f.status === 'error').length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Files Table */}
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
                  <TableHead>Size</TableHead>
                  <TableHead>Upload Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {files.map((file) => (
                  <TableRow key={file.id} className={selectedFile?.id === file.id ? 'bg-muted' : ''}>
                    <TableCell className="font-medium">{file.name}</TableCell>
                    <TableCell>{file.type.split('/').pop()}</TableCell>
                    <TableCell>{(file.size / 1024).toFixed(2)} KB</TableCell>
                    <TableCell>{new Date(file.upload_date).toLocaleString()}</TableCell>
                    <TableCell>
                      <Badge className={statusColors[file.status]}>
                        {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedFile(file)}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* File Details */}
        {selectedFile && (
          <FileDetails 
            file={selectedFile} 
            onClose={() => setSelectedFile(null)} 
          />
        )}
      </div>
    </div>
  );
}