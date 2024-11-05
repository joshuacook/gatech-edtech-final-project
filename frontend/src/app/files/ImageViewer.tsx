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
import { Image } from 'lucide-react';

const ImageViewer = ({ file }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Early return if file has no images
  if (!file.has_images || !file.processed_paths?.images) {
    return null;
  }

  const images = file.processed_paths.images;

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="relative">
            <Image className="h-4 w-4" />
            <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-blue-100 text-blue-600 text-xs flex items-center justify-center">
              {file.image_count}
            </span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          {Object.entries(images).map(([filename, path]) => (
            <DropdownMenuItem
              key={filename}
              onClick={() => {
                setSelectedImage({ name: filename, path: filename });
                setIsModalOpen(true);
              }}
              className="flex items-center gap-2"
            >
              <Image className="h-4 w-4" />
              <span className="truncate">{filename}</span>
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>{selectedImage?.name}</DialogTitle>
          </DialogHeader>
          <div className="flex-1 overflow-auto flex items-center justify-center p-4">
            {selectedImage && (
              <img
                src={`/api/files/${file.id}/images/${selectedImage.path}`}
                alt={selectedImage.name}
                className="max-w-full max-h-full object-contain"
              />
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ImageViewer;