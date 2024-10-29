'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FolderOpen, File, Clock, ArrowUpCircle, CheckCircle, AlertCircle } from 'lucide-react';

const statusColors = {
  uploaded: 'bg-blue-100 text-blue-800',
  processing: 'bg-yellow-100 text-yellow-800',
  complete: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800'
};

const FilePreview = ({ file }: { file: any }) => {
  if (!file) return null;

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle>File Details: {file.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-sm font-medium">File Information</p>
            <div className="bg-muted p-4 rounded-lg space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Size:</span>
                <span className="text-sm font-medium">{file.size}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Type:</span>
                <span className="text-sm font-medium">{file.type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Uploaded:</span>
                <span className="text-sm font-medium">{file.uploadDate}</span>
              </div>
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium">Processing Status</p>
            <div className="bg-muted p-4 rounded-lg space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Status:</span>
                <Badge className={statusColors[file.status as keyof typeof statusColors]}>
                  {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                </Badge>
              </div>
              {file.processedDate && (
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Processed:</span>
                  <span className="text-sm font-medium">{file.processedDate}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {file.preview && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Content Preview</p>
            <div className="bg-muted p-4 rounded-lg">
              <pre className="text-sm whitespace-pre-wrap">{file.preview}</pre>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const FileBrowserPage = () => {
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call to fetch files
    const fetchFiles = async () => {
      try {
        const response = await fetch('/api/files');
        const data = await response.json();
        setFiles(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error('Error fetching files:', error);
        setFiles([]);
      } finally {
        setLoading(false);
      }
    };

    fetchFiles();
  }, []);

  const statsCards = [
    {
      icon: <File className="w-5 h-5" />,
      title: "Total Files",
      value: files.length
    },
    {
      icon: <Clock className="w-5 h-5" />,
      title: "Processing",
      value: files.filter((f: any) => f.status === 'processing').length
    },
    {
      icon: <CheckCircle className="w-5 h-5" />,
      title: "Completed",
      value: files.filter((f: any) => f.status === 'complete').length
    }
  ];

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-4">
          <FolderOpen className="w-8 h-8" />
          <h1 className="text-3xl font-bold">File Browser</h1>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {statsCards.map((card, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex items-center space-x-4">
                  {card.icon}
                  <div>
                    <p className="text-sm font-medium">{card.title}</p>
                    <p className="text-2xl font-bold">{card.value}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Tabs defaultValue="all">
          <TabsList>
            <TabsTrigger value="all">All Files</TabsTrigger>
            <TabsTrigger value="processing">Processing</TabsTrigger>
            <TabsTrigger value="complete">Complete</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-4">
            <Card>
              <CardContent className="pt-6">
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
                    {files.map((file: any) => (
                      <TableRow key={file.id}>
                        <TableCell className="font-medium">{file.name}</TableCell>
                        <TableCell>{file.type}</TableCell>
                        <TableCell>{file.size}</TableCell>
                        <TableCell>{file.uploadDate}</TableCell>
                        <TableCell>
                          <Badge className={statusColors[file.status as keyof typeof statusColors]}>
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

            {selectedFile && <FilePreview file={selectedFile} />}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default FileBrowserPage;