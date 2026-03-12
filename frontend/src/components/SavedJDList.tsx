import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { SavedJD, ComparisonHistory } from "@/types/matcher";
import { Briefcase, Calendar, Check, FileText, Eye, ScrollText } from "lucide-react";

const API = "/api";

interface SavedJDListProps {
  jds: SavedJD[];
  onSelect?: (jd: SavedJD) => void;
  selectedJdId?: string | null;
  compact?: boolean;
}

const SavedJDList: React.FC<SavedJDListProps> = ({ jds, onSelect, selectedJdId, compact }) => {
  const [viewJD, setViewJD] = useState<SavedJD | null>(null);
  const [viewResume, setViewResume] = useState<ComparisonHistory | null>(null);

  if (jds.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground text-sm">
        No saved job descriptions yet.
      </div>
    );
  }

  return (
    <>
      <div className="space-y-3">
        {jds.map((jd) => {
          const isSelected = selectedJdId != null && jd.id === selectedJdId;
          return (
          <div
            key={jd.id}
            className={`p-4 rounded-xl border bg-card shadow-card hover:shadow-card-hover transition-all duration-200 ${
              onSelect ? "cursor-pointer" : ""
            } ${isSelected ? "ring-2 ring-primary border-primary bg-primary/5" : ""}`}
            onClick={() => onSelect?.(jd)}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="space-y-1.5 min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-semibold truncate">{jd.title}</h4>
                  {isSelected && (
                    <Check className="h-4 w-4 shrink-0 text-primary" aria-hidden />
                  )}
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Briefcase className="h-3 w-3" />
                  <span>{jd.company}</span>
                  <Calendar className="h-3 w-3 ml-1" />
                  <span>{jd.savedAt}</span>
                </div>
                {!compact && (
                  <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                    {jd.snippet}
                  </p>
                )}
              </div>
              <div className="flex items-center gap-1 flex-shrink-0">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  title="View JD content"
                  onClick={(e) => {
                    e.stopPropagation();
                    setViewJD(jd);
                  }}
                >
                  <Eye className="h-4 w-4 text-muted-foreground" />
                </Button>
                {jd.comparisons.length > 0 && (
                  <Badge variant="secondary" className="text-xs">
                    <FileText className="h-3 w-3 mr-1" />
                    {jd.comparisons.length}
                  </Badge>
                )}
              </div>
            </div>

            {!compact && jd.comparisons.length > 0 && (
              <div className="mt-3 space-y-1.5">
                {jd.comparisons.map((comp, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between text-xs p-2.5 rounded-lg bg-secondary/50"
                  >
                    <div className="flex items-center gap-2 truncate">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 flex-shrink-0"
                        title="View resume details"
                        onClick={(e) => {
                          e.stopPropagation();
                          setViewResume(comp);
                        }}
                      >
                        <ScrollText className="h-3.5 w-3.5 text-muted-foreground" />
                      </Button>
                      <span className="truncate">{comp.resumeName}</span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-muted-foreground">{comp.comparedAt}</span>
                      <span className="font-mono font-bold">{comp.score}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          );
        })}
      </div>

      {/* JD Content Modal: fixed header + iframe */}
      <Dialog open={!!viewJD} onOpenChange={() => setViewJD(null)}>
        <DialogContent className="max-w-4xl h-[85vh] flex flex-col p-0 gap-0 shadow-elevated overflow-hidden">
          <DialogHeader className="flex-shrink-0 sticky top-0 z-10 bg-card border-b px-6 py-4">
            <DialogTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5 text-primary" />
              {viewJD?.title}
            </DialogTitle>
            {viewJD && (
              <p className="text-sm text-muted-foreground">
                {viewJD.company ? `${viewJD.company} · ` : ""}Saved {viewJD.savedAt}
              </p>
            )}
          </DialogHeader>
          {viewJD && (
            <iframe
              title={`Job description: ${viewJD.title}`}
              src={`${API}/jds/${viewJD.id}/file`}
              className="flex-1 w-full min-h-0 border-0"
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Resume Content Modal: fixed header + iframe */}
      <Dialog open={!!viewResume} onOpenChange={() => setViewResume(null)}>
        <DialogContent className="max-w-4xl h-[85vh] flex flex-col p-0 gap-0 shadow-elevated overflow-hidden">
          <DialogHeader className="flex-shrink-0 sticky top-0 z-10 bg-card border-b px-6 py-4">
            <DialogTitle className="flex items-center gap-2">
              <ScrollText className="h-5 w-5 text-primary" />
              {viewResume?.resumeName ?? "Resume"}
            </DialogTitle>
            {viewResume && (
              <p className="text-sm text-muted-foreground">
                Score: <span className="font-mono font-semibold">{viewResume.score}</span>
                {viewResume.comparedAt && ` · Compared ${viewResume.comparedAt}`}
              </p>
            )}
          </DialogHeader>
          {viewResume?.resumeUuid && (
            <iframe
              title={viewResume.resumeName}
              src={`${API}/resumes/${viewResume.resumeUuid}/file`}
              className="flex-1 w-full min-h-0 border-0"
            />
          )}
          {viewResume && !viewResume.resumeUuid && (
            <div className="flex-1 flex items-center justify-center p-6 text-muted-foreground text-sm">
              Resume file not available for this comparison.
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default SavedJDList;
