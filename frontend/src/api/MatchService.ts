import axios from 'axios';
import { GET_MATCH_RANKINGS } from '../api_routes/match-core';
import { IMatchRankingResponse } from '../types/leaderboard';

class MatchService {
    public static getMatchRankings = async (params: { roundNumber: number; groupNumber: number }): Promise<IMatchRankingResponse> => {
        const response = await axios.get<IMatchRankingResponse>(
            GET_MATCH_RANKINGS(),
            {
              params: {
                round: params.roundNumber,
                group: params.groupNumber,
              },
            }
          );
          return response.data
      };
  }
  
  export default MatchService;