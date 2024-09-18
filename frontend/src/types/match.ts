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