"use client";

import React, { useEffect, useState } from 'react';
import { useUser } from '@/contexts/user-context';
import { LoginModal } from './login-modal';
import { Loader2 } from 'lucide-react';

interface AuthWrapperProps {
  children: React.ReactNode;
}

export function AuthWrapper({ children }: AuthWrapperProps) {
  const { user, isLoading } = useUser();
  const [showLogin, setShowLogin] = useState(false);

  useEffect(() => {
    // Show login modal if not authenticated after loading
    if (!isLoading && !user) {
      setShowLogin(true);
    }
    // Hide login modal when user is authenticated
    if (user) {
      setShowLogin(false);
    }
  }, [isLoading, user]);

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

  return (
    <>
      {children}
      <LoginModal open={showLogin && !user} onOpenChange={setShowLogin} />
    </>
  );
}