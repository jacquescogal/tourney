export const CREATE_TEAMS = (): string => `${import.meta.env.VITE_API_HOST}/match_results`;
export const GET_TEAM = (team_id: number | string): string =>
  `${import.meta.env.VITE_API_HOST}/teams/${team_id}`;
