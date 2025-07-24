# VibeX Web

A modern, unified web interface for VibeX task execution and observability.

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

### From VibeX Project

```bash
# Install dependencies and set up UI components
vibex web setup

# Start development server
vibex web dev

# Or just start the web interface
vibex web start --open
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
# Required: VibeX API URL
VIBEX_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=/api/vibex

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

#### Configure Persistent Storage

VibeX requires persistent storage for task data, agent memory, and artifacts. After deployment:

1. **Create a Volume** in Railway dashboard:
   - Go to your project settings
   - Add a new volume
   - Name it (e.g., "vibex-data")

2. **Mount the Volume**:
   - Mount path: `/app/.vibex`
   - This preserves all task data between deployments

3. **Set Environment Variables** in Railway dashboard:
   - `VIBEX_API_URL`: Your VibeX API deployment URL (if separate)
   - `PORT`: `7770` (Railway usually sets this automatically)

**Note**: Without a volume, all task data and agent memory will be lost on each deployment or container restart.

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

The web interface connects to VibeX API through a proxy configuration in `next.config.js`:

```javascript
async rewrites() {
  return [
    {
      source: '/api/vibex/:path*',
      destination: `${process.env.VIBEX_API_URL}/:path*`,
    },
  ]
}
```

This allows the frontend to make requests to `/api/vibex/*` which are proxied to your VibeX backend.

## Development

### Project Structure

```
web/
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

Part of the VibeX project. See the main repository for license information.