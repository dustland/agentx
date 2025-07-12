# AutoWriter Usage Guide

## Overview
AutoWriter is a professional multi-agent system that produces consulting-quality HTML reports. The system has been enhanced to generate outputs matching the quality of leading design agencies.

## Quick Start

### 1. Demo Mode (No API Keys Required)
To see a professional-quality sample output without API keys:

```bash
python3 demo_report.py
```

This generates a comprehensive web development trends report in `demo_output/web_development_trends_2025.html` that demonstrates:
- Modern design with Tailwind CSS
- Interactive ECharts visualizations
- Professional typography with Google Fonts
- Glassmorphism and advanced visual effects
- Smooth animations and micro-interactions
- Responsive mobile-first design

### 2. Full AutoWriter Mode (Requires API Keys)
To run the full AI-powered AutoWriter system:

1. Ensure you have API keys set in the project root `.env` file:
   ```
   DEEPSEEK_API_KEY=your_key_here
   # or OPENAI_API_KEY=your_key_here
   # or ANTHROPIC_API_KEY=your_key_here

   # Optional but recommended:
   SERPAPI_API_KEY=your_key_here
   
   # Note: Content extraction now uses Crawl4AI (open source)
   # No additional API keys needed for web scraping
   ```

2. Run the main script:
   ```bash
   python3 main.py
   ```

## Quality Standards

The enhanced AutoWriter now produces outputs that match or exceed the quality demonstrated in:
- `samples/design_trends_report.html` - Professional Chinese design report with advanced styling
- `samples/task1-sw.html` - Clean English technical report with charts

Key quality features implemented:
- **Visual Excellence**: Gradient backgrounds, glassmorphism effects, animated elements
- **Interactive Charts**: ECharts integration for data visualization
- **Typography**: Professional font combinations (Inter + Playfair Display)
- **Responsive Design**: Mobile-first approach with proper breakpoints
- **Micro-interactions**: Hover effects, smooth scrolling, fade-in animations
- **Accessibility**: ARIA labels, keyboard navigation, proper contrast ratios

## Output Structure

Generated reports include:
1. **Hero Section**: Eye-catching introduction with animated background
2. **Sticky Navigation**: Glassmorphism effect with smooth scroll indicators
3. **Content Sections**: Card-based layouts with proper spacing and shadows
4. **Interactive Visualizations**: Multiple chart types (line, radar, pie)
5. **Call-to-Action**: Professional footer with action buttons

## Customization

To generate reports on different topics, modify the `prompt` variable in `main.py`:

```python
prompt = """Generate a comprehensive report on [YOUR TOPIC HERE].
The report must match the quality of samples/design_trends_report.html..."""
```

## Troubleshooting

1. **API Key Issues**: Ensure your `.env` file is in the project root (`../../.env` from auto_writer)
2. **Python Version**: Requires Python 3.11+
3. **Dependencies**: Run `uv sync --dev` from project root if needed

## Sample Output

Open `demo_output/web_development_trends_2025.html` in your browser to see:
- Professional C-suite ready design
- Interactive data visualizations
- Smooth animations and transitions
- Mobile-responsive layout
- Modern UI/UX patterns

The output quality rivals professional agencies like Stripe, Vercel, and Linear.
