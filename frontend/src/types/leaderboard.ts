// Response schema for GET_MATCH_RANKINGS
export interface ITeamRanking {
  position: number;
  is_tired: boolean;
  is_qualified: boolean;
  team_id: number;
  team_name: string;
  goals: number;
  wins: number;
  draws: number;
  losses: number;
  registration_date_ddmm: string;
  registration_day_of_year: number;
}

export interface IGroupRanking {
  group_number: number;
  team_rankings: ITeamRanking[];
}

export interface IMatchRankingResponse {
  round_number: number;
  group_rankings: IGroupRanking[];
}

// ITeamRankingRow
export interface ITeamRankingRow extends ITeamRanking{
    wdl: string;
}
