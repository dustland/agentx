/**
 * Authentication client for VibeX
 *
 * Handles user authentication and session management via API endpoints.
 */

export interface User {
  id: string;
  username: string;
  email?: string;
  createdAt: string;
  lastLogin?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface AuthError {
  error: string;
}

/**
 * Register a new user
 */
export async function registerUser(
  username: string,
  password: string,
  email?: string
): Promise<User> {
  const response = await fetch("/api/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password, email }),
  });

  if (!response.ok) {
    const error: AuthError = await response.json();
    throw new Error(error.error || "Registration failed");
  }

  const data: AuthResponse = await response.json();
  return data.user;
}

/**
 * Login with username and password
 */
export async function loginUser(
  username: string,
  password: string
): Promise<User> {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const error: AuthError = await response.json();
    throw new Error(error.error || "Login failed");
  }

  const data: AuthResponse = await response.json();
  return data.user;
}

/**
 * Logout the current user
 */
export async function logoutUser(): Promise<void> {
  await fetch("/api/auth/logout", {
    method: "POST",
  });
}

/**
 * Get the current authenticated user
 */
export async function getCurrentUser(): Promise<User | null> {
  try {
    const response = await fetch("/api/auth/me");

    if (!response.ok) {
      // If we get a 401, it means the user is not authenticated
      if (response.status === 401) {
        // Return null to indicate no authenticated user
        // The api-client will handle the redirect
        return null;
      }
      // For other errors, throw to be caught by the caller
      throw new Error(`Failed to get current user: ${response.status}`);
    }

    const data = await response.json();
    return data.user;
  } catch (error) {
    console.error("Error fetching current user:", error);
    // Re-throw the error to be handled by the caller
    throw error;
  }
}

/**
 * Get user display name
 */
export function getUserDisplayName(user: User): string {
  return user.username;
}

/**
 * Demo user credentials for easy testing
 */
export const DEMO_USERS = [
  { username: "guest", password: "GuestDemo$2024!" },
  { username: "alice", password: "alice123" },
  { username: "bob", password: "bob123" },
];
