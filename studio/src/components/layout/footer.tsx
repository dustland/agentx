export function Footer() {
  return (
    <footer className="border-t bg-white/50 dark:bg-slate-900/50 backdrop-blur-md">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-sm text-slate-600 dark:text-slate-400">
            © 2024 AgentX Studio. Built with Next.js and AgentX Framework.
          </div>
          <div className="flex space-x-6 text-sm">
            <a
              href="https://github.com/your-org/agentx"
              className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
            >
              Documentation
            </a>
            <a
              href="https://github.com/your-org/agentx/issues"
              className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
            >
              Support
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}