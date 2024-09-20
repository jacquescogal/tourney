export const CREATE_TEAMS = (): string => `${import.meta.env.VITE_API_HOST}/teams`;

export const GET_TEAM_BY_ID = (team_id: number | string): string =>
  `${import.meta.env.VITE_API_HOST}/teams/${team_id}`;
export const GET_TEAMS = (): string =>
    `${import.meta.env.VITE_API_HOST}/teams`;

export const DELETE_TEAM_BY_ID = (team_id: number | string): string =>
  `${import.meta.env.VITE_API_HOST}/teams/${team_id}`;
  
export const PUT_TEAM_BY_ID = (team_id: number | string): string =>
  `${import.meta.env.VITE_API_HOST}/teams/${team_id}`;