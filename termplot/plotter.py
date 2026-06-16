import os
import math
from termplot.evaluator import safe_eval

# ANSI color codes
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'reset': '\033[0m',
    'gray': '\033[90m',
    'bold': '\033[1m'
}

COLOR_LIST = ['cyan', 'green', 'magenta', 'yellow', 'red', 'blue']

class Plotter:
    def __init__(self, char_width=80, char_height=20):
        self.char_width = char_width
        self.char_height = char_height
        
        # Default boundaries
        self.xmin = -10.0
        self.xmax = 10.0
        self.ymin = -5.0
        self.ymax = 5.0
        
        # Braille dot mapping
        self.dot_map = {
            (0, 0): 0x01,
            (0, 1): 0x02,
            (0, 2): 0x04,
            (0, 3): 0x40,
            (1, 0): 0x08,
            (1, 1): 0x10,
            (1, 2): 0x20,
            (1, 3): 0x80
        }
        
    def set_bounds(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        
    def reset_view(self):
        self.xmin = -10.0
        self.xmax = 10.0
        self.ymin = -5.0
        self.ymax = 5.0
        
    def zoom(self, factor):
        # Zoom around the center
        x_center = (self.xmin + self.xmax) / 2.0
        y_center = (self.ymin + self.ymax) / 2.0
        
        x_half_range = ((self.xmax - self.xmin) / 2.0) * factor
        y_half_range = ((self.ymax - self.ymin) / 2.0) * factor
        
        self.xmin = x_center - x_half_range
        self.xmax = x_center + x_half_range
        self.ymin = y_center - y_half_range
        self.ymax = y_center + y_half_range
        
    def pan(self, dx_fraction, dy_fraction):
        x_range = self.xmax - self.xmin
        y_range = self.ymax - self.ymin
        
        shift_x = x_range * dx_fraction
        shift_y = y_range * dy_fraction
        
        self.xmin += shift_x
        self.xmax += shift_x
        self.ymin += shift_y
        self.ymax += shift_y

    def render(self, functions):
        W, H = self.char_width, self.char_height
        sub_width = W * 2
        sub_height = H * 4
        
        # Grid of active dots per cell
        grid = [[0 for _ in range(W)] for _ in range(H)]
        # Cell color map
        grid_color = [[None for _ in range(W)] for _ in range(H)]
        
        # Plot each function
        for func_idx, fn in enumerate(functions):
            expr = fn["expr"]
            color_name = fn.get("color", COLOR_LIST[func_idx % len(COLOR_LIST)])
            color_code = COLORS.get(color_name, COLORS['white'])
            
            for px in range(sub_width):
                # Calculate mathematical x
                x = self.xmin + (px / (sub_width - 1)) * (self.xmax - self.xmin) if sub_width > 1 else self.xmin
                y = safe_eval(expr, x)
                
                if y is not None and self.ymin <= y <= self.ymax:
                    # Calculate virtual py
                    py = ((y - self.ymin) / (self.ymax - self.ymin)) * (sub_height - 1) if (self.ymax - self.ymin) > 0 else 0
                    v_row = int(sub_height - 1 - py)
                    v_col = px
                    
                    cx, dx = divmod(v_col, 2)
                    cy, dy = divmod(v_row, 4)
                    
                    if 0 <= cx < W and 0 <= cy < H:
                        grid[cy][cx] |= self.dot_map[(dx, dy)]
                        # Assign color
                        if grid_color[cy][cx] is None:
                            grid_color[cy][cx] = color_code
                            
        # Compute axes character rows/cols
        if self.ymin <= 0 <= self.ymax:
            py_zero = ((0 - self.ymin) / (self.ymax - self.ymin)) * (sub_height - 1) if (self.ymax - self.ymin) > 0 else 0
            cy_zero = int(sub_height - 1 - py_zero) // 4
        else:
            cy_zero = -1
            
        if self.xmin <= 0 <= self.xmax:
            px_zero = ((0 - self.xmin) / (self.xmax - self.xmin)) * (sub_width - 1) if (self.xmax - self.xmin) > 0 else 0
            cx_zero = int(px_zero) // 2
        else:
            cx_zero = -1
            
        # Compile composite background and dots
        lines = []
        for r in range(H):
            row_str = ""
            for c in range(W):
                if grid[r][c] != 0:
                    color = grid_color[r][c] or COLORS['white']
                    row_str += color + chr(0x2800 + grid[r][c]) + COLORS['reset']
                else:
                    is_x_axis = (r == cy_zero)
                    is_y_axis = (c == cx_zero)
                    
                    if is_x_axis and is_y_axis:
                        row_str += COLORS['gray'] + "┼" + COLORS['reset']
                    elif is_x_axis:
                        row_str += COLORS['gray'] + "─" + COLORS['reset']
                    elif is_y_axis:
                        row_str += COLORS['gray'] + "│" + COLORS['reset']
                    elif r % 4 == 0 and c % 10 == 0:
                        row_str += COLORS['gray'] + "·" + COLORS['reset']
                    else:
                        row_str += " "
            lines.append(row_str)
            
        return lines

    def build_full_screen(self, functions, interactive=True, help_open=False):
        plot_lines = self.render(functions)
        
        y_labels = []
        for r in range(self.char_height):
            frac = (self.char_height - 1 - r) / (self.char_height - 1) if self.char_height > 1 else 0.5
            y_val = self.ymin + frac * (self.ymax - self.ymin)
            if abs(y_val) < 1e-10:
                y_val = 0.0
            label_str = f"{y_val:10.4g} "
            y_labels.append(label_str)
            
        top_border = COLORS['gray'] + "┌" + "─" * self.char_width + "┐" + COLORS['reset']
        bottom_border = COLORS['gray'] + "└" + "─" * self.char_width + "┘" + COLORS['reset']
        
        frame_lines = []
        frame_lines.append(" " * 11 + top_border)
        
        for r in range(self.char_height):
            left_lbl = COLORS['bold'] + y_labels[r] + COLORS['reset']
            left_border = COLORS['gray'] + "│" + COLORS['reset']
            right_border = COLORS['gray'] + "│" + COLORS['reset']
            frame_lines.append(f"{left_lbl}{left_border}{plot_lines[r]}{right_border}")
            
        frame_lines.append(" " * 11 + bottom_border)
        
        center_x = (self.xmin + self.xmax) / 2.0
        xmin_str = f"{self.xmin:.4g}"
        center_str = f"{center_x:.4g}"
        xmax_str = f"{self.xmax:.4g}"
        
        spacing1 = max(1, (self.char_width // 2) - len(xmin_str) - (len(center_str) // 2))
        spacing2 = max(1, self.char_width - len(xmin_str) - spacing1 - len(center_str) - len(xmax_str))
        
        x_axis_ticks = " " * 12 + COLORS['bold'] + xmin_str + " " * spacing1 + center_str + " " * spacing2 + xmax_str + COLORS['reset']
        frame_lines.append(x_axis_ticks)
        
        legend_parts = []
        for idx, fn in enumerate(functions):
            expr = fn["expr"]
            color_name = fn.get("color", COLOR_LIST[idx % len(COLOR_LIST)])
            color_code = COLORS.get(color_name, COLORS['white'])
            legend_parts.append(f"{color_code}● f{idx+1}(x) = {expr}{COLORS['reset']}")
            
        legend_line = " " * 12 + "  ".join(legend_parts)
        frame_lines.append("")
        frame_lines.append(legend_line)
        
        if interactive:
            info_line = COLORS['gray'] + " " * 12 + "Controls: [WASD] Pan | [+-] Zoom | [F] Add Func | [C] Clear | [R] Reset | [H] Help | [Q] Quit" + COLORS['reset']
            frame_lines.append(info_line)
            
            if help_open:
                help_box = [
                    COLORS['yellow'] + "┌─────────────────────────────────────────────────────────────────────────────┐" + COLORS['reset'],
                    COLORS['yellow'] + "│                       TermPlot Interactive Help Guide                       │" + COLORS['reset'],
                    COLORS['yellow'] + "├─────────────────────────────────────────────────────────────────────────────┤" + COLORS['reset'],
                    COLORS['yellow'] + "│  [W] or [Up Arrow]    : Pan Up      │  [+] or [=]            : Zoom In      │" + COLORS['reset'],
                    COLORS['yellow'] + "│  [S] or [Down Arrow]  : Pan Down    │  [-] or [_]            : Zoom Out     │" + COLORS['reset'],
                    COLORS['yellow'] + "│  [A] or [Left Arrow]  : Pan Left    │  [R] or [r]            : Reset View   │" + COLORS['reset'],
                    COLORS['yellow'] + "│  [D] or [Right Arrow] : Pan Right   │  [F] or [f]            : Add Function │" + COLORS['reset'],
                    COLORS['yellow'] + "│  [C] or [c]           : Clear All   │  [H] or [h]            : Toggle Help  │" + COLORS['reset'],
                    COLORS['yellow'] + "├─────────────────────────────────────────────────────────────────────────────┤" + COLORS['reset'],
                    COLORS['yellow'] + "│  Supported Math: sin(x), cos(x), tan(x), sqrt(x), abs(x), exp(x), log(x),   │" + COLORS['reset'],
                    COLORS['yellow'] + "│                  pi, e, ^ or ** (power), implicit mult (e.g. 2x, 5sin(x))   │" + COLORS['reset'],
                    COLORS['yellow'] + "└─────────────────────────────────────────────────────────────────────────────┘" + COLORS['reset']
                ]
                frame_lines.append("")
                for line in help_box:
                    frame_lines.append(" " * 6 + line)
                    
        return "\n".join(frame_lines)
