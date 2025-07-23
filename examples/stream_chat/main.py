#!/usr/bin/env python3
import asyncio
import sys
import argparse
import time
from pathlib import Path
from vibex.core.xagent import XAgent
from vibex.config.team_loader import load_team_config
from vibex.utils.logger import get_logger

logger = get_logger(__name__)

# ANSI color codes for pretty output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

async def stream_response(x: XAgent, message: str, show_streaming: bool = False, auto_execute: bool = False):
    """Send a message and optionally show streaming progress."""
    if show_streaming:
        print(f"{Colors.CYAN}X: {Colors.END}", end='', flush=True)
        
        # Track streaming chunks
        chunk_count = 0
        start_time = time.time()
        
        # Mock streaming display (since we can't directly access chunks from here)
        # In a real implementation, you'd hook into the streaming events
        response = await x.chat(message)
        
        # Show the complete response
        print(f"{Colors.YELLOW}{response.text}{Colors.END}")
        
        elapsed = time.time() - start_time
        print(f"{Colors.GREEN}✓ Response completed in {elapsed:.2f}s{Colors.END}")
    else:
        # Simple response without streaming visualization
        print(f"{Colors.CYAN}X: {Colors.END}", end='', flush=True)
        response = await x.chat(message)
        print(response.text)
    
    # Show additional info if available
    if response.preserved_steps:
        print(f"  {Colors.MAGENTA}(Preserved {len(response.preserved_steps)} completed steps){Colors.END}")
    if response.regenerated_steps:
        print(f"  {Colors.MAGENTA}(Regenerated {len(response.regenerated_steps)} steps){Colors.END}")
    
    # Auto-execute plan if created and auto_execute is True
    if auto_execute and x.plan and response.metadata.get('execution_type') == 'plan_created':
        print(f"\n{Colors.BLUE}🚀 Auto-executing plan...{Colors.END}\n")
        
        # Execute the plan step by step
        while not x.is_complete:
            step_start = time.time()
            print(f"{Colors.YELLOW}Executing next step...{Colors.END}")
            
            step_result = await x.step()
            
            # Clean up and display step result
            if step_result:
                # Remove excessive newlines and format nicely
                lines = step_result.strip().split('\n')
                for line in lines:
                    if line.strip():
                        if line.startswith('✅'):
                            print(f"{Colors.GREEN}{line}{Colors.END}")
                        elif line.startswith('❌'):
                            print(f"{Colors.RED}{line}{Colors.END}")
                        elif line.startswith('⚠️'):
                            print(f"{Colors.YELLOW}{line}{Colors.END}")
                        elif line.startswith('🎉'):
                            print(f"{Colors.MAGENTA}{Colors.BOLD}{line}{Colors.END}")
                        else:
                            print(line)
                
                step_elapsed = time.time() - step_start
                print(f"{Colors.GREEN}  (Step completed in {step_elapsed:.2f}s){Colors.END}\n")
            
            # Check if we should continue
            if "All tasks completed successfully" in step_result or "Task execution halted" in step_result:
                break
    
    return response

async def main():
    parser = argparse.ArgumentParser(
        description='VibeX Simple Chat - Interactive or single-shot mode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default)
  python main.py

  # Single message mode
  python main.py --message "What is the capital of France?"

  # Single message with streaming display
  python main.py --message "Tell me a joke" --stream

  # Auto-execute a plan after creation
  python main.py --message "Plan a 3 day trip to SF" --auto-execute

  # Auto-execute with streaming
  python main.py --message "Write a blog post about AI" --stream --auto-execute

  # Create a new task with custom ID
  python main.py --task-id my-task-123 --message "Hello!"

  # Resume an existing task
  python main.py --resume .vibex/tasks/abc123 --message "Continue our conversation"
"""
    )
    
    parser.add_argument('-m', '--message', 
                        help='Single message to send (exits after response)')
    parser.add_argument('-s', '--stream', 
                        action='store_true',
                        help='Show streaming progress (for single message mode)')
    parser.add_argument('-a', '--auto-execute',
                        action='store_true',
                        default=True,
                        help='Automatically execute plan after creation (default: True)')
    parser.add_argument('--no-auto-execute',
                        dest='auto_execute',
                        action='store_false',
                        help='Disable automatic plan execution')
    parser.add_argument('-t', '--task-id',
                        help='Custom task ID to use')
    parser.add_argument('-r', '--resume',
                        help='Resume from existing task directory')
    parser.add_argument('-c', '--config',
                        default='config/team.yaml',
                        help='Path to team config (default: config/team.yaml)')
    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='Minimal output mode')
    
    args = parser.parse_args()
    
    # Resolve config path
    config_path = Path(__file__).parent / args.config
    if not config_path.exists():
        print(f"{Colors.RED}❌ Config file not found: {config_path}{Colors.END}")
        sys.exit(1)
    
    # Header
    if not args.quiet:
        print(f"{Colors.BOLD}{Colors.CYAN}🤖 VibeX Simple Chat{Colors.END}")
        print(f"Config: {config_path}")
        if args.task_id:
            print(f"Task ID: {args.task_id}")
        if args.resume:
            print(f"Resuming from: {args.resume}")
        print()

    # Initialize XAgent
    try:
        team_config = load_team_config(str(config_path))
        
        kwargs = {'team_config': team_config}
        if args.task_id:
            kwargs['task_id'] = args.task_id
        if args.resume:
            kwargs['taskspace_dir'] = Path(args.resume)
            
        x = XAgent(**kwargs)
        
        if not args.quiet:
            print(f"{Colors.GREEN}✓ XAgent initialized (Task ID: {x.task_id}){Colors.END}")
            print()
        
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to initialize XAgent: {e}{Colors.END}")
        logger.error(f"Initialization failed: {e}", exc_info=True)
        sys.exit(1)

    # Single message mode
    if args.message:
        if not args.quiet:
            print(f"{Colors.BLUE}You: {args.message}{Colors.END}")
        
        try:
            await stream_response(x, args.message, args.stream, args.auto_execute)
            
            if not args.quiet:
                print(f"\n{Colors.GREEN}✓ Task completed successfully{Colors.END}")
                print(f"Task data saved to: .vibex/tasks/{x.task_id}/")
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
            logger.error(f"Chat failed: {e}", exc_info=True)
            sys.exit(1)
    
    # Interactive mode
    else:
        if not args.quiet:
            print("Interactive mode started! Type 'quit' or 'q' to exit.")
            print("Type '/help' for available commands.")
            print()

        # Start the conversation loop
        while True:
            try:
                user_input = input(f"{Colors.BLUE}You: {Colors.END}").strip()
                
                # Check for commands
                if user_input.lower() in ['quit', 'q', 'exit']:
                    break
                elif user_input == '/help':
                    print(f"{Colors.CYAN}Available commands:{Colors.END}")
                    print("  /help    - Show this help")
                    print("  /status  - Show current task status")
                    print("  /plan    - Show current plan (if any)")
                    print("  /clear   - Clear screen")
                    print("  quit/q   - Exit the chat")
                    continue
                elif user_input == '/status':
                    print(f"Task ID: {x.task_id}")
                    print(f"Has plan: {'Yes' if x.plan else 'No'}")
                    print(f"Is complete: {'Yes' if x.is_complete else 'No'}")
                    continue
                elif user_input == '/plan':
                    if x.plan:
                        print(f"Goal: {x.plan.goal}")
                        print(f"Tasks: {len(x.plan.tasks)}")
                        for i, task in enumerate(x.plan.tasks, 1):
                            status_icon = "✓" if task.status == "completed" else "○"
                            print(f"  {status_icon} {i}. {task.name} ({task.status})")
                    else:
                        print("No plan created yet.")
                    continue
                elif user_input == '/clear':
                    print("\033[H\033[J", end='')
                    continue
                elif not user_input:
                    continue

                # Chat with X
                await stream_response(x, user_input, args.stream, args.auto_execute)

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Interrupted!{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.END}")
                logger.error(f"Chat error: {e}", exc_info=True)
        
        if not args.quiet:
            print(f"\n{Colors.GREEN}Chat session ended.{Colors.END}")
            print(f"Task data saved to: .vibex/tasks/{x.task_id}/")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Goodbye!{Colors.END}")
