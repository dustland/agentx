"use client";

import { useState } from "react";
import { SendButton } from "@/components/chat";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Slider } from "@/components/ui/slider";
import { Toggle } from "@/components/ui/toggle";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ThemeSwitcher } from "@/components/theme-switcher";
import { Sidebar, SidebarItem } from "@/components/layout/sidebar";
import { TypingIndicator } from "@/components/typing-indicator";
import {
  ChevronRight,
  Settings,
  User,
  Mail,
  Phone,
  Calendar,
  Star,
  Heart,
  MessageSquare,
  Bell,
  Search,
  Filter,
  Download,
  Upload,
  Edit,
  Trash2,
  Plus,
  Minus,
  Check,
  X,
  AlertCircle,
  Info,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

export default function DesignPage() {
  const [progress, setProgress] = useState(33);
  const [sliderValue, setSliderValue] = useState([50]);

  // Mock sidebar items for testing
  const mockSidebarItems: SidebarItem[] = [
    {
      id: "1",
      title: "Research Task",
      subtitle: "Data analysis project",
      status: "running",
      href: "#",
      metadata: {
        timeAgo: "2m ago",
        configPath: "config/research.yaml",
      },
    },
    {
      id: "2",
      title: "Content Generation",
      subtitle: "Blog post writing",
      status: "completed",
      href: "#",
      metadata: {
        timeAgo: "1h ago",
        configPath: "config/writer.yaml",
      },
    },
    {
      id: "3",
      title: "Code Review",
      subtitle: "PR analysis",
      status: "error",
      href: "#",
      metadata: {
        timeAgo: "30m ago",
        configPath: "config/reviewer.yaml",
      },
    },
    {
      id: "4",
      title: "Data Processing",
      subtitle: "ETL pipeline",
      status: "pending",
      href: "#",
      metadata: {
        timeAgo: "5m ago",
      },
    },
  ];

  return (
    <div className="container max-w-7xl py-8 mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">Design System</h1>
          <p className="text-muted-foreground text-lg">
            Complete UI component library and design tokens for VibeX
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Theme:</span>
          <ThemeSwitcher />
        </div>
      </div>

      {/* Color Palette */}
      <Card>
        <CardHeader>
          <CardTitle>Color Palette</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {/* Primary Colors */}
            <div className="space-y-2">
              <div className="h-16 w-full bg-primary rounded-lg shadow-sm"></div>
              <p className="text-sm font-medium">Primary</p>
            </div>
            <div className="space-y-2">
              <div className="h-16 w-full bg-primary/80 rounded-lg shadow-sm"></div>
              <p className="text-sm font-medium">Primary/80</p>
            </div>
            <div className="space-y-2">
              <div className="h-16 w-full bg-secondary rounded-lg shadow-sm"></div>
              <p className="text-sm font-medium">Secondary</p>
            </div>
            <div className="space-y-2">
              <div className="h-16 w-full bg-muted rounded-lg shadow-sm"></div>
              <p className="text-sm font-medium">Muted</p>
            </div>
            <div className="space-y-2">
              <div className="h-16 w-full bg-accent rounded-lg shadow-sm"></div>
              <p className="text-sm font-medium">Accent</p>
            </div>
            <div className="space-y-2">
              <div className="h-16 w-full bg-destructive rounded-lg shadow-sm"></div>
              <p className="text-sm font-medium">Destructive</p>
            </div>
            {/* Background Colors */}
            <div className="space-y-2">
              <div className="h-16 w-full bg-background border rounded-lg shadow-sm"></div>
              <p className="text-sm font-medium">Background</p>
            </div>
            <div className="space-y-2">
              <div className="h-16 w-full bg-card border rounded-lg shadow-sm"></div>
              <p className="text-sm font-medium">Card</p>
            </div>
            <div className="space-y-2">
              <div className="h-16 w-full bg-popover border rounded-lg shadow-sm"></div>
              <p className="text-sm font-medium">Popover</p>
            </div>
            <div className="space-y-2">
              <div className="h-16 w-full bg-border rounded-lg shadow-sm"></div>
              <p className="text-sm font-medium">Border</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Typography */}
      <Card>
        <CardHeader>
          <CardTitle>Typography</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold">Heading 1</h1>
            <h2 className="text-3xl font-semibold">Heading 2</h2>
            <h3 className="text-2xl font-semibold">Heading 3</h3>
            <h4 className="text-xl font-semibold">Heading 4</h4>
            <p className="text-lg">Large text for important content</p>
            <p className="text-base">Base text for regular content</p>
            <p className="text-sm">Small text for secondary information</p>
            <p className="text-xs text-muted-foreground">
              Extra small text for captions
            </p>
            <p className="text-sm text-muted-foreground">
              Muted text for less important content
            </p>
            <code className="text-sm bg-muted px-2 py-1 rounded">
              Code snippet
            </code>
          </div>
        </CardContent>
      </Card>

      {/* Buttons */}
      <Card>
        <CardHeader>
          <CardTitle>Buttons</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Button Variants */}
            <div className="space-y-3">
              <h4 className="font-semibold">Variants</h4>
              <div className="flex flex-wrap gap-2">
                <Button variant="default">Default</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="destructive">Destructive</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="link">Link</Button>
              </div>
            </div>

            {/* Button Sizes */}
            <div className="space-y-3">
              <h4 className="font-semibold">Sizes</h4>
              <div className="flex flex-wrap items-center gap-2">
                <Button size="sm">Small</Button>
                <Button size="default">Default</Button>
                <Button size="lg">Large</Button>
                <Button size="icon">
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Button States */}
            <div className="space-y-3">
              <h4 className="font-semibold">States</h4>
              <div className="flex flex-wrap gap-2">
                <Button>Normal</Button>
                <Button disabled>Disabled</Button>
                <Button>
                  <Settings className="mr-2 h-4 w-4" />
                  With Icon
                </Button>
              </div>
            </div>

            {/* Send Button */}
            <div className="space-y-3">
              <h4 className="font-semibold">Send Button</h4>
              <div className="flex items-center gap-4">
                <SendButton isLoading={false} />
                <SendButton isLoading={true} />
                <SendButton isLoading={false} disabled={true} />
                <SendButton isLoading={false} size="sm" />
                <SendButton isLoading={true} size="sm" />
                <SendButton isLoading={false} disabled={true} size="sm" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Form Components */}
      <Card>
        <CardHeader>
          <CardTitle>Form Components</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Inputs */}
            <div className="space-y-4">
              <h4 className="font-semibold">Inputs</h4>
              <div className="space-y-3">
                <div>
                  <Label htmlFor="normal">Normal Input</Label>
                  <Input id="normal" placeholder="Type something..." />
                </div>
                <div>
                  <Label htmlFor="disabled">Disabled Input</Label>
                  <Input id="disabled" placeholder="Disabled" disabled />
                </div>
                <div>
                  <Label htmlFor="textarea">Textarea</Label>
                  <Textarea id="textarea" placeholder="Type your message..." />
                </div>
              </div>
            </div>

            {/* Select & Checkboxes */}
            <div className="space-y-4">
              <h4 className="font-semibold">Selection</h4>
              <div className="space-y-3">
                <div>
                  <Label>Select</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select an option" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="option1">Option 1</SelectItem>
                      <SelectItem value="option2">Option 2</SelectItem>
                      <SelectItem value="option3">Option 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Checkboxes</Label>
                  <div className="flex items-center space-x-2">
                    <Checkbox id="terms" />
                    <Label htmlFor="terms">Accept terms and conditions</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox id="newsletter" defaultChecked />
                    <Label htmlFor="newsletter">Subscribe to newsletter</Label>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Radio Group</Label>
                  <RadioGroup defaultValue="option1">
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="option1" id="r1" />
                      <Label htmlFor="r1">Option 1</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="option2" id="r2" />
                      <Label htmlFor="r2">Option 2</Label>
                    </div>
                  </RadioGroup>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Interactive Components */}
      <Card>
        <CardHeader>
          <CardTitle>Interactive Components</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Progress & Sliders */}
            <div className="space-y-4">
              <h4 className="font-semibold">Progress & Sliders</h4>
              <div className="space-y-3">
                <div>
                  <Label>Progress ({progress}%)</Label>
                  <Progress value={progress} className="mt-2" />
                </div>
                <div>
                  <Label>Slider ({sliderValue[0]})</Label>
                  <Slider
                    value={sliderValue}
                    onValueChange={setSliderValue}
                    max={100}
                    step={1}
                    className="mt-2"
                  />
                </div>
              </div>
            </div>

            {/* Toggles */}
            <div className="space-y-4">
              <h4 className="font-semibold">Toggles</h4>
              <div className="flex flex-wrap gap-2">
                <Toggle>
                  <User className="h-4 w-4" />
                </Toggle>
                <Toggle pressed>
                  <Heart className="h-4 w-4" />
                </Toggle>
                <Toggle>
                  <Star className="h-4 w-4" />
                </Toggle>
              </div>
            </div>

            {/* Avatars */}
            <div className="space-y-4">
              <h4 className="font-semibold">Avatars</h4>
              <div className="flex items-center gap-2">
                <Avatar>
                  <AvatarImage src="https://github.com/shadcn.png" />
                  <AvatarFallback>CN</AvatarFallback>
                </Avatar>
                <Avatar>
                  <AvatarFallback>JD</AvatarFallback>
                </Avatar>
                <Avatar>
                  <AvatarFallback>
                    <User className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Badges & Alerts */}
      <Card>
        <CardHeader>
          <CardTitle>Feedback Components</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Badges */}
            <div className="space-y-3">
              <h4 className="font-semibold">Badges</h4>
              <div className="flex flex-wrap gap-2">
                <Badge variant="default">Default</Badge>
                <Badge variant="secondary">Secondary</Badge>
                <Badge variant="destructive">Destructive</Badge>
                <Badge variant="outline">Outline</Badge>
              </div>
            </div>

            {/* Alerts */}
            <div className="space-y-3">
              <h4 className="font-semibold">Alerts</h4>
              <div className="space-y-3">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    This is an informational alert message.
                  </AlertDescription>
                </Alert>

                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    This is a destructive alert message.
                  </AlertDescription>
                </Alert>
              </div>
            </div>

            {/* Typing Indicator */}
            <div className="space-y-3">
              <h4 className="font-semibold">Typing Indicator</h4>
              <div className="space-y-3">
                <div className="bg-card border rounded-lg p-4">
                  <p className="text-sm text-muted-foreground mb-2">
                    Message content would go here...
                  </p>
                  <TypingIndicator />
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <Card>
        <CardHeader>
          <CardTitle>Navigation</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="tab1" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="tab1">Overview</TabsTrigger>
              <TabsTrigger value="tab2">Analytics</TabsTrigger>
              <TabsTrigger value="tab3">Reports</TabsTrigger>
              <TabsTrigger value="tab4">Settings</TabsTrigger>
            </TabsList>
            <TabsContent value="tab1" className="mt-4">
              <p className="text-sm text-muted-foreground">
                Overview tab content
              </p>
            </TabsContent>
            <TabsContent value="tab2" className="mt-4">
              <p className="text-sm text-muted-foreground">
                Analytics tab content
              </p>
            </TabsContent>
            <TabsContent value="tab3" className="mt-4">
              <p className="text-sm text-muted-foreground">
                Reports tab content
              </p>
            </TabsContent>
            <TabsContent value="tab4" className="mt-4">
              <p className="text-sm text-muted-foreground">
                Settings tab content
              </p>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Icons */}
      <Card>
        <CardHeader>
          <CardTitle>Common Icons</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-8 md:grid-cols-12 lg:grid-cols-16 gap-4">
            {[
              { icon: User, name: "User" },
              { icon: Settings, name: "Settings" },
              { icon: Mail, name: "Mail" },
              { icon: Phone, name: "Phone" },
              { icon: Calendar, name: "Calendar" },
              { icon: Star, name: "Star" },
              { icon: Heart, name: "Heart" },
              { icon: MessageSquare, name: "Message" },
              { icon: Bell, name: "Bell" },
              { icon: Search, name: "Search" },
              { icon: Filter, name: "Filter" },
              { icon: Download, name: "Download" },
              { icon: Upload, name: "Upload" },
              { icon: Edit, name: "Edit" },
              { icon: Trash2, name: "Trash" },
              { icon: Plus, name: "Plus" },
              { icon: Minus, name: "Minus" },
              { icon: Check, name: "Check" },
              { icon: X, name: "X" },
              { icon: ChevronRight, name: "Chevron" },
            ].map(({ icon: Icon, name }) => (
              <TooltipProvider key={name}>
                <Tooltip>
                  <TooltipTrigger>
                    <div className="flex flex-col items-center gap-2 p-2 rounded hover:bg-muted transition-colors">
                      <Icon className="h-5 w-5" />
                      <span className="text-xs text-muted-foreground">
                        {name}
                      </span>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{name} Icon</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Layout Components */}
      <Card>
        <CardHeader>
          <CardTitle>Layout Components</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div>
              <h4 className="font-semibold mb-3">Separators</h4>
              <div className="space-y-2">
                <p className="text-sm">Content above separator</p>
                <Separator />
                <p className="text-sm">Content below separator</p>
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-3">Card Variations</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Simple Card</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Basic card with header and content.
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-dashed">
                  <CardContent className="flex items-center justify-center h-32">
                    <div className="text-center">
                      <Plus className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                      <p className="text-sm text-muted-foreground">
                        Dashed Card
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-primary text-primary-foreground">
                  <CardHeader>
                    <CardTitle>Primary Card</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm opacity-90">
                      Card with primary background.
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sidebar Testing */}
      <Card>
        <CardHeader>
          <CardTitle>Sidebar Testing</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Sidebar with Items */}
            <div className="space-y-2">
              <h4 className="font-medium">With Items</h4>
              <div className="h-80 border rounded-lg overflow-hidden">
                <Sidebar
                  title="XAgents"
                  items={mockSidebarItems}
                  isActiveItem={(item) => item.id === "1"}
                />
              </div>
            </div>

            {/* Loading Sidebar */}
            <div className="space-y-2">
              <h4 className="font-medium">Loading State</h4>
              <div className="h-80 border rounded-lg overflow-hidden">
                <Sidebar title="XAgents" isLoading={true} />
              </div>
            </div>

            {/* Sidebar with Placeholder */}
            <div className="space-y-2">
              <h4 className="font-medium">Empty State</h4>
              <div className="h-80 border rounded-lg overflow-hidden">
                <Sidebar
                  title="XAgents"
                  items={[]}
                  placeholder={
                    <div className="text-center text-muted-foreground">
                      <div className="bg-muted/30 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                        <Plus className="h-5 w-5" />
                      </div>
                      <p className="text-sm font-medium mb-1">
                        No XAgents found
                      </p>
                      <p className="text-xs opacity-75">
                        Create a new XAgent to get started
                      </p>
                    </div>
                  }
                />
              </div>
            </div>

            {/* Sidebar with Custom Children */}
            <div className="space-y-2">
              <h4 className="font-medium">Custom Content</h4>
              <div className="h-80 border rounded-lg overflow-hidden">
                <Sidebar title="Custom">
                  <div className="p-4 space-y-3">
                    <div className="bg-accent/20 rounded-lg p-3">
                      <h5 className="font-medium text-sm">Custom Section 1</h5>
                      <p className="text-xs text-muted-foreground mt-1">
                        This is custom content in the sidebar
                      </p>
                    </div>
                    <div className="bg-primary/10 rounded-lg p-3">
                      <h5 className="font-medium text-sm">Custom Section 2</h5>
                      <p className="text-xs text-muted-foreground mt-1">
                        You can put anything here
                      </p>
                    </div>
                  </div>
                </Sidebar>
              </div>
            </div>

            {/* Sidebar without Title */}
            <div className="space-y-2">
              <h4 className="font-medium">No Title</h4>
              <div className="h-80 border rounded-lg overflow-hidden">
                <Sidebar
                  items={mockSidebarItems.slice(0, 2)}
                  isActiveItem={(item) => item.id === "2"}
                />
              </div>
            </div>

            {/* Minimal Sidebar */}
            <div className="space-y-2">
              <h4 className="font-medium">Minimal</h4>
              <div className="h-80 border rounded-lg overflow-hidden">
                <Sidebar
                  items={[
                    { id: "simple1", title: "Simple Item 1" },
                    { id: "simple2", title: "Simple Item 2" },
                    { id: "simple3", title: "Simple Item 3" },
                  ]}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
