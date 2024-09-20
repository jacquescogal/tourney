import { z } from 'zod';

export const MatchResultBaseSchema = z.object({
    team_name: z.string().min(1, 'team name is required').regex(/^[a-zA-Z0-9-_ ]*$/, 'team name can only contain alphanumeric characters, hyphens, underscores, and spaces'),
    goals_scored: z.number().int('must be whole number').min(0,'cannot be negative')
})

export type MatchResultBase = z.infer<typeof MatchResultBaseSchema>;

export const CreateMatchResultsSchema = z.object({
    result: z.array(MatchResultBaseSchema).min(2,'exactly 2 teams and their scores for match result must be provided').max(2,'exactly 2 teams and their scores for match result must be provided')
})

export type CreateMatchResults = z.infer<typeof CreateMatchResultsSchema>;

export const BatchCreateMatchResultsRequestSchema = z.object({
    results: z.array(CreateMatchResultsSchema).min(1, 'must contain at least 1 element'),
    round_number: z.number().int('must be a whole number').min(1, 'Round number should be between 1 and 3 inclusive').max(3,'Round number should be between 1 and 3 inclusive')
})

export type BatchCreateMatchResultsRequest = z.infer<typeof BatchCreateMatchResultsRequestSchema>;


export const UpdateMatchResultRequestSchema = z.object({
    round_number: z
      .number()
      .min(1, "Round number should be between 1 and 3")
      .max(3, "Round number should be between 1 and 3")
      .describe("Round number for the matches"),
    match_id: z
      .number()
      .describe("Unique identifier for the match"),
    team_id: z
      .number()
      .describe("Unique identifier for the first team"),
    team_goals: z
      .number()
      .nonnegative("Goals scored should be non-negative")
      .describe("Number of goals scored by the first team")
  });
  
  export type UpdateMatchResultRequest = z.infer<typeof UpdateMatchResultRequestSchema>;

  export const DeleteMatchResultRequestSchema = z.object({
    round_number: z
      .number()
      .min(1, "Round number should be between 1 and 3")
      .max(3, "Round number should be between 1 and 3")
      .describe("Round number for the matches"),
    match_id: z
      .number()
      .describe("Unique identifier for the match"),
  });
  
  export type DeleteMatchResultRequest = z.infer<typeof DeleteMatchResultRequestSchema>;