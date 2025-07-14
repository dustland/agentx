# AgentX Studio

A modern, unified web interface for AgentX task execution and observability.

## Features

- **Task Executor**: Create and monitor AI agent tasks in real-time
- **Observability Dashboard**: Comprehensive metrics and monitoring
- **Agent Performance**: Track individual agent performance and success rates
- **Artifact Browser**: View and download generated artifacts
- **Real-time Updates**: Live task status and message streaming
- **Dark Mode**: Automatic theme detection with manual toggle

## Tech Stack

- **Next.js 15** with App Router and Turbopack
- **React 19** with Server Components
- **TypeScript** for type safety
- **Tailwind CSS v4** for styling
- **Radix UI** for accessible components
- **React Query** for data fetching
- **Framer Motion** for animations

## Quick Start

### From AgentX Project

```bash
# Install dependencies and set up UI components
agentx studio setup

# Start development server
agentx studio dev

# Or just start the studio
agentx studio start --open
```

### Standalone Development

```bash
# One-time setup (updates to latest versions and installs components)
pnpm run setup

# Or manually:
pnpm update --latest    # Update all dependencies to latest
pnpm install           # Install dependencies
./setup-ui.sh          # Install shadcn/ui components

# Start development server
pnpm dev

# Other commands
pnpm run update        # Update all dependencies
pnpm run typecheck     # Run TypeScript type checking
pnpm run build         # Build for production
pnpm run clean         # Clean install (removes node_modules and lockfile)
```

## Environment Variables

Create a `.env.local` file:

```env
# Required: AgentX API URL
AGENTX_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=/api/agentx

# Optional: Enable mock data for development
NEXT_PUBLIC_ENABLE_MOCK_DATA=false
```

## Deployment

### Railway

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Deploy
railway login
railway init
railway up
```

Set environment variables in Railway dashboard:
- `AGENTX_API_URL`: Your AgentX API deployment URL

### Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Nixpacks (Recommended for Railway)

The project includes `nixpacks.toml` configuration for optimal Railway deployment:

```toml
[phases.setup]
nixPkgs = ["nodejs_20", "pnpm"]

[phases.install]
cmds = ["pnpm install --frozen-lockfile"]

[phases.build]
cmds = ["pnpm run build"]

[start]
cmd = "pnpm run start"
```

Railway will automatically detect and use this configuration.

## API Integration

The studio connects to AgentX API through a proxy configuration in `next.config.js`:

```javascript
async rewrites() {
  return [
    {
      source: '/api/agentx/:path*',
      destination: `${process.env.AGENTX_API_URL}/:path*`,
    },
  ]
}
```

This allows the frontend to make requests to `/api/agentx/*` which are proxied to your AgentX backend.

## Development

### Project Structure

```
studio/
├── src/
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   │   ├── ui/          # shadcn/ui components
│   │   └── ...          # Feature components
│   ├── lib/             # Utilities and hooks
│   │   ├── hooks/       # Custom React hooks
│   │   ├── api.ts       # API client
│   │   └── utils.ts     # Helper functions
│   └── styles/          # Global styles
├── public/              # Static assets
└── components.json      # shadcn/ui configuration
```

### Adding New Components

Use the shadcn/ui CLI to add components:

```bash
pnpm dlx shadcn@latest add <component-name>
```

### Testing

```bash
# Run type checking
pnpm tsc --noEmit

# Run linting
pnpm lint

# Run in development with hot reload
pnpm dev
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Part of the AgentX project. See the main repository for license information.