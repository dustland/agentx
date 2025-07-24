import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "VibeX",
  description: "Login to VibeX",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="min-h-screen bg-background">{children}</div>;
}
