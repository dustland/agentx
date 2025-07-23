import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UIState {
  // Sidebar state
  sidebarPinned: boolean;
  setSidebarPinned: (pinned: boolean) => void;
  
  // Initial message for new tasks (passed between routes)
  initialMessage: string | null;
  setInitialMessage: (message: string | null) => void;
  clearInitialMessage: () => void;
  consumeInitialMessage: () => string | null;
}

export const useAppStore = create<UIState>()(
  persist(
    (set, get) => ({
      // Sidebar state
      sidebarPinned: true,
      setSidebarPinned: (pinned) => set({ sidebarPinned: pinned }),
      
      // Initial message management
      initialMessage: null,
      setInitialMessage: (message) => set({ initialMessage: message }),
      clearInitialMessage: () => set({ initialMessage: null }),
      consumeInitialMessage: () => {
        const message = get().initialMessage;
        if (message) {
          set({ initialMessage: null });
        }
        return message;
      },
    }),
    {
      name: "ui-store",
      partialize: (state) => ({
        sidebarPinned: state.sidebarPinned,
        initialMessage: state.initialMessage,
      }),
    }
  )
);