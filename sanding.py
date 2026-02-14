#!/usr/bin/env python3
"""
NONAGON FORGE - GUARANTEED SANDING VISUALIZER
Seismograph + Boulder Chase Visualization
"""

import turtle
import math
import time

# ====================
# CORE SANDING EQUATION
# ====================
def sanding_equation(E, N, A):
    """S = f(E × N) / A_thought"""
    if A == 0:
        A = 0.001
    return (E * N) / A

def ratchet_principle(values):
    """z_final = max(z) - Ratchet locks altitude"""
    max_val = values[0]
    result = []
    for v in values:
        max_val = max(max_val, v)
        result.append(max_val)
    return result

# ====================
# TURTLE VISUALIZATION ENGINE
# ====================
class ForgeVisualizer:
    def __init__(self):
        # Initialize screen
        self.screen = turtle.Screen()
        self.screen.setup(width=900, height=700)
        self.screen.bgcolor("black")
        self.screen.title("NONAGON FORGE - SANDING SEISMOGRAPH")
        
        # Hide default turtle
        turtle.hideturtle()
        turtle.speed(0)
        turtle.tracer(0, 0)  # Turn off animation for instant drawing
        
        # Initialize drawing turtles
        self.seismo = turtle.Turtle()
        self.seismo.hideturtle()
        self.seismo.speed(0)
        self.seismo.pensize(2)
        
        self.boulder = turtle.Turtle()
        self.boulder.hideturtle()
        self.boulder.speed(0)
        
        self.text = turtle.Turtle()
        self.text.hideturtle()
        self.text.speed(0)
        self.text.penup()
        
        # Colors from NONAGON palette
        self.colors = {
            'acid': '#00FF00',
            'magenta': '#FF00FF', 
            'cyan': '#00FFFF',
            'yellow': '#FFFF00',
            'red': '#FF5555',
            'blue': '#5555FF'
        }
        
        # Current parameters
        self.E = 5.0
        self.N = 5.0
        self.A = 2.0
        self.S_history = []
        
    def draw_grid(self):
        """Draw seismograph grid"""
        t = turtle.Turtle()
        t.hideturtle()
        t.speed(0)
        t.pencolor("#333333")
        t.penup()
        
        # Horizontal lines
        for y in range(-250, 301, 50):
            t.goto(-400, y)
            t.pendown()
            t.goto(400, y)
            t.penup()
            
        # Vertical lines (time markers)
        for x in range(-400, 401, 50):
            t.goto(x, -250)
            t.pendown()
            t.goto(x, 250)
            t.penup()
            
        # Center line (zero axis)
        t.pencolor("#555555")
        t.pensize(2)
        t.goto(-400, 0)
        t.pendown()
        t.goto(400, 0)
        t.penup()
        
    def draw_seismograph(self, S_value):
        """Draw seismograph wave based on S value"""
        self.seismo.clear()
        
        # Calculate wave parameters from S
        amplitude = S_value * 10
        frequency = S_value * 0.5
        noise = S_value * 0.3
        
        # Set color based on S
        if S_value > 8:
            color = self.colors['red']
        elif S_value > 4:
            color = self.colors['magenta']
        elif S_value > 1:
            color = self.colors['cyan']
        else:
            color = self.colors['acid']
            
        self.seismo.pencolor(color)
        self.seismo.penup()
        
        # Draw the wave
        x_start = -400
        self.seismo.goto(x_start, 0)
        self.seismo.pendown()
        
        for x in range(x_start, 401, 2):
            # Seismograph equation
            y = (amplitude * math.sin(x * frequency * 0.01) + 
                 noise * math.sin(x * frequency * 0.03) +
                 0.5 * amplitude * math.sin(x * 0.005))
            
            # Add ratchet effect (can't go below previous minimum)
            if len(self.S_history) > 1:
                base = max(0, min(self.S_history))
                y = max(y, base)
                
            self.seismo.goto(x, y)
            
        # Add to history and apply ratchet
        self.S_history.append(S_value)
        if len(self.S_history) > 100:
            self.S_history.pop(0)
            
    def draw_boulder(self, S_value):
        """Draw boulder that chases based on S"""
        self.boulder.clear()
        
        # Boulder size based on S
        boulder_size = min(100, S_value * 15)
        
        # Boulder position (chases from right)
        boulder_x = 300 - (S_value * 10)
        boulder_y = -150
        
        # Runner position (you)
        runner_x = -350
        runner_y = -150
        
        # Draw runner
        self.boulder.penup()
        self.boulder.goto(runner_x, runner_y)
        self.boulder.pendown()
        self.boulder.pencolor(self.colors['acid'])
        self.boulder.fillcolor(self.colors['acid'])
        self.boulder.begin_fill()
        self.boulder.circle(15)
        self.boulder.end_fill()
        
        # Draw "RUNNER" label
        self.boulder.penup()
        self.boulder.goto(runner_x, runner_y - 30)
        self.boulder.pencolor(self.colors['acid'])
        self.boulder.write("RUNNER", align="center", font=("Arial", 10, "bold"))
        
        # Draw boulder
        self.boulder.penup()
        self.boulder.goto(boulder_x, boulder_y)
        self.boulder.pendown()
        
        # Color based on danger
        if S_value > 8:
            boulder_color = self.colors['red']
        elif S_value > 5:
            boulder_color = self.colors['magenta']
        else:
            boulder_color = "#888888"
            
        self.boulder.pencolor(boulder_color)
        self.boulder.fillcolor(boulder_color)
        self.boulder.begin_fill()
        self.boulder.circle(boulder_size)
        self.boulder.end_fill()
        
        # Draw "BOULDER (S)" label
        self.boulder.penup()
        self.boulder.goto(boulder_x, boulder_y - boulder_size - 20)
        self.boulder.pencolor(boulder_color)
        self.boulder.write(f"BOULDER (S={S_value:.1f})", align="center", font=("Arial", 10, "bold"))
        
        # Draw danger zone
        danger_distance = boulder_x - runner_x
        if danger_distance < 200:
            self.boulder.penup()
            self.boulder.goto((runner_x + boulder_x)/2, -180)
            self.boulder.pencolor(self.colors['red'])
            self.boulder.write("⚠️ DANGER CLOSE ⚠️", align="center", font=("Arial", 12, "bold"))
            
    def draw_chiral_spiral(self, S_value):
        """Draw chiral spiral based on S"""
        t = turtle.Turtle()
        t.hideturtle()
        t.speed(0)
        t.penup()
        
        # Spiral parameters based on S
        turns = 3 + S_value * 0.3
        growth = 0.5 + S_value * 0.1
        
        # Position
        t.goto(300, 200)
        t.pendown()
        
        # Draw chiral spiral (sovereign)
        t.pencolor(self.colors['cyan'])
        for i in range(int(100 * turns)):
            angle = i * 0.1
            r = growth * angle
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            t.goto(300 + x, 200 + y)
            
        # Draw mirror spiral (beige baseline)
        t.penup()
        t.goto(300, 200)
        t.pendown()
        t.pencolor("#666666")
        for i in range(int(100 * turns)):
            angle = i * 0.1
            r = growth * angle
            x = r * math.cos(-angle)  # Mirrored
            y = r * math.sin(-angle)
            t.goto(300 + x, 200 + y)
            
        # Label
        t.penup()
        t.goto(300, 200 - 100)
        t.pencolor(self.colors['cyan'])
        t.write("CHIRAL SPIRAL", align="center", font=("Arial", 10, "bold"))
        
    def draw_info_panel(self):
        """Draw parameter information"""
        self.text.clear()
        
        S = sanding_equation(self.E, self.N, self.A)
        
        # Title
        self.text.goto(0, 300)
        self.text.pencolor(self.colors['yellow'])
        self.text.write("NONAGON FORGE - SANDING VISUALIZER", 
                       align="center", font=("Arial", 16, "bold"))
        
        # Equation
        self.text.goto(0, 270)
        self.text.pencolor(self.colors['cyan'])
        self.text.write(f"S = (E × N) / A  =  ({self.E} × {self.N}) / {self.A}  =  {S:.2f}", 
                       align="center", font=("Arial", 12, "bold"))
        
        # Parameter display
        self.text.goto(-400, 250)
        self.text.pencolor(self.colors['acid'])
        self.text.write(f"E (Entropy): {self.E}", font=("Arial", 10, "bold"))
        
        self.text.goto(-200, 250)
        self.text.pencolor(self.colors['magenta'])
        self.text.write(f"N (Novelty): {self.N}", font=("Arial", 10, "bold"))
        
        self.text.goto(0, 250)
        self.text.pencolor(self.colors['blue'])
        self.text.write(f"A (Shielding): {self.A}", font=("Arial", 10, "bold"))
        
        self.text.goto(200, 250)
        self.text.pencolor(self.colors['red'])
        self.text.write(f"S (Friction): {S:.2f}", font=("Arial", 10, "bold"))
        
        # Interpretation
        self.text.goto(0, 220)
        if S > 8:
            status = "⚡ CRITICAL FORGE - Boulder is ON YOU"
            color = self.colors['red']
        elif S > 4:
            status = "🔨 OPTIMAL SANDING - Active shaping"
            color = self.colors['magenta']
        elif S > 1:
            status = "⚖️ STABLE COHERENCE - Manageable"
            color = self.colors['cyan']
        else:
            status = "🌀 LAMINAR FLOW - Easy running"
            color = self.colors['acid']
            
        self.text.pencolor(color)
        self.text.write(status, align="center", font=("Arial", 12, "bold"))
        
        # Instructions
        self.text.goto(0, -300)
        self.text.pencolor("#888888")
        self.text.write("CONTROLS: E/N/A = increase, e/n/a = decrease, SPACE = randomize, Q = quit", 
                       align="center", font=("Arial", 10, "normal"))
        
    def update_display(self):
        """Update all visualizations"""
        turtle.clear()
        
        # Draw all components
        self.draw_grid()
        
        S = sanding_equation(self.E, self.N, self.A)
        self.draw_seismograph(S)
        self.draw_boulder(S)
        self.draw_chiral_spiral(S)
        self.draw_info_panel()
        
        turtle.update()
        
    def run(self):
        """Main event loop"""
        # Initial draw
        self.update_display()
        
        # Key bindings
        def increase_E():
            self.E = min(10.0, self.E + 0.5)
            self.update_display()
            
        def decrease_E():
            self.E = max(0.1, self.E - 0.5)
            self.update_display()
            
        def increase_N():
            self.N = min(10.0, self.N + 0.5)
            self.update_display()
            
        def decrease_N():
            self.N = max(0.1, self.N - 0.5)
            self.update_display()
            
        def increase_A():
            self.A = min(10.0, self.A + 0.5)
            self.update_display()
            
        def decrease_A():
            self.A = max(0.1, self.A - 0.5)
            self.update_display()
            
        def randomize():
            import random
            self.E = random.uniform(1.0, 9.0)
            self.N = random.uniform(1.0, 9.0)
            self.A = random.uniform(1.0, 5.0)
            self.update_display()
            
        # Set up key bindings
        self.screen.onkeypress(increase_E, "E")
        self.screen.onkeypress(decrease_E, "e")
        self.screen.onkeypress(increase_N, "N")
        self.screen.onkeypress(decrease_N, "n")
        self.screen.onkeypress(increase_A, "A")
        self.screen.onkeypress(decrease_A, "a")
        self.screen.onkeypress(randomize, "space")
        self.screen.onkeypress(lambda: self.screen.bye(), "q")
        
        self.screen.listen()
        self.screen.mainloop()

# ====================
# EXECUTION GUARANTEE
# ====================
def main():
    """Guaranteed execution with fallbacks"""
    print("=" * 60)
    print("NONAGON FORGE VISUALIZER - INITIALIZING")
    print("=" * 60)
    print("A window should appear shortly...")
    print("If not, trying alternative method...")
    print()
    
    try:
        # Try to run the visualizer
        viz = ForgeVisualizer()
        viz.run()
        
    except Exception as e:
        print(f"Visualizer error: {e}")
        print("\nTrying fallback text-only mode...")
        
        # Fallback: text-based visualization
        import random
        E, N, A = 5.0, 5.0, 2.0
        
        for _ in range(10):
            S = sanding_equation(E, N, A)
            
            # Text-based boulder visualization
            boulder_size = int(S * 3)
            runner_pos = 0
            boulder_pos = 50 - int(S * 4)
            
            line = [" "] * 50
            line[runner_pos] = "🏃"  # Runner
            line[min(boulder_pos, 49)] = "🪨"  # Boulder
            
            print(f"S={S:.2f}: " + "".join(line))
            
            # Adjust parameters
            E += random.uniform(-1, 1)
            N += random.uniform(-1, 1)
            A += random.uniform(-0.5, 0.5)
            E = max(0.1, min(10, E))
            N = max(0.1, min(10, N))
            A = max(0.1, min(10, A))
            
            time.sleep(0.5)

if __name__ == "__main__":
    main()