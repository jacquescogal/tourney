
// Assuming UserRole is an enum or type in your TypeScript code
export type UserRole = 'player' | 'admin'; // Example of possible roles

export interface IUserSession {
    user_id: number;
    user_role: UserRole;
    team_id?: number | null; // Optional field, can be null or undefined
}
