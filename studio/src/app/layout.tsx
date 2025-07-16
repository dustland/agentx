import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/styles/globals.css";
import { Providers } from "@/components/common/providers";
import { ThemeProvider } from "@/components/common/theme-provider";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "sonner";
import { UserProvider } from "@/contexts/user-context";
import { AuthWrapper } from "@/components/auth/auth-wrapper";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    default: "AgentX Studio",
    template: "%s | AgentX Studio",
  },
  description: "Unified interface for AgentX task execution and observability",
  keywords: [
    "AI",
    "agents",
    "automation",
    "task execution",
    "observability",
    "multi-agent",
    "orchestration",
  ],
  authors: [{ name: "AgentX Team" }],
  creator: "AgentX Studio",
  publisher: "AgentX Studio",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon-16x16.png",
    apple: "/apple-touch-icon.png",
    other: [
      {
        rel: "icon",
        type: "image/png",
        sizes: "32x32",
        url: "/favicon-32x32.png",
      },
      {
        rel: "icon",
        type: "image/png",
        sizes: "16x16",
        url: "/favicon-16x16.png",
      },
      {
        rel: "manifest",
        url: "/site.webmanifest",
      },
    ],
  },
};

export const viewport = {
  themeColor: "#3b82f6",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>{`
          :root {
            --header-height: 57px;
          }
        `}</style>
      </head>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <UserProvider>
            <TooltipProvider>
              <Providers>
                <AuthWrapper>{children}</AuthWrapper>
              </Providers>
            </TooltipProvider>
            <Toaster position="bottom-right" />
          </UserProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
