import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MatchResult } from "@/types/matcher";
import { CheckCircle2, AlertTriangle } from "lucide-react";

interface ScoreDisplayProps {
  result: MatchResult;
}

function getScoreColor(score: number): string {
  if (score >= 70) return "text-score-high";
  if (score >= 50) return "text-score-mid";
  return "text-score-low";
}

function getProgressColor(score: number): string {
  if (score >= 70) return "bg-score-high";
  if (score >= 50) return "bg-score-mid";
  return "bg-score-low";
}

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({ result }) => {
  return (
    <Card className="shadow-card-hover">
      <CardContent className="p-6 space-y-6">
        <div className="text-center space-y-2">
          <p className="text-sm font-semibold tracking-wide uppercase text-muted-foreground">
            Match Score
          </p>
          <div className={`text-7xl font-bold font-mono ${getScoreColor(result.score)}`}>
            {result.score}
          </div>
          <p className="text-xs text-muted-foreground">out of 100</p>
          <div className="max-w-xs mx-auto">
            <div className="relative h-3 w-full overflow-hidden rounded-full bg-secondary">
              <div
                className={`h-full rounded-full transition-all duration-700 ease-out ${getProgressColor(result.score)}`}
                style={{ width: `${result.score}%` }}
              />
            </div>
          </div>
        </div>

        <p className="text-sm text-muted-foreground text-center leading-relaxed max-w-lg mx-auto">
          {result.summary}
        </p>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-score-high" />
              <h4 className="text-sm font-semibold">Strengths</h4>
            </div>
            {result.strengths.map((item, i) => (
              <div key={i} className="p-3 rounded-lg bg-secondary/50 shadow-card space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{item.title}</span>
                  <Badge variant="secondary" className="font-mono text-xs">
                    {item.score}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-score-low" />
              <h4 className="text-sm font-semibold">Weaknesses</h4>
            </div>
            {result.weaknesses.map((item, i) => (
              <div key={i} className="p-3 rounded-lg bg-secondary/50 shadow-card space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{item.title}</span>
                  <Badge variant="destructive" className="font-mono text-xs">
                    {item.score}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ScoreDisplay;
