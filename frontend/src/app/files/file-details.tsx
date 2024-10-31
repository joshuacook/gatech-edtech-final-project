"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { 
  File, 
  Clock, 
  FileText,
  Download,
  Copy,
  Check,
  ExternalLink
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const statusColors = {
  uploaded: 'bg-blue-100 text-blue-800',
  processing: 'bg-yellow-100 text-yellow-800',
  complete: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800'
} as const;

type FileStatus = keyof typeof statusColors;

const FileContent = ({ file }: { file: any }) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        setLoading(true);
        setError(null);
        // Use the content endpoint instead of metadata
        const response = await fetch(`/api/files/${file.id}/content`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to fetch content');
        }
        const data = await response.json();
        setContent(data.content || ''); // Use empty string as fallback
      } catch (error) {
        setError(error instanceof Error ? error.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    if (file?.id) {
      fetchContent();
    }
  }, [file?.id]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-muted-foreground">Loading content...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>Error loading content: {error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="space-x-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleCopy}
          >
            {copied ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
            {copied ? 'Copied!' : 'Copy Content'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            asChild
          >
            <a href={`/api/files/${file.id}/download/markdown`} download>
              <Download className="w-4 h-4 mr-2" />
              Download
            </a>
          </Button>
        </div>
        <span className="text-sm text-muted-foreground">
          {content.length.toLocaleString()} characters
        </span>
      </div>
      
      <Card>
        <CardContent className="p-4 max-h-[800px] overflow-auto">
          <pre className="text-sm whitespace-pre-wrap font-mono bg-muted p-4 rounded-lg">
            {content}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
};

const FileMetadata = ({ file }: { file: { status: FileStatus; id?: string; [key: string]: any } }) => {
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/files/${file.id}/metadata`);
        if (!response.ok) throw new Error('Failed to fetch metadata');
        const data = await response.json();
        setMetadata(data);
      } catch (error) {
        console.error('Error fetching metadata:', error);
      } finally {
        setLoading(false);
      }
    };

    if (file?.id) {
      fetchMetadata();
    }
  }, [file?.id]);

  if (loading) {
    return <div>Loading metadata...</div>;
  }

  return (
    <Card>
      <CardContent className="p-4">
        <pre className="text-sm whitespace-pre-wrap font-mono bg-muted p-4 rounded-lg overflow-auto">
          {JSON.stringify(metadata, null, 2)}
        </pre>
      </CardContent>
    </Card>
  );
};

const FileDetails = ({ file }: { file: { status: FileStatus; [key: string]: any } }) => {
  if (!file) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">{file.name}</h2>
          <p className="text-sm text-muted-foreground">
            Uploaded {new Date(file.upload_date).toLocaleString()}
          </p>
        </div>
        <Badge className={statusColors[file.status]}>
          {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
        </Badge>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <File className="w-4 h-4 text-muted-foreground" />
              <p className="text-sm font-medium">Size</p>
            </div>
            <p className="text-2xl">{(file.size / 1024).toFixed(2)} KB</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-muted-foreground" />
              <p className="text-sm font-medium">Type</p>
            </div>
            <p className="text-2xl">{file.type.split('/').pop()}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <p className="text-sm font-medium">Processing Time</p>
            </div>
            <p className="text-2xl">
              {file.processed_date ? 
                `${Math.round((new Date(file.processed_date).getTime() - new Date(file.upload_date).getTime()) / 1000)}s` : 
                'N/A'}
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="content">
        <TabsList>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="metadata">Metadata</TabsTrigger>
        </TabsList>

        <TabsContent value="content" className="mt-4">
          <FileContent file={file} />
        </TabsContent>

        <TabsContent value="metadata" className="mt-4">
          <FileMetadata file={file} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FileDetails;