import { MatchResult, SavedJD } from "@/types/matcher";
import matchResultJson from "./match-result.json";
import recommendationsJson from "./recommendations.json";
import savedJDsJson from "./saved-jds.json";

export const dummyMatchResult: MatchResult = matchResultJson;
export const dummyRecommendations: string[] = recommendationsJson;
export const savedJDs: SavedJD[] = savedJDsJson;
