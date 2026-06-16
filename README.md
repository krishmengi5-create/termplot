# 📊 TermPlot

> **An interactive, high-resolution mathematical function visualizer built entirely for the command line.**

`TermPlot` is a lightweight, zero-dependency command-line utility written in Python that allows you to plot and explore mathematical functions directly in your terminal. By utilizing Unicode **Braille characters** (`\u2800` to `\u28FF`) as a 2x4 sub-pixel matrix, `TermPlot` achieves an effective resolution **8 times higher** than traditional block-based terminal plotters!

Explore complex sine waves, quadratics, exp/log behaviors, or your own custom mathematical equations in a fluid, interactive terminal UI with full support for panning, zooming, color legends, and dynamic terminal window resizing.

---

## 🎨 Interactive Preview

```
│                    
   ⢀⠔⠑⢄            │   ⠠⠊⒜             
  ⢀⠂   ⠄           │  ⠠⠁  ⠈⢄            
  ⠄    ⠈⢄          │  ⠂    ⠠            
 ⠠      ⢀          │ ⢈      ⠂           
 ⠂       ⠄         │⢀       ⠈           
⢐        ⠠         │⢀        ⠁          
⠂─────────⠄────────⢀─────────⠈─────────⢐
          ⠠        ⢀          ⠁        ⠂
           ⠄      ⢀│          ⠈⢄      ⢐ 
           ⢐      ⠄│           ⢀      ⠁ 
            ⢁    ⢐ │            ⠄    ⢈  
             ⢄  ⠠⠁ │            ⠈⢄  ⢐   
              ⢒⢔⠁  │             ⠈⢢⠊    
                   │
```

---

## 🚀 Key Features

*   **Subpixel Rendering**: Employs a custom Braille-mapping coordinate engine to turn every terminal character cell into a 2x4 pixel grid (virtual 160x96 canvas in an 80x24 space).
*   **Fluid Interactive Mode**: Pan around the cartesian plane and zoom in/out with real-time screen redraws.
*   **Interactive Expression Parser**: Securely preprocesses and evaluates standard mathematical strings in terms of `x` (e.g. `sin(x) * x` or `cos(2x)`). Supports implicit multiplication (e.g., `2x` instead of `2*x`).
*   **Multi-Function Overlays**: Plots multiple curves simultaneously, styled with vibrant ANSI escape colors and auto-managed legends.
*   **Grid and Axis Compositing**: Draws crisp horizontal/vertical axes and dynamic reference grid ticks in the background.
*   **Dynamic Resize Handling**: Listens to terminal window size changes and scales the visualization grid in real time.
*   **Export Capabilities**: Save your high-fidelity terminal renders as beautifully styled, standalone `.html` web pages or plain `.txt` files.
*   **Zero External Dependencies**: Standard library Python. No installation bloat!

---

## 🛠️ Installation

Clone the repository and install it locally:

```bash
git clone https://github.com/krishmengi5-create/termplot.git
cd termplot
pip install -e .
```

Alternatively, you can run the tool directly as a standalone script:

```bash
python3 main.py --interactive
```

---

## 📖 Usage Guide

`TermPlot` supports both **Interactive Mode** (visual, real-time control) and **Command Line Mode** (instant plotting/exporting).

### 🕹️ 1. Interactive Mode
Launch interactive mode with a default sine/cosine set or with custom functions:

```bash
# Launch with default functions
termplot

# Launch with custom equations
termplot "sin(x)" "x^2 - 3" "exp(-0.2*x)"
```

#### Keyboard Controls:
*   `W` / `Up Arrow`    : Pan view **Up**
*   `S` / `Down Arrow`  : Pan view **Down**
*   `A` / `Left Arrow`  : Pan view **Left**
*   `D` / `Right Arrow` : Pan view **Right**
*   `+` / `=`           : **Zoom In** (narrow coordinate boundaries)
*   `-` / `_`           : **Zoom Out** (expand coordinate boundaries)
*   `F` / `f`           : **Add function** on-the-fly via input prompt
*   `C` / `c`           : **Clear** all functions to start fresh
*   `R` / `r`           : **Reset view** to default boundaries (`[-10, 10]`, `[-5, 5]`)
*   `H` / `h`           : Toggle the **Interactive Help Panel**
*   `Q` / `q`           : **Quit** the application

---

### 🖥️ 2. Single-Line Command Mode
Plot functions once and print them straight to the console:

```bash
# Plot sine and cosine over a custom range
termplot "sin(x)" "cos(x)" --xmin -3.14 --xmax 3.14 --ymin -1.2 --ymax 1.2
```

---

### 📄 3. Exporting Plots
Export stunning terminal-styled math graphs as static HTML files or plain text files:

```bash
# Export to a beautifully styled terminal HTML panel
termplot "sin(x)*cos(x/2)" --export-html my_plot.html

# Export to a text file with ANSI color codes intact
termplot "x^3 - 4x" --export-txt my_plot.txt
```

---

## 💡 Supported Math Syntax

Our safe parser compiles standard Python mathematical syntax. Supported operators/functions include:
*   **Variables**: `x`
*   **Trig**: `sin`, `cos`, `tan`, `asin`, `acos`, `atan` (and hyperbolic counterparts `sinh`, `cosh`, `tanh`)
*   **Exponential / Power**: `exp`, `log`, `log10`, `sqrt`, `^` or `**` (e.g., `x^2`, `x**3`)
*   **Constants**: `pi`, `e`
*   **Helper Utilities**: `abs`, `ceil`, `floor`
*   **Implicit Multiplication**: Common syntax like `2x` is auto-converted to `2*x`, `x(x-1)` becomes `x*(x-1)`, and `5sin(x)` becomes `5*sin(x)`.

---

## 🏗️ Architecture & Inner Workings

At its core, `TermPlot` represents character cells as 2x4 subpixel grids.
The terminal uses Unicode **Braille patterns** (`\u2800` - `\u28FF`) which consist of 8 dots.
A mathematical coordinate $(x, y)$ is mapped to a virtual coordinate:
$$\text{Virtual } X = \frac{x - x_{\min}}{x_{\max} - x_{\min}} \times (W \times 2)$$
$$\text{Virtual } Y = \frac{y - y_{\min}}{y_{\max} - y_{\min}} \times (H \times 4)$$

These virtual pixel offsets map to specific bits in the Braille block:
```
(dx=0, dy=0) -> Dot 1 (0x01)     (dx=1, dy=0) -> Dot 4 (0x08)
(dx=0, dy=1) -> Dot 2 (0x02)     (dx=1, dy=1) -> Dot 5 (0x10)
(dx=0, dy=2) -> Dot 3 (0x04)     (dx=1, dy=2) -> Dot 6 (0x20)
(dx=0, dy=3) -> Dot 7 (0x40)     (dx=1, dy=3) -> Dot 8 (0x80)
```
These are combined using bitwise `OR` operations for all points occupying the same character block.

---

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
