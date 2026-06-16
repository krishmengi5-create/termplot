import sys
import os
import argparse
from termplot.plotter import Plotter, COLORS, COLOR_LIST
from termplot.evaluator import safe_eval

def get_key():
    import select
    try:
        import tty
        import termios
    except ImportError:
        return None
        
    fd = sys.stdin.fileno()
    try:
        old_settings = termios.tcgetattr(fd)
    except Exception:
        return None
        
    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if rlist:
            key = sys.stdin.read(1)
            if key == '\x1b':
                rlist, _, _ = select.select([sys.stdin], [], [], 0.02)
                if rlist:
                    key += sys.stdin.read(2)
            return key
    except Exception:
        pass
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            pass
    return None

def main():
    parser = argparse.ArgumentParser(
        description="TermPlot: High-Resolution Mathematical Function Visualizer in the Terminal using Braille Graphics.",
        epilog="Examples:\n  python3 main.py \"sin(x)\"\n  python3 main.py \"sin(x)\" \"cos(x/2)\" --xmin -5 --xmax 5\n  python3 main.py --interactive",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("functions", nargs="*", help="Mathematical expressions in terms of x to plot")
    parser.add_argument("--xmin", type=float, default=-10.0, help="Minimum X bound (default: -10)")
    parser.add_argument("--xmax", type=float, default=10.0, help="Maximum X bound (default: 10)")
    parser.add_argument("--ymin", type=float, default=-5.0, help="Minimum Y bound (default: -5)")
    parser.add_argument("--ymax", type=float, default=5.0, help="Maximum Y bound (default: 5)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Launch interactive mode even if functions are passed")
    parser.add_argument("--export-html", type=str, help="Export a static HTML file of the plot and exit")
    parser.add_argument("--export-txt", type=str, help="Export a plain text file of the plot and exit")
    
    args = parser.parse_args()
    
    functions = []
    for idx, expr in enumerate(args.functions):
        functions.append({
            "expr": expr,
            "color": COLOR_LIST[idx % len(COLOR_LIST)]
        })
        
    is_interactive = args.interactive or (not args.functions and not args.export_html and not args.export_txt)
    
    if is_interactive and not functions:
        functions.append({"expr": "sin(x)", "color": "cyan"})
        functions.append({"expr": "cos(2x)", "color": "green"})
        
    try:
        term_w, term_h = os.get_terminal_size()
    except Exception:
        term_w, term_h = 80, 24
        
    plot_w = max(30, term_w - 14)
    plot_h = max(10, term_h - 7 if is_interactive else term_h - 6)
    
    plotter = Plotter(char_width=plot_w, char_height=plot_h)
    plotter.set_bounds(args.xmin, args.xmax, args.ymin, args.ymax)
    
    if args.export_html:
        export_to_html(plotter, functions, args.export_html)
        return
        
    if args.export_txt:
        export_to_txt(plotter, functions, args.export_txt)
        return
        
    if not is_interactive:
        screen = plotter.build_full_screen(functions, interactive=False)
        print(screen)
        return
        
    help_open = False
    dirty = True
    print("\033[H\033[J", end="")
    
    try:
        while True:
            try:
                curr_w, curr_h = os.get_terminal_size()
            except Exception:
                curr_w, curr_h = 80, 24
                
            p_w = max(30, curr_w - 14)
            p_h = max(10, curr_h - (18 if help_open else 7))
            
            if p_w != plotter.char_width or p_h != plotter.char_height:
                plotter.char_width = p_w
                plotter.char_height = p_h
                dirty = True
                
            if dirty:
                screen_content = plotter.build_full_screen(functions, interactive=True, help_open=help_open)
                print("\033[H" + screen_content)
                dirty = False
                
            key = get_key()
            if not key:
                continue
                
            key_lower = key.lower()
            
            if key in ('q', 'Q', '\x03'):
                print("\n" * 3)
                print(f"{COLORS['bold']}Thank you for using TermPlot!{COLORS['reset']}")
                break
                
            elif key_lower == 'w' or key == '\x1b[A':
                plotter.pan(0, 0.15)
                dirty = True
            elif key_lower == 's' or key == '\x1b[B':
                plotter.pan(0, -0.15)
                dirty = True
            elif key_lower == 'a' or key == '\x1b[D':
                plotter.pan(-0.15, 0)
                dirty = True
            elif key_lower == 'd' or key == '\x1b[C':
                plotter.pan(0.15, 0)
                dirty = True
                
            elif key in ('+', '='):
                plotter.zoom(0.8)
                dirty = True
            elif key in ('-', '_'):
                plotter.zoom(1.25)
                dirty = True
                
            elif key_lower == 'r':
                plotter.reset_view()
                dirty = True
                
            elif key_lower == 'h':
                help_open = not help_open
                dirty = True
                
            elif key_lower == 'c':
                functions = []
                dirty = True
                
            elif key_lower == 'f':
                print("\033[H\033[J", end="")
                print(f"{COLORS['bold']}{COLORS['cyan']}=== Add New Mathematical Function ==={COLORS['reset']}")
                print(f"Supported functions: sin(x), cos(x), tan(x), sqrt(x), exp(x), log(x), abs(x), etc.")
                print(f"Example: sin(x) * cos(x/2) + 1")
                print("-" * 50)
                
                try:
                    expr_input = input("\nEnter function: f(x) = ").strip()
                    if expr_input:
                        test_val = safe_eval(expr_input, 1.0)
                        functions.append({
                            "expr": expr_input,
                            "color": COLOR_LIST[len(functions) % len(COLOR_LIST)]
                        })
                        print(f"\n{COLORS['green']}\u2713 Added f{len(functions)}(x) = {expr_input}{COLORS['reset']}")
                    else:
                        print(f"\n{COLORS['yellow']}Cancelled.{COLORS['reset']}")
                except Exception as e:
                    print(f"\n{COLORS['red']}Error: Invalid mathematical expression! ({e}){COLORS['reset']}")
                    
                print("\nPress Enter to return to plot...")
                input()
                print("\033[H\033[J", end="")
                dirty = True
    except KeyboardInterrupt:
        print("\n" * 3)
        print(f"{COLORS['bold']}Thank you for using TermPlot!{COLORS['reset']}")

def export_to_txt(plotter, functions, path):
    screen = plotter.build_full_screen(functions, interactive=False)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(screen)
        print(f"Plot successfully exported as text to: {path}")
    except Exception as e:
        print(f"Failed to export text: {e}")

def export_to_html(plotter, functions, path):
    screen = plotter.build_full_screen(functions, interactive=False)
    html_content = ansi_to_html(screen)
    
    template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TermPlot Export - Math Visualizer</title>
    <style>
        body {{
            background-color: #0f141c;
            color: #abb2bf;
            font-family: 'Fira Code', 'Courier New', Courier, monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .terminal-window {{
            background-color: #05080c;
            border: 1px solid #1e293b;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            max-width: 95vw;
            width: fit-content;
        }}
        .terminal-header {{
            background-color: #0f172a;
            padding: 10px 15px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #1e293b;
            border-radius: 8px 8px 0 0;
        }}
        .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .red-dot {{ background-color: #ef4444; }}
        .yellow-dot {{ background-color: #eab308; }}
        .green-dot {{ background-color: #22c55e; }}
        .title {{
            color: #94a3b8;
            font-size: 14px;
            margin-left: auto;
            margin-right: auto;
            font-weight: bold;
        }}
        .terminal-body {{
            padding: 20px;
            overflow-x: auto;
            white-space: pre;
            line-height: 1.25;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 20px;
            color: #64748b;
            font-size: 12px;
            text-align: center;
        }}
        a {{
            color: #38bdf8;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="terminal-window">
        <div class="terminal-header">
            <div class="dot red-dot"></div>
            <div class="dot yellow-dot"></div>
            <div class="dot green-dot"></div>
            <div class="title">termplot --export</div>
        </div>
        <div class="terminal-body">{{html_content}}</div>
    </div>
    <div class="footer">
        Generated by <a href="https://github.com/krishmengi5-create/termplot" target="_blank">TermPlot</a> \u2014 Interactive Terminal Math Visualizer
    </div>
</body>
</html>
"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(template)
        print(f"Plot successfully exported as HTML to: {path}")
    except Exception as e:
        print(f"Failed to export HTML: {e}")

def ansi_to_html(text):
    replacements = [
        ('\033[91m', '<span style="color: #f87171;">'),
        ('\033[92m', '<span style="color: #4ade80;">'),
        ('\033[93m', '<span style="color: #facc15;">'),
        ('\033[94m', '<span style="color: #60a5fa;">'),
        ('\033[95m', '<span style="color: #c084fc;">'),
        ('\033[96m', '<span style="color: #2dd4bf;">'),
        ('\033[97m', '<span style="color: #f1f5f9;">'),
        ('\033[90m', '<span style="color: #475569;">'),
        ('\033[1m', '<span style="font-weight: bold;">'),
        ('\033[0m', '</span>'),
    ]
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for ansi, html in replacements:
        escaped = escaped.replace(ansi, html)
    return escaped
