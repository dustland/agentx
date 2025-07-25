import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Check if user is authenticated by looking for auth token in cookies
  const authToken = request.cookies.get("auth-token");

  // Public routes that don't require authentication
  const publicRoutes = ["/auth/login", "/auth/register"];
  const isPublicRoute = publicRoutes.some((route) =>
    request.nextUrl.pathname.startsWith(route)
  );

  // If accessing public route, allow access
  if (isPublicRoute) {
    // If already authenticated and trying to access login/register, redirect to home
    if (authToken?.value) {
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  // If not authenticated and trying to access protected route, redirect to login
  if (!authToken?.value) {
    const loginUrl = new URL("/auth/login", request.url);
    loginUrl.searchParams.set("redirect", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If authenticated, allow access
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, etc.)
     */
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.jpg$|.*\\.jpeg$|.*\\.gif$|.*\\.svg$).*)",
    // Also try simpler patterns
    "/",
    "/(agents)/:path*",
  ],
};
