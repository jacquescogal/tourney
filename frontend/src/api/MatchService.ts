import { GET_MATCH_RANKINGS } from '../api_routes/match-core';
import { BatchCreateMatchResultsRequest } from '../types/match';

class MatchService {
    public static getMatchRankings = async (params: { roundNumber: number; groupNumber: number }): Promise<Response> => {
      const strParams = {
        round: String(params.roundNumber),
        group: String(params.groupNumber),
      }
      const queryString = new URLSearchParams(strParams).toString();
      const response = await fetch(`${GET_MATCH_RANKINGS()}?${queryString}`);
      return response
      };

      public static createMatchResults = async (payload:BatchCreateMatchResultsRequest): Promise<Response> => {
        const response = await fetch("http://localhost:8000/match_results/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });
        return response
        };

      
  }
  
  export default MatchService;