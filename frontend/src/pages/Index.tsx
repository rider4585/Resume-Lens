import React, { useState, useCallback, useEffect } from "react";
import InputArea from "@/components/InputArea";
import ScoreDisplay from "@/components/ScoreDisplay";
import Recommendations from "@/components/Recommendations";
import SavedJDList from "@/components/SavedJDList";
import LoadingButton from "@/components/LoadingButton";
import ThemeToggle from "@/components/ThemeToggle";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { compareResume, getRecommendations, getSavedJDs } from "@/lib/api";
import { MatchResult, SavedJD } from "@/types/matcher";
import { GitCompareArrows, BookOpen, Sparkles } from "lucide-react";

const Index = () => {
  const [resumeText, setResumeText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [jdFile, setJdFile] = useState<File | null>(null);

  const [comparing, setComparing] = useState(false);
  const [compareError, setCompareError] = useState<string | null>(null);
  const [result, setResult] = useState<MatchResult | null>(null);

  const [loadingRecs, setLoadingRecs] = useState(false);
  const [recommendations, setRecommendations] = useState<string[] | null>(null);

  const [savedJDs, setSavedJDs] = useState<SavedJD[]>([]);
  const [savedJDsLoading, setSavedJDsLoading] = useState(true);
  const [selectedJdId, setSelectedJdId] = useState<string | null>(null);

  useEffect(() => {
    getSavedJDs()
      .then(setSavedJDs)
      .catch(() => setSavedJDs([]))
      .finally(() => setSavedJDsLoading(false));
  }, []);

  const hasInput = (resumeText.trim() || resumeFile) && (jdText.trim() || jdFile);

  const handleCompare = useCallback(async () => {
    setComparing(true);
    setCompareError(null);
    setResult(null);
    setRecommendations(null);
    try {
      let jdContent = jdText.trim();
      if (jdFile && !jdContent) {
        jdContent = await readFileAsText(jdFile).catch(() => "");
      }
      const { match, resumeText: apiResumeText } = await compareResume(
        resumeText,
        resumeFile,
        jdContent,
        jdFile,
        selectedJdId,
        !selectedJdId
      );
      setResult(match);
      setLastResumeTextFromApi(apiResumeText ?? null);
      getSavedJDs().then(setSavedJDs);
    } catch (e) {
      setCompareError(e instanceof Error ? e.message : "Compare failed");
    } finally {
      setComparing(false);
    }
  }, [resumeText, resumeFile, jdText, jdFile, selectedJdId]);

  const [lastResumeTextFromApi, setLastResumeTextFromApi] = useState<string | null>(null);

  const handleGetRecommendations = useCallback(async () => {
    if (!result) return;
    let resumeContent = lastResumeTextFromApi ?? resumeText.trim();
    if (!resumeContent && resumeFile && (resumeFile.type === "text/plain" || resumeFile.name.endsWith(".txt"))) {
      resumeContent = await readFileAsText(resumeFile).catch(() => "");
    }
    if (!resumeContent) return;

    let jobDescription = jdText.trim();
    if (!jobDescription && jdFile && (jdFile.type === "text/plain" || jdFile.name.endsWith(".txt"))) {
      jobDescription = await readFileAsText(jdFile).catch(() => "");
    }
    if (!jobDescription) return;

    setLoadingRecs(true);
    setRecommendations(null);
    try {
      const recs = await getRecommendations(
        resumeContent,
        jobDescription,
        result.score,
        result.summary
      );
      setRecommendations(recs);
    } catch {
      setRecommendations([]);
    } finally {
      setLoadingRecs(false);
    }
  }, [result, resumeText, resumeFile, jdText, jdFile, lastResumeTextFromApi]);

  const handleSelectSavedJD = useCallback((jd: SavedJD) => {
    setJdText(jd.content);
    setJdFile(null);
    setSelectedJdId(jd.id);
  }, []);

  const handleResumeFile = useCallback((file: File) => {
    setResumeFile(file);
    setResumeText("");
  }, []);

  const handleJdFile = useCallback((file: File) => {
    setJdFile(file);
    setJdText("");
    setSelectedJdId(null);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card shadow-card sticky top-0 z-50">
        <div className="container max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-primary flex items-center justify-center shadow-card">
              <GitCompareArrows className="h-5 w-5 text-primary-foreground" />
            </div>
            <h1 className="text-lg font-bold tracking-tight">Resume Lens</h1>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <main className="container max-w-5xl mx-auto px-4 py-8 space-y-8">
        <Tabs defaultValue="compare">
          <TabsList className="mb-6 shadow-card">
            <TabsTrigger value="compare" className="gap-1.5">
              <GitCompareArrows className="h-4 w-4" />
              Compare
            </TabsTrigger>
            <TabsTrigger value="saved" className="gap-1.5">
              <BookOpen className="h-4 w-4" />
              Saved JDs
            </TabsTrigger>
          </TabsList>

          <TabsContent value="compare" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
              <InputArea
                label="Resume"
                placeholder="Paste your resume text here..."
                value={resumeText}
                onChange={(v) => { setResumeText(v); setResumeFile(null); }}
                fileName={resumeFile?.name ?? null}
                onFileSelect={handleResumeFile}
              />
              <InputArea
                label="Job Description"
                placeholder="Paste the job description here..."
                value={jdText}
                onChange={(v) => { setJdText(v); setJdFile(null); setSelectedJdId(null); }}
                fileName={jdFile?.name ?? null}
                onFileSelect={handleJdFile}
              >
                <SavedJDList
                  jds={savedJDsLoading ? [] : savedJDs}
                  onSelect={handleSelectSavedJD}
                  selectedJdId={selectedJdId}
                  compact
                />
              </InputArea>
            </div>

            {compareError && (
              <p className="text-sm text-destructive text-center">{compareError}</p>
            )}

            <div className="flex justify-center">
              <LoadingButton
                size="lg"
                loading={comparing}
                loadingText="Analyzing..."
                disabled={!hasInput}
                onClick={handleCompare}
                className="min-w-[200px] shadow-card hover:shadow-card-hover transition-shadow"
              >
                <GitCompareArrows className="h-4 w-4" />
                Compare
              </LoadingButton>
            </div>

            {result && (
              <div className="space-y-4">
                <ScoreDisplay result={result} />

                {!recommendations && (
                  <div className="flex justify-center">
                    <LoadingButton
                      variant="outline"
                      size="lg"
                      loading={loadingRecs}
                      loadingText="Generating..."
                      onClick={handleGetRecommendations}
                      className="min-w-[250px] shadow-card hover:shadow-card-hover transition-shadow"
                    >
                      <Sparkles className="h-4 w-4" />
                      Get Recommendations
                    </LoadingButton>
                  </div>
                )}

                {recommendations && <Recommendations recommendations={recommendations} />}
              </div>
            )}
          </TabsContent>

          <TabsContent value="saved">
            <div className="max-w-2xl">
              <p className="text-sm text-muted-foreground mb-4">
                Previously saved job descriptions and their comparison history.
              </p>
              {savedJDsLoading ? (
                <p className="text-sm text-muted-foreground">Loading saved JDs...</p>
              ) : (
                <SavedJDList jds={savedJDs} selectedJdId={selectedJdId} />
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve((r.result as string) || "");
    r.onerror = () => reject(new Error("Failed to read file"));
    r.readAsText(file, "UTF-8");
  });
}

export default Index;
