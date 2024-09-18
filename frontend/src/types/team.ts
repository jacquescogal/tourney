import { z } from 'zod';
import { parse, isValid } from 'date-fns';

export const RegisterTeamRequestSchema = z.object({
  team_name: z.string().min(1, 'team name is required').regex(/^[a-zA-Z0-9-_ ]*$/, 'team name can only contain alphanumeric characters, hyphens, underscores, and spaces'),
  registration_date: z.string()
  .length(5,'registration date needs to adhere to DD/MM format')
  .regex(/^[0-9]{2}\/[0-9]{2}$/, 'registration date needs to adhere to DD/MM format')
  .refine(
    (date: string)=>{
      const parsedDate = parse(date, 'dd/MM', new Date());
      return isValid(parsedDate);
  }, 'registration date is not valid')
  ,
  group_number: z.number().min(1, "group  number must be either 1 or 2").max(2, "group  number must be either 1 or 2")
});
export type RegisterTeamRequest = z.infer<typeof RegisterTeamRequestSchema>;

export type BatchRegisterTeamRequest = {
    teams: RegisterTeamRequest[]
}

// For teamboard
export interface ITeam {
  team_id: number;
  team_name: string;
  registration_day_of_year: number;
  registration_date_ddmm: string;
  group_number: number;
}

// For TeamDetailPage
// Define the types based on your FastAPI response
export interface ITeamMatchUpDetail {
  opponent: string;
  round_number: number;
  match_id: number;
  goals_scored: number;
  goals_conceded: number;
}

export interface ITeamMatchUpDetailRow extends ITeamMatchUpDetail{
  goals_for_againt: string;
}

export interface ITeamDetails {
  team_name: string;
  registration_date_ddmm: string;
  group_number: number;
  match_ups: ITeamMatchUpDetail[];
}
