"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { useAuthStore } from "@/store/auth";
import { Loader2, AlertCircle, HelpCircle } from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuthStore();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Get the redirect URL from query params, default to home
  const redirectTo = searchParams.get("redirect") || "/";

  const fillGuestCredentials = () => {
    setUsername("guest");
    setPassword("GuestDemo$2024!");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login(username, password);
      // Redirect to the intended page after successful login
      router.push(redirectTo);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">
            Login to AgentX Studio
          </CardTitle>
          <CardDescription>Enter your credentials to continue</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label htmlFor="username">Username</Label>
                <HoverCard>
                  <HoverCardTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-5 w-5 rounded-full p-0"
                    >
                      <HelpCircle className="h-3.5 w-3.5" />
                    </Button>
                  </HoverCardTrigger>
                  <HoverCardContent className="w-80" align="start">
                    <div className="space-y-3">
                      <div>
                        <p className="text-sm font-semibold">Quick Start</p>
                        <p className="text-sm text-muted-foreground">
                          Use one of these demo accounts to get started:
                        </p>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <code className="text-xs bg-muted px-2 py-1 rounded">
                            guest / GuestDemo$2024!
                          </code>
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            onClick={fillGuestCredentials}
                          >
                            Fill in
                          </Button>
                        </div>
                        <code className="block text-xs bg-muted px-2 py-1 rounded">
                          alice / alice123
                        </code>
                        <code className="block text-xs bg-muted px-2 py-1 rounded">
                          bob / bob123
                        </code>
                      </div>
                    </div>
                  </HoverCardContent>
                </HoverCard>
              </div>
              <Input
                id="username"
                type="text"
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={isLoading}
                autoFocus
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Logging in...
                </>
              ) : (
                "Login"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
