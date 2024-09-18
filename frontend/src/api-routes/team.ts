export const CREATE_TEAMS = (): string => `${import.meta.env.VITE_API_HOST}/match_results`;
export const GET_TEAM_BY_ID = (team_id: number | string): string =>
  `${import.meta.env.VITE_API_HOST}/teams/${team_id}`;
export const GET_TEAMS = (): string =>
    `${import.meta.env.VITE_API_HOST}/teams`;
  