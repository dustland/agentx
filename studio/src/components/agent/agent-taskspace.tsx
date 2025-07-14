"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Bot, Plus, Sparkles, Zap, Target } from "lucide-react";
import Image from "next/image";

export function AgentTaskspace() {
  return (
    <div className="flex-1 overflow-auto relative">
      {/* Background X Pattern */}
      <div className="absolute inset-0 opacity-[0.02] pointer-events-none">
        <div className="w-full h-full flex items-center justify-center">
          <div className="text-[40rem] font-bold text-primary select-none">X</div>
        </div>
      </div>

      <div className="relative z-10 p-6 space-y-8">
        {/* Hero Section */}
        <div className="text-center py-12 space-y-6">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Image src="/logo.png" alt="AgentX" width={48} height={48} className="object-contain" />
            <span className="text-5xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
              Agent<span className="text-6xl">X</span>
            </span>
          </div>
          
          <h1 className="text-4xl font-bold tracking-tight text-foreground">
            Welcome to the <span className="text-primary">Vibe-X</span> Experience
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Where AI agents transcend boundaries and embrace the unknown. 
            Experience the <span className="font-semibold text-primary">X-factor</span> in autonomous intelligence.
          </p>

          <div className="flex items-center justify-center gap-4 pt-4">
            <Button size="lg" className="gap-2">
              <Sparkles className="h-5 w-5" />
              Start Your Journey
            </Button>
            <Button size="lg" variant="outline" className="gap-2">
              <Target className="h-5 w-5" />
              Explore Vibe-X
            </Button>
          </div>
        </div>

        {/* Philosophy Section */}
        <div className="max-w-4xl mx-auto">
          <Card className="border-primary/20 bg-gradient-to-r from-primary/5 to-purple-600/5">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl flex items-center justify-center gap-2">
                <Zap className="h-6 w-6 text-primary" />
                The Vibe-X Philosophy
              </CardTitle>
              <CardDescription className="text-base">
                Embracing the experimental, the bold, and the transformative
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-3 gap-6 text-center">
                <div className="space-y-2">
                  <div className="text-3xl font-bold text-primary">∞</div>
                  <h3 className="font-semibold">Limitless</h3>
                  <p className="text-sm text-muted-foreground">
                    Break boundaries of traditional AI interactions
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="text-3xl font-bold text-primary"><Zap className="h-8 w-8" /></div>
                  <h3 className="font-semibold">Dynamic</h3>
                  <p className="text-sm text-muted-foreground">
                    Adaptive intelligence that evolves with you
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="text-3xl font-bold text-primary"><Target className="h-8 w-8" /></div>
                  <h3 className="font-semibold">Focused</h3>
                  <p className="text-sm text-muted-foreground">
                    Precision-driven results with creative flair
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Agent Cards */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold tracking-tight">Your Agent<span className="text-primary">X</span> Fleet</h2>
              <p className="text-muted-foreground">
                Autonomous agents powered by Vibe-X intelligence
              </p>
            </div>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Deploy New Agent
            </Button>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card className="group hover:shadow-lg transition-all hover:border-primary/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                  Research<span className="text-primary">X</span>
                </CardTitle>
                <CardDescription>
                  Deep-dive research with experimental methodologies
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Vibe Status</span>
                    <span className="text-green-600 font-medium">On Fire</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>X-Missions</span>
                    <span className="font-mono">124</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2 mt-3">
                    <div className="bg-primary h-2 rounded-full w-[78%]"></div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-lg transition-all hover:border-primary/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-full bg-purple-500/10 flex items-center justify-center">
                    <Sparkles className="h-4 w-4 text-purple-500" />
                  </div>
                  Creative<span className="text-primary">X</span>
                </CardTitle>
                <CardDescription>
                  Content creation with an experimental edge
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Vibe Status</span>
                    <span className="text-purple-600 font-medium">Vibing</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>X-Missions</span>
                    <span className="font-mono">89</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2 mt-3">
                    <div className="bg-purple-500 h-2 rounded-full w-[65%]"></div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-lg transition-all hover:border-primary/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-full bg-blue-500/10 flex items-center justify-center">
                    <Target className="h-4 w-4 text-blue-500" />
                  </div>
                  Analysis<span className="text-primary">X</span>
                </CardTitle>
                <CardDescription>
                  Data insights with unconventional patterns
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Vibe Status</span>
                    <span className="text-blue-600 font-medium">Locked In</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>X-Missions</span>
                    <span className="font-mono">67</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2 mt-3">
                    <div className="bg-blue-500 h-2 rounded-full w-[92%]"></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}