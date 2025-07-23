import { cookies } from "next/headers";
import jwt from "jsonwebtoken";
import {
  findUserByUsername,
  verifyPassword,
  updateLastLogin,
} from "@/lib/auth-db";
import { env } from "@/lib/env";

export async function authenticateUser(username: string, password: string) {
  // Validate input
  if (!username || !password) {
    throw new Error("Username and password are required");
  }

  // Find user
  const user = await findUserByUsername(username);
  if (!user) {
    throw new Error("Invalid username or password");
  }

  // Verify password
  if (!verifyPassword(password, user.passwordHash)) {
    throw new Error("Invalid username or password");
  }

  // Update last login
  await updateLastLogin(user.id);

  return user;
}

export function generateAuthToken(userId: string, username: string) {
  return jwt.sign({ userId, username }, env.JWT_SECRET, { expiresIn: "7d" });
}

export async function setAuthCookie(token: string) {
  const cookieStore = await cookies();
  cookieStore.set("auth-token", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: "/",
  });
}

export async function clearAuthCookie() {
  const cookieStore = await cookies();
  cookieStore.delete("auth-token");
}

export async function getCurrentUser() {
  const cookieStore = await cookies();
  const token = cookieStore.get("auth-token")?.value;

  if (!token) {
    return null;
  }

  try {
    const decoded = jwt.verify(token, env.JWT_SECRET) as any;
    return {
      id: decoded.userId,
      username: decoded.username,
    };
  } catch {
    return null;
  }
}
