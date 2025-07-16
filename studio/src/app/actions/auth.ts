'use server';

import { cookies } from 'next/headers';
import jwt from 'jsonwebtoken';
import { redirect } from 'next/navigation';
import { findUserByUsername, verifyPassword, updateLastLogin, initializeDemoUsers } from '@/lib/auth-db';
import { env } from '@/lib/env';

export interface LoginResult {
  success: boolean;
  error?: string;
  user?: {
    id: string;
    username: string;
    email?: string;
  };
}

export async function loginAction(
  username: string,
  password: string
): Promise<LoginResult> {
  try {
    // Initialize demo users if enabled
    await initializeDemoUsers();

    // Validate input
    if (!username || !password) {
      return { success: false, error: 'Username and password are required' };
    }

    // Find user
    const user = await findUserByUsername(username);
    if (!user) {
      return { success: false, error: 'Invalid username or password' };
    }

    // Verify password
    if (!verifyPassword(password, user.passwordHash)) {
      return { success: false, error: 'Invalid username or password' };
    }

    // Update last login
    await updateLastLogin(user.id);

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, username: user.username },
      env.JWT_SECRET,
      { expiresIn: '7d' }
    );

    // Set HTTP-only cookie
    cookies().set('auth-token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/',
    });

    return {
      success: true,
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
      },
    };
  } catch (error) {
    console.error('Login error:', error);
    return { success: false, error: 'Internal server error' };
  }
}

export async function logoutAction() {
  cookies().delete('auth-token');
  redirect('/auth/login');
}

export async function getCurrentUser() {
  const token = cookies().get('auth-token')?.value;

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