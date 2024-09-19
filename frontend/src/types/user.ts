import { z } from 'zod';

// Define the UserRole enum
export const UserRole = z.enum(['player', 'manager', 'admin']);

// Define the User schema
export const UserLoginRequestSchema = z.object({
  username: z
    .string()
    .min(1, { message: 'Username cannot be empty' })
    .max(50, { message: 'Username is too long (max 50 characters)' })
    .regex(
      /^[a-zA-Z0-9 _-]+$/,
      'Username can only contain alphanumeric characters, underscores, hyphens and spaces'
    )
    .transform((val) => val.toLowerCase()), // Converts username to lowercase
  password: z
    .string()
    .min(1, { message: 'Password cannot be empty' })
    .max(72, { message: 'Password is too long (max 50 characters)' })
});

export type UserLoginRequest = z.infer<typeof UserLoginRequestSchema>;
