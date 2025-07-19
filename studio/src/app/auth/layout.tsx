import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AgentX",
  description: "Login to AgentX Studio",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="min-h-screen bg-background">{children}</div>;
}
