import {
  CREATE_GAME_MATCHES,
  GET_MATCH_RANKINGS,
  GET_MATCH_RESULTS,
} from "../api_routes/match-core";
import { BatchCreateMatchResultsRequest } from "../types/match";

class MatchService {
  public static getMatchRankings = async (params: {
    roundNumber: number;
    groupNumber: number;
  }): Promise<Response> => {
    const strParams = {
      round_number: String(params.roundNumber),
      group_number: String(params.groupNumber),
    };
    const queryString = new URLSearchParams(strParams).toString();
    const response = await fetch(`${GET_MATCH_RANKINGS()}?${queryString}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    return response;
  };

  public static getMatchResults = async (params: {
    roundNumber: number;
  }): Promise<Response> => {
    const strParams = {
      round_number: String(params.roundNumber),
    };
    const queryString = new URLSearchParams(strParams).toString();
    const response = await fetch(`${GET_MATCH_RESULTS()}?${queryString}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    return response;
  };

  public static createMatchResults = async (
    payload: BatchCreateMatchResultsRequest
  ): Promise<Response> => {
    const response = await fetch(`${CREATE_GAME_MATCHES()}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      credentials: "include",
    });
    return response;
  };
}

export default MatchService;
