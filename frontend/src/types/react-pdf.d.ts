declare module 'react-pdf' {
  import { ReactElement, Component } from 'react';
  
  export interface DocumentProps {
    file: string | ArrayBuffer | { data: Uint8Array; };
    onLoadSuccess?: (document: { numPages: number }) => void;
    onLoadError?: (error: Error) => void;
    loading?: React.ReactNode;
    error?: React.ReactNode;
    className?: string;
    children?: React.ReactNode;
  }
  
  export interface PageProps {
    pageNumber: number;
    scale?: number;
    renderTextLayer?: boolean;
    renderAnnotationLayer?: boolean;
    width?: number;
    height?: number;
    className?: string;
  }
  
  export class Document extends Component<DocumentProps> {}
  export class Page extends Component<PageProps> {}
  
  export const pdfjs: {
    GlobalWorkerOptions: {
      workerSrc: string;
    };
    version: string;
  };
} 