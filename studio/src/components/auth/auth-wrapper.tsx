"use client";

import React, { useEffect } from "react";
import { useAuthStore } from "@/stores/auth";
import { useRouter, usePathname } from "next/navigation";
import { Loader2 } from "lucide-react";

interface AuthWrapperProps {
  children: React.ReactNode;
}

export function AuthWrapper({ children }: AuthWrapperProps) {
  const { user, isLoading, isAuthenticated, checkAuth } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    // Don't redirect if we're already on the login page or still loading
    if (isLoading || pathname === "/auth/login") {
      return;
    }

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
      const redirectUrl = encodeURIComponent(pathname);
      router.push(`/auth/login?redirect=${redirectUrl}`);
    }
  }, [isLoading, isAuthenticated, router, pathname]);

  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading AgentX Studio...</p>
        </div>
      </div>
    );
  }

  // Show login page content if we're on the login route
  if (pathname === "/auth/login") {
    return <>{children}</>;
  }

  // Don't render protected content if user is not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
