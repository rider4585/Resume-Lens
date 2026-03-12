import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Lightbulb } from "lucide-react";

interface RecommendationsProps {
  recommendations: string[];
}

const Recommendations: React.FC<RecommendationsProps> = ({ recommendations }) => {
  return (
    <Card className="shadow-card-hover">
      <CardContent className="p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-accent" />
          <h3 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground">
            Recommendations to Improve
          </h3>
        </div>
        <ol className="space-y-3">
          {recommendations.map((rec, i) => (
            <li key={i} className="flex gap-3 p-3 rounded-lg bg-secondary/50 shadow-card">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-accent text-accent-foreground text-xs font-bold flex items-center justify-center">
                {i + 1}
              </span>
              <p className="text-sm leading-relaxed">{rec}</p>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
};

export default Recommendations;
