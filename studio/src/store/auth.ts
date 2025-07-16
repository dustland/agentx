import { create } from "zustand";
import { persist } from "zustand/middleware";
import { getCurrentUser, loginUser, logoutUser, User } from "@/lib/auth";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Actions
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,

      login: async (username: string, password: string) => {
        set({ isLoading: true });
        try {
          const user = await loginUser(username, password);

          // Set user data in cookie for middleware
          document.cookie = `user=${JSON.stringify(user)}; path=/; max-age=${
            60 * 60 * 24 * 7
          }; samesite=lax`;

          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        try {
          await logoutUser();
        } catch (error) {
          console.error("Logout error:", error);
        } finally {
          // Clear user cookie
          document.cookie =
            "user=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;";

          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      checkAuth: async () => {
        set({ isLoading: true });
        try {
          const user = await getCurrentUser();
          set({
            user,
            isAuthenticated: !!user,
            isLoading: false,
          });
        } catch (error) {
          console.error("Auth check error:", error);
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      clearAuth: () => {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
