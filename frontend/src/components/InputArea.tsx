import React, { useCallback } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, FileText } from "lucide-react";

interface InputAreaProps {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  fileName: string | null;
  onFileSelect: (file: File) => void;
  children?: React.ReactNode;
}

const InputArea: React.FC<InputAreaProps> = ({
  label,
  placeholder,
  value,
  onChange,
  fileName,
  onFileSelect,
  children,
}) => {
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) onFileSelect(file);
    },
    [onFileSelect]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onFileSelect(file);
    },
    [onFileSelect]
  );

  return (
    <Card className="flex-1 shadow-card hover:shadow-card-hover transition-shadow duration-200">
      <CardContent className="p-5">
        <h3 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground mb-3">
          {label}
        </h3>
        <Tabs defaultValue="text">
          <TabsList className="w-full mb-3">
            <TabsTrigger value="text" className="flex-1">Paste Text</TabsTrigger>
            <TabsTrigger value="upload" className="flex-1">Upload File</TabsTrigger>
            {children && <TabsTrigger value="saved" className="flex-1">Saved</TabsTrigger>}
          </TabsList>
          <TabsContent value="text">
            <Textarea
              placeholder={placeholder}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              className="min-h-[200px] resize-none font-mono text-sm"
            />
          </TabsContent>
          <TabsContent value="upload">
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className="border-2 border-dashed border-border rounded-xl p-8 text-center min-h-[200px] flex flex-col items-center justify-center gap-3 hover:border-accent hover:bg-accent/5 transition-all cursor-pointer"
              onClick={() => document.getElementById(`file-${label}`)?.click()}
            >
              {fileName ? (
                <>
                  <FileText className="h-10 w-10 text-accent" />
                  <p className="text-sm font-medium">{fileName}</p>
                  <p className="text-xs text-muted-foreground">Click or drag to replace</p>
                </>
              ) : (
                <>
                  <Upload className="h-10 w-10 text-muted-foreground" />
                  <p className="text-sm font-medium">Drop your file here</p>
                  <p className="text-xs text-muted-foreground">
                    PDF, DOCX, or TXT — max 5MB
                  </p>
                </>
              )}
              <input
                id={`file-${label}`}
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleFileInput}
                className="hidden"
              />
            </div>
          </TabsContent>
          {children && <TabsContent value="saved">{children}</TabsContent>}
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default InputArea;
