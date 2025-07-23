import { NextRequest, NextResponse } from 'next/server';
import { authenticateUser, generateAuthToken, setAuthCookie } from '@/lib/auth-server';
import { initializeDemoUsers } from '@/lib/auth-db';

export async function POST(request: NextRequest) {
  try {
    // Initialize demo users on first run
    await initializeDemoUsers();
    
    const { username, password } = await request.json();

    // Authenticate user
    const user = await authenticateUser(username, password);
    
    // Generate token
    const token = generateAuthToken(user.id, user.username);

    // Return response with token
    const response = NextResponse.json({
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        createdAt: user.createdAt,
        lastLogin: user.lastLogin,
      },
      token,
    });

    // Set HTTP-only cookie for better security
    response.cookies.set('auth-token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/',
    });

    return response;
  } catch (error: any) {
    console.error('Login error:', error);
    
    // Return specific error message if it's a known error
    if (error.message === 'Username and password are required') {
      return NextResponse.json(
        { error: error.message },
        { status: 400 }
      );
    }
    
    if (error.message === 'Invalid username or password') {
      return NextResponse.json(
        { error: error.message },
        { status: 401 }
      );
    }
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}