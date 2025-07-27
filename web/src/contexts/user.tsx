"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { User, getCurrentUser, loginUser, logoutUser } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useApi } from "@/lib/api-client";

interface UserContextType {
  user: User | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const refreshUser = async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error("Failed to get current user:", error);
      setUser(null);
      // Don't redirect here - let middleware handle routing
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const loggedInUser = await loginUser(username, password);
      setUser(loggedInUser);
      // Don't call refreshUser here as it's redundant and can cause timing issues
      // The user is already set and authenticated
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await logoutUser();
      setUser(null);
      router.push("/auth/login");
    } catch (error) {
      console.error("Failed to logout:", error);
    }
  };

  return (
    <UserContext.Provider
      value={{ user, isLoading, login, logout, refreshUser }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
}
