import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { FileStack } from 'lucide-react';

const MetadataViewer = ({ file }) => {
  const [isOpen, setIsOpen] = useState(false);

  // Early return if file has no metadata
  if (!file.metadata?.documentMetadata) {
    return null;
  }

  const { documentMetadata } = file.metadata;

  // Format confidence as percentage
  const formatConfidence = (value: number) => `${Math.round(value)}%`;

  return (
    <>
      <Button 
        variant="ghost" 
        size="icon"
        onClick={() => setIsOpen(true)}
        className="relative"
      >
        <FileStack className="h-4 w-4" />
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Document Analysis</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* Summary */}
            <div className="text-sm text-muted-foreground">
              {file.metadata.summary}
            </div>

            {/* Document Type */}
            <div className="space-y-1.5">
              <div className="text-sm font-medium">Document Type</div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="capitalize">
                  {documentMetadata.primaryType.category}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  ({documentMetadata.primaryType.subType})
                </span>
                <Badge className="ml-auto">
                  {formatConfidence(documentMetadata.primaryType.confidence)}
                </Badge>
              </div>
            </div>

            {/* Target Audience */}
            <div className="space-y-1.5">
              <div className="text-sm font-medium">Target Audience</div>
              <div className="space-y-1">
                {documentMetadata.contentProperties.targetAudience.map((audience, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="capitalize text-sm">{audience.type}</span>
                    <Badge>{formatConfidence(audience.confidence)}</Badge>
                  </div>
                ))}
              </div>
            </div>

            {/* Content Properties */}
            <div className="space-y-1.5">
              <div className="text-sm font-medium">Content Properties</div>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center">
                  <span>Formality: <span className="text-muted-foreground capitalize">{documentMetadata.contentProperties.formalityLevel.value}</span></span>
                  <Badge>{formatConfidence(documentMetadata.contentProperties.formalityLevel.confidence)}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span>Time Sensitivity: <span className="text-muted-foreground capitalize">{documentMetadata.contentProperties.timeSensitivity.value}</span></span>
                  <Badge>{formatConfidence(documentMetadata.contentProperties.timeSensitivity.confidence)}</Badge>
                </div>
              </div>
            </div>

            {/* Quality Score */}
            <div className="space-y-1.5">
              <div className="text-sm font-medium">Quality Assessment</div>
              <div className="flex items-center justify-between">
                <div className="text-2xl font-bold">
                  {documentMetadata.qualityAssessment.overallQuality.score}/100
                </div>
                <Badge>{formatConfidence(documentMetadata.qualityAssessment.overallQuality.confidence)}</Badge>
              </div>
              <div className="grid grid-cols-2 gap-3 mt-2">
                {Object.entries(documentMetadata.qualityAssessment.coherence).map(([key, value]) => (
                  <div key={key} className="text-sm">
                    <div className="text-muted-foreground capitalize">
                      {key.replace(/([A-Z])/g, ' $1').trim()}
                    </div>
                    <div className="font-medium">{value}/100</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default MetadataViewer;