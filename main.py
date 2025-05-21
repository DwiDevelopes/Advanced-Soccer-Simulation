import tkinter as tk
import random
import math
from tkinter import messagebox
import time

class SoccerPlayer:
    def __init__(self, canvas, x, y, team, player_id, position):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.team = team  # 'home' or 'away'
        self.player_id = player_id
        self.position = position  # 'GK', 'DEF', 'MID', 'FWD'
        self.selected = False
        self.radius = 15
        self.speed = self.calculate_speed()
        self.target_x = x
        self.target_y = y
        self.has_ball = False
        self.stamina = 100
        self.skill = random.uniform(0.7, 1.0)
        self.state = "idle"  # 'idle', 'chasing', 'attacking', 'defending', 'celebrating'
        self.celebrate_timer = 0
        
        # Player attributes
        if team == 'home':
            self.color = '#1a3e8c'  # Dark blue
            self.text_color = 'white'
        else:
            self.color = '#8c1a1a'  # Dark red
            self.text_color = 'white'
        
        self.id = canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill=self.color, outline='black', width=2
        )
        self.text_id = canvas.create_text(
            x, y, text=str(player_id),
            fill=self.text_color, font=('Arial', 10, 'bold')
        )
        
        # Add position indicator
        pos_colors = {'GK': 'yellow', 'DEF': 'green', 'MID': 'blue', 'FWD': 'red'}
        self.pos_indicator = canvas.create_oval(
            x - 5, y - self.radius - 10,
            x + 5, y - self.radius,
            fill=pos_colors.get(position, 'white'), outline='black'
        )
    
    def calculate_speed(self):
        # Different speeds based on position
        base_speed = 2.0
        if self.position == 'GK':
            return base_speed * 0.9
        elif self.position == 'DEF':
            return base_speed * 1.0
        elif self.position == 'MID':
            return base_speed * 1.2
        elif self.position == 'FWD':
            return base_speed * 1.3
        return base_speed
    
    def move_towards_target(self):
        if self.state == "celebrating":
            self.celebrate_timer -= 1
            if self.celebrate_timer <= 0:
                self.state = "idle"
            return
            
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 2:
            # Apply fatigue
            fatigue_factor = 1 - (0.5 * (1 - self.stamina/100))
            actual_speed = self.speed * fatigue_factor * (0.8 + 0.4 * self.skill)
            
            self.x += dx / distance * actual_speed
            self.y += dy / distance * actual_speed
            
            # Update stamina
            self.stamina = max(30, self.stamina - 0.05)
            
            self.update_canvas_position()
    
    def update_canvas_position(self):
        self.canvas.coords(self.id, 
                          self.x - self.radius, 
                          self.y - self.radius,
                          self.x + self.radius, 
                          self.y + self.radius)
        self.canvas.coords(self.text_id, self.x, self.y)
        self.canvas.coords(self.pos_indicator,
                          self.x - 5, self.y - self.radius - 10,
                          self.x + 5, self.y - self.radius)
    
    def set_target(self, x, y, state="moving"):
        self.target_x = x
        self.target_y = y
        self.state = state
    
    def is_clicked(self, event_x, event_y):
        distance = math.sqrt((event_x - self.x)**2 + (event_y - self.y)**2)
        return distance <= self.radius
    
    def select(self):
        self.selected = True
        self.canvas.itemconfig(self.id, outline='yellow', width=3)
    
    def deselect(self):
        self.selected = False
        self.canvas.itemconfig(self.id, outline='black', width=2)
    
    def celebrate(self, duration=50):
        self.state = "celebrating"
        self.celebrate_timer = duration
        # Make player jump up and down
        self.canvas.itemconfig(self.id, outline='gold', width=4)
    
    def recover_stamina(self):
        if self.state != "celebrating":
            self.stamina = min(100, self.stamina + 0.1)

class Ball:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = 10
        self.speed_x = 0
        self.speed_y = 0
        self.owner = None
        self.last_owner = None
        self.id = canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill='white', outline='black'
        )
        self.trail = []
        self.max_trail = 5
    
    def move(self):
        if self.owner:
            # Ball follows owner
            self.x = self.owner.x
            self.y = self.owner.y
            self.speed_x = 0
            self.speed_y = 0
        else:
            # Ball moves freely
            self.x += self.speed_x
            self.y += self.speed_y
            
            # Bounce off walls with more realistic physics
            if self.x - self.radius <= 0:
                self.x = self.radius
                self.speed_x *= -0.7
            elif self.x + self.radius >= 800:
                self.x = 800 - self.radius
                self.speed_x *= -0.7
                
            if self.y - self.radius <= 0:
                self.y = self.radius
                self.speed_y *= -0.7
            elif self.y + self.radius >= 500:
                self.y = 500 - self.radius
                self.speed_y *= -0.7
            
            # Apply more realistic friction
            self.speed_x *= 0.96
            self.speed_y *= 0.96
            
            # Stop if very slow
            if abs(self.speed_x) < 0.1 and abs(self.speed_y) < 0.1:
                self.speed_x = 0
                self.speed_y = 0
        
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
        
        self.update_canvas_position()
    
    def update_canvas_position(self):
        self.canvas.coords(self.id, 
                          self.x - self.radius, 
                          self.y - self.radius,
                          self.x + self.radius, 
                          self.y + self.radius)
    
    def kick(self, power_x, power_y, accuracy=1.0):
        # Add some randomness based on accuracy
        self.speed_x = power_x * (0.9 + 0.2 * accuracy * random.random())
        self.speed_y = power_y * (0.9 + 0.2 * accuracy * random.random())
        self.owner = None
    
    def pass_ball(self, target_x, target_y, power=3.0, accuracy=1.0):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        
        # Normalize and apply power
        power_x = dx / distance * power
        power_y = dy / distance * power
        
        # Add some randomness based on accuracy
        power_x *= (0.8 + 0.4 * accuracy * random.random())
        power_y *= (0.8 + 0.4 * accuracy * random.random())
        
        self.kick(power_x, power_y, accuracy)
    
    def shoot(self, target_x, target_y, power=5.0, accuracy=0.8):
        self.pass_ball(target_x, target_y, power, accuracy)
    
    def set_owner(self, player):
        if self.owner:
            self.owner.has_ball = False
        self.owner = player
        if player:
            player.has_ball = True
            self.last_owner = player

class SoccerGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Soccer Simulation")
        
        # Game state
        self.home_score = 0
        self.away_score = 0
        self.game_active = False
        self.match_time = 0  # In seconds
        self.half_length = 45 * 60  # 45 minutes per half
        self.current_half = 1
        self.selected_player = None
        self.drag_start = None
        self.last_update_time = time.time()
        self.possession_time = {'home': 0, 'away': 0, 'none': 0}
        self.last_possession = 'none'
        self.shots = {'home': 0, 'away': 0}
        self.shots_on_target = {'home': 0, 'away': 0}
        self.custom_formation_mode = False
        self.home_formation = '4-4-2'
        self.away_formation = '4-4-2'
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=800, height=500, bg='#2e8b57')  # Forest green
        self.canvas.pack()
        
        # Draw field markings
        self.draw_field()
        
        # Create control panel
        self.control_panel = tk.Frame(root)
        self.control_panel.pack(fill=tk.X)
        
        # Score and time display
        self.score_display = tk.Label(self.control_panel, text="Home: 0 - Away: 0", 
                                     font=('Arial', 14, 'bold'))
        self.score_display.pack(side=tk.LEFT, padx=10)
        
        self.time_display = tk.Label(self.control_panel, text="00:00 - 1st Half", 
                                   font=('Arial', 14))
        self.time_display.pack(side=tk.LEFT, padx=10)
        
        # Match controls
        self.match_controls = tk.Frame(self.control_panel)
        self.match_controls.pack(side=tk.RIGHT, padx=10)
        
        self.start_button = tk.Button(self.match_controls, text="Start Match", 
                                    command=self.start_match)
        self.start_button.pack(side=tk.LEFT)
        
        self.pause_button = tk.Button(self.match_controls, text="Pause", 
                                    command=self.pause_match, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT)
        
        # Stats display
        self.stats_display = tk.Label(root, text="Possession: H 0% - A 0% | Shots: H 0(0) - A 0(0)", 
                                    font=('Arial', 12))
        self.stats_display.pack()
        
        # Formation controls
        self.formation_frame = tk.Frame(root)
        self.formation_frame.pack()
        
        tk.Label(self.formation_frame, text="Home Formation:").pack(side=tk.LEFT)
        self.home_formation_var = tk.StringVar(value='4-4-2')
        formations = ['4-4-2', '4-3-3', '3-5-2', '4-2-3-1', '5-3-2']
        tk.OptionMenu(self.formation_frame, self.home_formation_var, *formations, 
                     command=self.set_home_formation).pack(side=tk.LEFT)
        
        tk.Label(self.formation_frame, text="Away Formation:").pack(side=tk.LEFT, padx=(10,0))
        self.away_formation_var = tk.StringVar(value='4-4-2')
        tk.OptionMenu(self.formation_frame, self.away_formation_var, *formations, 
                     command=self.set_away_formation).pack(side=tk.LEFT)
        
        self.custom_formation_btn = tk.Button(self.formation_frame, text="Custom Formation", 
                                            command=self.enable_custom_formation)
        self.custom_formation_btn.pack(side=tk.LEFT, padx=10)
        
        # Initialize players and ball
        self.home_players = []
        self.away_players = []
        self.ball = Ball(self.canvas, 400, 250)
        
        # Set initial formation
        self.set_home_formation('4-4-2')
        self.set_away_formation('4-4-2')
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Start game loop
        self.game_loop()
    
    def draw_field(self):
        # Field outline
        self.canvas.create_rectangle(50, 50, 750, 450, outline='white', width=2)
        
        # Center line and circle
        self.canvas.create_line(400, 50, 400, 450, fill='white', width=2)
        self.canvas.create_oval(350, 200, 450, 300, outline='white', width=2)
        self.canvas.create_oval(395, 245, 405, 255, fill='white', outline='white')  # Center spot
        
        # Goals
        self.canvas.create_rectangle(50, 200, 30, 300, fill='white', outline='white')
        self.canvas.create_rectangle(750, 200, 770, 300, fill='white', outline='white')
        
        # Penalty areas
        self.canvas.create_rectangle(50, 150, 150, 350, outline='white', width=2)
        self.canvas.create_rectangle(750, 150, 650, 350, outline='white', width=2)
        
        # Goal areas
        self.canvas.create_rectangle(50, 225, 90, 275, outline='white', width=2)
        self.canvas.create_rectangle(750, 225, 710, 275, outline='white', width=2)
        
        # Penalty spots
        self.canvas.create_oval(115, 245, 125, 255, fill='white', outline='white')
        self.canvas.create_oval(685, 245, 675, 255, fill='white', outline='white')
        
        # Corner arcs
        self.canvas.create_arc(30, 30, 90, 90, start=0, extent=90, outline='white', style='arc')
        self.canvas.create_arc(710, 30, 770, 90, start=90, extent=90, outline='white', style='arc')
        self.canvas.create_arc(30, 410, 90, 470, start=270, extent=90, outline='white', style='arc')
        self.canvas.create_arc(710, 410, 770, 470, start=180, extent=90, outline='white', style='arc')
    
    def set_home_formation(self, formation):
        if self.game_active and not self.custom_formation_mode:
            return
            
        self.home_formation = formation
        self.create_players('home', formation)
    
    def set_away_formation(self, formation):
        if self.game_active and not self.custom_formation_mode:
            return
            
        self.away_formation = formation
        self.create_players('away', formation)
    
    def create_players(self, team, formation):
        if team == 'home':
            players = self.home_players
            x_mult = 1
            start_x = 100
        else:
            players = self.away_players
            x_mult = -1
            start_x = 700
        
        # Clear existing players
        for player in players:
            self.canvas.delete(player.id)
            self.canvas.delete(player.text_id)
            self.canvas.delete(player.pos_indicator)
        
        players.clear()
        
        # Goalkeeper
        players.append(SoccerPlayer(self.canvas, start_x, 250, team, 1, 'GK'))
        
        if formation == '4-4-2':
            # Defenders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 150, team, 2, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 200, team, 3, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 300, team, 4, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 350, team, 5, 'DEF'))
            
            # Midfielders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*200, 150, team, 6, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*200, 225, team, 7, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*200, 275, team, 8, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*200, 350, team, 9, 'MID'))
            
            # Forwards
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*300, 225, team, 10, 'FWD'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*300, 275, team, 11, 'FWD'))
        
        elif formation == '4-3-3':
            # Defenders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 150, team, 2, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 225, team, 3, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 275, team, 4, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 350, team, 5, 'DEF'))
            
            # Midfielders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*200, 200, team, 6, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*200, 250, team, 7, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*200, 300, team, 8, 'MID'))
            
            # Forwards
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*300, 175, team, 9, 'FWD'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*300, 250, team, 10, 'FWD'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*300, 325, team, 11, 'FWD'))
        
        elif formation == '3-5-2':
            # Defenders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 200, team, 2, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 250, team, 3, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 300, team, 4, 'DEF'))
            
            # Midfielders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*180, 125, team, 5, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*180, 200, team, 6, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*180, 250, team, 7, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*180, 300, team, 8, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*180, 375, team, 9, 'MID'))
            
            # Forwards
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*280, 225, team, 10, 'FWD'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*280, 275, team, 11, 'FWD'))
        
        elif formation == '4-2-3-1':
            # Defenders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 150, team, 2, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 225, team, 3, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 275, team, 4, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 350, team, 5, 'DEF'))
            
            # Defensive Midfielders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*180, 225, team, 6, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*180, 275, team, 7, 'MID'))
            
            # Attacking Midfielders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*250, 200, team, 8, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*250, 250, team, 9, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*250, 300, team, 10, 'MID'))
            
            # Forward
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*320, 250, team, 11, 'FWD'))
        
        elif formation == '5-3-2':
            # Defenders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*80, 150, team, 2, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 200, team, 3, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 250, team, 4, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*100, 300, team, 5, 'DEF'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*80, 350, team, 6, 'DEF'))
            
            # Midfielders
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*200, 225, team, 7, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*200, 250, team, 8, 'MID'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*200, 275, team, 9, 'MID'))
            
            # Forwards
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*300, 225, team, 10, 'FWD'))
            players.append(SoccerPlayer(self.canvas, start_x + x_mult*300, 275, team, 11, 'FWD'))
    
    def enable_custom_formation(self):
        if self.game_active:
            messagebox.showwarning("Match Active", "Cannot change formation during active match!")
            return
            
        self.custom_formation_mode = not self.custom_formation_mode
        if self.custom_formation_mode:
            self.custom_formation_btn.config(bg='yellow')
            messagebox.showinfo("Custom Formation", "Drag players to set custom formation")
        else:
            self.custom_formation_btn.config(bg='SystemButtonFace')
            # Reset to saved formation
            self.set_home_formation(self.home_formation)
            self.set_away_formation(self.away_formation)
    
    def on_canvas_click(self, event):
        if not self.custom_formation_mode:
            return
            
        # Check if a player was clicked
        for player in self.home_players + self.away_players:
            if player.is_clicked(event.x, event.y):
                if self.selected_player:
                    self.selected_player.deselect()
                player.select()
                self.selected_player = player
                self.drag_start = (event.x, event.y)
                return
        
        # If no player was clicked, deselect
        if self.selected_player:
            self.selected_player.deselect()
            self.selected_player = None
    
    def on_canvas_drag(self, event):
        if not self.custom_formation_mode or not self.selected_player:
            return
            
        # Move the selected player
        dx = event.x - self.drag_start[0]
        dy = event.y - self.drag_start[1]
        
        self.selected_player.x += dx
        self.selected_player.y += dy
        self.selected_player.target_x = self.selected_player.x
        self.selected_player.target_y = self.selected_player.y
        
        self.selected_player.update_canvas_position()
        self.drag_start = (event.x, event.y)
    
    def on_canvas_release(self, event):
        if not self.custom_formation_mode or not self.selected_player:
            return
            
        self.selected_player.deselect()
        self.selected_player = None
    
    def start_match(self):
        self.game_active = True
        self.match_time = 0
        self.current_half = 1
        self.home_score = 0
        self.away_score = 0
        self.possession_time = {'home': 0, 'away': 0, 'none': 0}
        self.last_possession = 'none'
        self.shots = {'home': 0, 'away': 0}
        self.shots_on_target = {'home': 0, 'away': 0}
        
        self.update_score()
        self.update_stats()
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.custom_formation_btn.config(state=tk.DISABLED)
        
        # Reset ball to center
        self.reset_ball()
        
        # Reset player positions
        self.set_home_formation(self.home_formation)
        self.set_away_formation(self.away_formation)
    
    def pause_match(self):
        self.game_active = not self.game_active
        if self.game_active:
            self.pause_button.config(text="Pause")
            self.last_update_time = time.time()  # Reset timer to avoid big time jumps
        else:
            self.pause_button.config(text="Resume")
            self.start_button.config(state=tk.NORMAL)
    
    def reset_ball(self):
        self.ball.x = 400
        self.ball.y = 250
        self.ball.speed_x = 0
        self.ball.speed_y = 0
        self.ball.set_owner(None)
        self.ball.update_canvas_position()
    
    def game_loop(self):
        current_time = time.time()
        time_elapsed = current_time - self.last_update_time
        self.last_update_time = current_time
        
        if self.game_active:
            # Update match time
            self.match_time += time_elapsed
            self.update_time_display()
            
            # Update possession stats
            self.update_possession_stats(time_elapsed)
            
            # Move players and ball
            self.update_players()
            self.update_ball()
            
            # Check for goals
            self.check_for_goals()
            
            # AI decision making
            self.ai_decision_making()
        
        # Schedule next frame
        self.root.after(30, self.game_loop)
    
    def update_time_display(self):
        minutes = int(self.match_time // 60)
        seconds = int(self.match_time % 60)
        
        if self.match_time > self.half_length and self.current_half == 1:
            half = "HT"
        elif self.match_time > 2 * self.half_length:
            half = "FT"
            self.game_active = False
            self.pause_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)
            self.custom_formation_btn.config(state=tk.NORMAL)
        else:
            if self.match_time > self.half_length:
                half = "2nd Half"
                if self.current_half == 1:
                    self.current_half = 2
                    # Reset positions for second half
                    self.reset_ball()
                    for team in [self.home_players, self.away_players]:
                        for player in team:
                            player.x = 800 - player.x  # Switch sides
                            player.y = 500 - player.y
                            player.target_x = player.x
                            player.target_y = player.y
                            player.update_canvas_position()
            else:
                half = "1st Half"
        
        time_text = f"{minutes:02d}:{seconds:02d} - {half}"
        self.time_display.config(text=time_text)
    
    def update_possession_stats(self, time_elapsed):
        if self.ball.owner:
            team = self.ball.owner.team
            self.possession_time[team] += time_elapsed
            self.last_possession = team
        else:
            self.possession_time['none'] += time_elapsed
            self.last_possession = 'none'
        
        # Update stats display periodically
        if random.random() < 0.05:  # Update ~5% of the time to reduce CPU usage
            self.update_stats()
    
    def update_stats(self):
        total_time = max(1, sum(self.possession_time.values()))
        home_poss = int(self.possession_time['home'] / total_time * 100)
        away_poss = int(self.possession_time['away'] / total_time * 100)
        
        stats_text = (f"Possession: H {home_poss}% - A {away_poss}% | "
                     f"Shots: H {self.shots['home']}({self.shots_on_target['home']}) - "
                     f"A {self.shots['away']}({self.shots_on_target['away']})")
        self.stats_display.config(text=stats_text)
    
    def update_players(self):
        for player in self.home_players + self.away_players:
            player.move_towards_target()
            player.recover_stamina()
    
    def update_ball(self):
        self.ball.move()
        
        # Check for player-ball collisions
        for player in self.home_players + self.away_players:
            if player.state == "celebrating":
                continue
                
            distance = math.sqrt((player.x - self.ball.x)**2 + (player.y - self.ball.y)**2)
            if distance < player.radius + self.ball.radius:
                self.handle_collision(player)
    
    def handle_collision(self, player):
        if self.ball.owner == player:
            return
            
        # Calculate interception chance based on player skill and position
        interception_chance = 0.5 * player.skill
        if player.position == 'DEF':
            interception_chance += 0.2
        if player.team != self.last_possession:  # Tackling chance
            interception_chance += 0.1
        
        if random.random() < interception_chance:
            # Player gains control of the ball
            self.ball.set_owner(player)
            
            # If this was a tackle, make the previous owner stumble
            if self.ball.last_owner and self.ball.last_owner.team != player.team:
                self.ball.last_owner.set_target(
                    self.ball.last_owner.x + random.uniform(-20, 20),
                    self.ball.last_owner.y + random.uniform(-20, 20),
                    "stumbling"
                )
    
    def ai_decision_making(self):
        if not self.game_active or random.random() > 0.05:  # Only run AI occasionally
            return
            
        # AI for players with ball
        for player in self.home_players + self.away_players:
            if player.has_ball:
                self.ai_with_ball(player)
            else:
                self.ai_without_ball(player)
    
    def ai_with_ball(self, player):
        # Decide whether to pass, shoot, or dribble
        decision = random.random()
        
        # Get teammates and opponents
        teammates = [p for p in (self.home_players if player.team == 'home' else self.away_players) 
                    if p != player]
        opponents = self.away_players if player.team == 'home' else self.home_players
        
        # Calculate distance to opponent goal
        goal_x = 750 if player.team == 'home' else 50
        goal_y = 250
        distance_to_goal = math.sqrt((player.x - goal_x)**2 + (player.y - goal_y)**2)
        
        # Shoot if close enough and has a clear shot
        if distance_to_goal < 200 and random.random() < 0.3:
            self.shoot_ball(player)
            return
        
        # Look for passing options
        best_pass = None
        best_pass_score = 0
        
        for teammate in teammates:
            # Check if teammate is in a good position (ahead of player)
            if ((player.team == 'home' and teammate.x > player.x) or 
                (player.team == 'away' and teammate.x < player.x)):
                
                # Check if path is relatively clear
                opponents_in_path = sum(1 for opp in opponents 
                                      if self.distance_to_line(player.x, player.y, 
                                                             teammate.x, teammate.y, 
                                                             opp.x, opp.y) < 50)
                
                pass_score = (teammate.skill * 0.5 + 
                             (1 - opponents_in_path / 3) * 0.5)
                
                if pass_score > best_pass_score:
                    best_pass = teammate
                    best_pass_score = pass_score
        
        # Make pass if good option found
        if best_pass and best_pass_score > 0.5 and random.random() < 0.7:
            self.pass_ball(player, best_pass)
            return
        
        # Otherwise dribble forward
        target_x = player.x + (50 if player.team == 'home' else -50)
        target_y = player.y + random.uniform(-30, 30)
        
        # Ensure we stay on field
        target_x = max(50, min(750, target_x))
        target_y = max(50, min(450, target_y))
        
        player.set_target(target_x, target_y, "dribbling")
    
    def ai_without_ball(self, player):
        # Basic positioning logic based on player position
        if player.position == 'GK':
            # Goalkeeper stays near goal
            target_x = 100 if player.team == 'home' else 700
            target_y = 250
            
            # If ball is near, move toward it
            if ((player.team == 'home' and self.ball.x < 250) or 
                (player.team == 'away' and self.ball.x > 550)):
                target_y = self.ball.y
            
        elif player.position == 'DEF':
            # Defenders stay back but move toward ball
            base_x = 200 if player.team == 'home' else 600
            target_x = base_x + (self.ball.x - 400) * 0.2 * (1 if player.team == 'home' else -1)
            target_y = self.ball.y * 0.7 + player.y * 0.3
            
        elif player.position == 'MID':
            # Midfielders follow ball but maintain shape
            base_x = 300 if player.team == 'home' else 500
            target_x = base_x + (self.ball.x - 400) * 0.3 * (1 if player.team == 'home' else -1)
            target_y = self.ball.y * 0.5 + player.y * 0.5
            
        else:  # FWD
            # Forwards look for attacking positions
            base_x = 400 if player.team == 'home' else 400
            target_x = base_x + (self.ball.x - 400) * 0.4 * (1 if player.team == 'home' else -1)
            
            # Make runs into space
            if random.random() < 0.1:
                target_y = player.y + random.uniform(-50, 50)
            else:
                target_y = self.ball.y * 0.3 + player.y * 0.7
        
        # Adjust for formation shape
        formation_factor = 0.7  # How much to stick to formation position
        target_x = target_x * (1 - formation_factor) + player.target_x * formation_factor
        target_y = target_y * (1 - formation_factor) + player.target_y * formation_factor
        
        # Ensure we stay on field
        target_x = max(50, min(750, target_x))
        target_y = max(50, min(450, target_y))
        
        # If ball is very close, chase it
        ball_distance = math.sqrt((player.x - self.ball.x)**2 + (player.y - self.ball.y)**2)
        if ball_distance < 100 and not self.ball.owner:
            target_x = self.ball.x
            target_y = self.ball.y
        
        player.set_target(target_x, target_y)
    
    def distance_to_line(self, x1, y1, x2, y2, px, py):
        # Calculate distance from point (px,py) to line segment (x1,y1)-(x2,y2)
        line_len = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if line_len == 0:
            return math.sqrt((px-x1)**2 + (py-y1)**2)
        
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_len ** 2)))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        return math.sqrt((px - proj_x)**2 + (py - proj_y)**2)
    
    def shoot_ball(self, player):
        if not player.has_ball:
            return
            
        self.shots[player.team] += 1
        
        # Determine target - either corners or center of goal
        goal_x = 750 if player.team == 'home' else 50
        if random.random() < 0.7:  # 70% chance to aim for corners
            goal_y = 220 if random.random() < 0.5 else 280
        else:
            goal_y = 250
        
        # Calculate shot accuracy based on distance, angle, and player skill
        dx = goal_x - player.x
        dy = goal_y - player.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        angle = abs(math.atan2(dy, dx))
        if player.team == 'away':
            angle = math.pi - angle
        
        # Accuracy factors
        distance_factor = min(1, 200 / max(50, distance))  # Better when closer
        angle_factor = 1 - (angle / (math.pi/2))  # Better when straight on
        skill_factor = player.skill
        
        accuracy = 0.5 * distance_factor + 0.3 * skill_factor + 0.2 * angle_factor
        
        # Add some randomness
        accuracy *= random.uniform(0.8, 1.2)
        accuracy = max(0.1, min(0.9, accuracy))
        
        # Determine shot power
        power = 5 + 3 * player.skill * random.uniform(0.8, 1.2)
        
        # Apply shot
        self.ball.shoot(goal_x + random.uniform(-20, 20), 
                       goal_y + random.uniform(-20, 20), 
                       power, accuracy)
        
        # Count as shot on target if accurate enough
        if accuracy > 0.5:
            self.shots_on_target[player.team] += 1
        
        # Player follows through
        player.set_target(
            player.x + dx/distance * 20,
            player.y + dy/distance * 20,
            "shooting"
        )
    
    def pass_ball(self, passer, receiver):
        if not passer.has_ball:
            return
            
        # Calculate pass power based on distance
        dx = receiver.x - passer.x
        dy = receiver.y - passer.y
        distance = math.sqrt(dx*dx + dy*dy)
        power = min(6, distance / 15)
        
        # Pass accuracy based on player skill and pressure
        accuracy = 0.7 * passer.skill
        opponents_near = sum(1 for opp in (self.away_players if passer.team == 'home' else self.home_players)
                           if math.sqrt((opp.x - passer.x)**2 + (opp.y - passer.y)**2) < 50)
        accuracy *= max(0.5, 1 - opponents_near * 0.1)
        
        # Add some randomness
        accuracy *= random.uniform(0.9, 1.1)
        accuracy = max(0.3, min(0.9, accuracy))
        
        # Make the pass
        self.ball.pass_ball(receiver.x, receiver.y, power, accuracy)
        
        # Receiver moves to meet the ball
        receiver.set_target(
            receiver.x + dx/distance * 30,
            receiver.y + dy/distance * 30,
            "receiving"
        )
    
    def check_for_goals(self):
        # Check for home goal (right side)
        if (self.ball.x + self.ball.radius >= 750 and 
            200 <= self.ball.y <= 300 and 
            not self.ball.owner):
            self.away_score += 1
            self.update_score()
            self.handle_goal('away')
        
        # Check for away goal (left side)
        elif (self.ball.x - self.ball.radius <= 50 and 
              200 <= self.ball.y <= 300 and 
              not self.ball.owner):
            self.home_score += 1
            self.update_score()
            self.handle_goal('home')
    
    def handle_goal(self, scoring_team):
        # Reset ball
        self.reset_ball()
        
        # Celebrate with random players from scoring team
        scorers = self.home_players if scoring_team == 'home' else self.away_players
        for player in random.sample(scorers, min(5, len(scorers))):
            player.celebrate()
        
        # Reset player positions after delay
        self.root.after(2000, self.reset_positions_after_goal)
    
    def reset_positions_after_goal(self):
        # Reset to formation positions
        self.set_home_formation(self.home_formation)
        self.set_away_formation(self.away_formation)
        
        # Reset ball to center
        self.reset_ball()
    
    def update_score(self):
        self.score_display.config(text=f"Home: {self.home_score} - Away: {self.away_score}")

if __name__ == "__main__":
    root = tk.Tk()
    game = SoccerGame(root)
    root.mainloop()