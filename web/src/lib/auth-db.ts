/**
 * Simple file-based user database for VibeX
 *
 * This is a lightweight solution for development and small deployments.
 * For production, replace with a proper database.
 */

import fs from "fs/promises";
import path from "path";
import crypto from "crypto";

const DB_FILE = path.join(process.cwd(), ".vibex-users.json");

export interface User {
  id: string;
  username: string;
  email?: string;
  passwordHash: string;
  createdAt: string;
  lastLogin?: string;
}

interface UserDB {
  users: User[];
}

// Initialize DB file if it doesn't exist
async function initDB(): Promise<void> {
  try {
    await fs.access(DB_FILE);
  } catch {
    const initialDB: UserDB = { users: [] };
    await fs.writeFile(DB_FILE, JSON.stringify(initialDB, null, 2));
  }
}

// Read users from file
async function readDB(): Promise<UserDB> {
  await initDB();
  const data = await fs.readFile(DB_FILE, "utf-8");
  return JSON.parse(data);
}

// Write users to file
async function writeDB(db: UserDB): Promise<void> {
  await fs.writeFile(DB_FILE, JSON.stringify(db, null, 2));
}

// Hash password using crypto (simple alternative to bcrypt)
export function hashPassword(password: string): string {
  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto
    .pbkdf2Sync(password, salt, 1000, 64, "sha512")
    .toString("hex");
  return `${salt}:${hash}`;
}

// Verify password
export function verifyPassword(password: string, storedHash: string): boolean {
  const [salt, hash] = storedHash.split(":");
  const verifyHash = crypto
    .pbkdf2Sync(password, salt, 1000, 64, "sha512")
    .toString("hex");
  return hash === verifyHash;
}

// Create a new user
export async function createUser(
  username: string,
  password: string,
  email?: string
): Promise<User> {
  const db = await readDB();

  // Check if user exists
  if (db.users.some((u) => u.username === username)) {
    throw new Error("Username already exists");
  }

  if (email && db.users.some((u) => u.email === email)) {
    throw new Error("Email already registered");
  }

  const newUser: User = {
    id: crypto.randomBytes(16).toString("hex"),
    username,
    email,
    passwordHash: hashPassword(password),
    createdAt: new Date().toISOString(),
  };

  db.users.push(newUser);
  await writeDB(db);

  // Return user without password hash
  const { passwordHash, ...userWithoutPassword } = newUser;
  return { ...userWithoutPassword, passwordHash: "" };
}

// Find user by username
export async function findUserByUsername(
  username: string
): Promise<User | null> {
  const db = await readDB();
  return db.users.find((u) => u.username === username) || null;
}

// Find user by ID
export async function findUserById(id: string): Promise<User | null> {
  const db = await readDB();
  return db.users.find((u) => u.id === id) || null;
}

// Update last login
export async function updateLastLogin(userId: string): Promise<void> {
  const db = await readDB();
  const user = db.users.find((u) => u.id === userId);
  if (user) {
    user.lastLogin = new Date().toISOString();
    await writeDB(db);
  }
}

// Initialize demo users
export async function initializeDemoUsers(): Promise<void> {
  const db = await readDB();

  // Only initialize demo users if explicitly enabled
  if (process.env.ENABLE_DEMO_USERS !== "true") {
    return;
  }

  // Check if each demo user exists and create if not
  const demoUsers = [
    {
      username: "guest",
      password: process.env.DEMO_USER_PASSWORD || "ChangeMe!2024",
      email: "guest@example.com",
    },
    {
      username: "alice",
      password: process.env.DEMO_USER_PASSWORD || "ChangeMe!2024",
      email: "alice@example.com",
    },
    {
      username: "bob",
      password: process.env.DEMO_USER_PASSWORD || "ChangeMe!2024",
      email: "bob@example.com",
    },
  ];

  let usersAdded = false;
  for (const demoUser of demoUsers) {
    if (!db.users.find((u) => u.username === demoUser.username)) {
      try {
        await createUser(demoUser.username, demoUser.password, demoUser.email);
        usersAdded = true;
      } catch (error) {
        console.error(
          `Failed to create demo user ${demoUser.username}:`,
          error
        );
      }
    }
  }

  if (usersAdded) {
    console.log("Demo users initialized");
  }
}
