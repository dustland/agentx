import { NextRequest, NextResponse } from 'next/server';
import { clearAuthCookie } from '@/lib/auth-server';

export async function POST(request: NextRequest) {
  // Clear the auth cookie
  const response = NextResponse.json({ success: true });
  
  response.cookies.set('auth-token', '', {
    httpOnly: true,
    expires: new Date(0),
    path: '/',
  });

  return response;
}