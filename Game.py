from __future__ import division
import sys
from PredPreyEngine import PredPreyEngine
from Pred import Pred
from Prey import Prey
from time import sleep
try:
    # for Python2
    import Tkinter as tk
    import tkFont as tkfont
except ImportError:
    # for Python3
    import tkinter as tk
    import tkinter.font as tkfont

class KeyboardHandler(object):
    def __init__(self):
        self.right = False
        self.down = False
        self.left = False
        self.up = False
        self.fire = False
        self.jump = False
        self.quadspeed = False
        self.restart = False
        self.playpause = False
        self.humanup = False
        self.humandown = False

    def keyPressed(self,event):
        if event.keysym == 'Down':
            self.down = True
        elif event.keysym == 'Right':
            self.right = True
        elif event.keysym == 'Left':
            self.left = True
        elif event.keysym == 'Up':
            self.up = True
        elif event.keysym.upper() == 'A':
            self.fire = True
        elif event.keysym.upper() == 'S':
            self.jump = True
        elif event.keysym.upper() == 'Q':
            self.quadspeed = True
        elif event.keysym.upper() == 'W':
            self.restart = True
        elif event.keysym.upper() == 'Z':
            self.playpause = True
        elif event.keysym.upper() == 'M':
            self.humanup = True
        elif event.keysym.upper() == 'N':
            self.humandown = True

    def keyReleased(self,event):
        if event.keysym == 'Down':
            self.down = False
        elif event.keysym == 'Right':
            self.right = False
        elif event.keysym == 'Left':
            self.left = False
        elif event.keysym == 'Up':
            self.up = False
        elif event.keysym.upper() == 'A':
            self.fire = False
        elif event.keysym.upper() == 'S':
            self.jump = False
        elif event.keysym.upper() == 'Q':
            self.quadspeed = False
        elif event.keysym.upper() == 'M':
            self.humanup = False
        elif event.keysym.upper() == 'N':
            self.humandown = False

class PredPreyGUI:
    def __init__(self, engine):
        # Setup variables
        self.human_player = -1
        self.playing_real_time = False
        self.projectile_list = []
        self.objects = []
        self.gui_objects = {}
        self.gfx_dict = {}
        self.gui_players = []
        self.gui_status = []
        self.sim_running = False
        self.pp_engine = engine

        # Frame and animation variables
        self.frame_length = 16
        self.frames_until_update = 8
        self.frame = self.frames_until_update

        # Prepare the window
        self.init_gui()

        # Load graphics
        self.load_gfx()

        # Setup background
        self.setup_game_window()

        # Enable keyboard support
        self.kbd_handler = KeyboardHandler()
        self.gui_canvas.bind_all('<Key>', self.kbd_handler.keyPressed)
        self.gui_canvas.bind_all('<KeyRelease>', self.kbd_handler.keyReleased)

    # Load all graphics files
    def load_gfx(self):
        gfx_static = ['Grass', 'GrassDark', 'Brick', 'Water', 'Stone', 'Snow', 'Projectile']
        gfx_players = ['PredHeadTransparent', 'PreyTransparent']

        for item in gfx_static:
            self.gfx_dict[item] = tk.PhotoImage(file=('./gfx/'+item+'.gif'))

        for item in gfx_players:
            for direction in ['Up', 'Down', 'Left', 'Right']:
                self.gfx_dict[item + direction] = tk.PhotoImage(file=('./gfx/'+item+direction+'.gif'))

    def set_human_player(self):
        for player in self.pp_engine.players:
            player.human = False
        self.pp_engine.players[self.human_player].human = True

    def init_gui(self):
        # Init game window
        self.tkinter_instance = tk.Tk()
        self.tkinter_instance.resizable(width=False, height=False)
        self.tkinter_instance.geometry('{}x{}'.format(self.pp_engine.squaresize * self.pp_engine.world_width, self.pp_engine.squaresize * self.pp_engine.world_height + 21 * (len(self.pp_engine.players) + 1)))
        self.gui_canvas = tk.Canvas(self.tkinter_instance)
        self.gui_canvas.pack(fill=tk.BOTH, expand=1)

        # GUI information
        self.font_top = tkfont.Font(weight='bold', size=10)
        self.font_info = tkfont.Font(size=10)
        temp = tk.Label(self.tkinter_instance, text="PredPrey version ?.???   time=0", font=self.font_top, background='white')
        temp.pack(fill=tk.X)
        self.gui_status.append(temp)
        for each in self.pp_engine.players:
            temp = tk.Label(self.tkinter_instance, text=each, font=self.font_info, background='white')
            temp.pack(fill=tk.X)
            self.gui_status.append(temp)

    # Create background and players
    def setup_game_window(self):
        # Draw background tiles
        for y in range(0, self.pp_engine.world_height):
            for x in range(0, self.pp_engine.world_width):
                tile = self.pp_engine.world[y * self.pp_engine.world_width + x]
                self.gui_canvas.create_image(x * self.pp_engine.squaresize + 10, y * self.pp_engine.squaresize + 10, image=self.gfx_dict[tile])

        # Create players
        self.gui_players = []
        for player in self.pp_engine.players:
            temp = self.gui_canvas.create_image(self.pp_engine.squaresize * player.x + 10, self.pp_engine.squaresize * player.y + 10, image=self.gfx_dict[player.gfx + 'Left'])
            self.gui_players.append(temp)

    def run_simulation(self):
        self.sim_running = True
        self.tkinter_instance.after(1000, self.render_frame)
        self.tkinter_instance.mainloop()

    def get_human_action(self):
        human_action = []

        if self.kbd_handler.fire:
            human_action.append("FIRE")
        elif self.kbd_handler.jump:
            human_action.append("JUMP")
        else:
            human_action.append("MOVE")

        if self.kbd_handler.right:
            human_action.append("RIGHT")
        elif self.kbd_handler.left:
            human_action.append("LEFT")
        elif self.kbd_handler.up:
            human_action.append("UP")
        elif self.kbd_handler.down:
            human_action.append("DOWN")

        if len(human_action) < 2:
            human_action = None

        return human_action

    # Update GUI information
    def update_gui(self):
        for i in range(0, len(self.pp_engine.players)):
            player = self.pp_engine.players[i]
            label = self.gui_status[i+1]

            label['text'] = 'Player %d (%s) at (%d,%d)' % (i, player.type, player.x, player.y)
            if self.current_update:
                label['text'] += ' doing %s' % self.current_update[i]

            if not player.alive:
                label['background'] = 'red'
            elif player.human:
                label['background'] = 'yellow'
            else:
                label['background'] = 'white'

        self.gui_status[0]['text'] = "PredPrey version ?.???   time=%d" % self.pp_engine.time

    def update_characters(self, update):
        animation_factor = 1.0/self.frames_until_update

        if update:
            for i in range(0, len(self.pp_engine.players)):
                # Applicable action and gui element
                action = update[i]
                gui_element = self.gui_players[i]
                player = self.pp_engine.players[i]

                # Update the characters
                if action:
                    if action[0] == 'MOVE' or action[0] == 'JUMP':
                        direction = player.direction[0] + player.direction[1:].lower()
                        self.gui_canvas.itemconfig(gui_element, image=self.gfx_dict[player.gfx + direction])

                        if action[1] == 'UP':
                            self.gui_canvas.move(gui_element, 0, -action[2] * self.pp_engine.squaresize * animation_factor)

                        elif action[1] == 'DOWN':
                            self.gui_canvas.move(gui_element, 0, action[2] * self.pp_engine.squaresize * animation_factor)

                        elif action[1] == 'LEFT':
                            self.gui_canvas.move(gui_element, -action[2] * self.pp_engine.squaresize * animation_factor, 0)

                        elif action[1] == 'RIGHT':
                            self.gui_canvas.move(gui_element, action[2] * self.pp_engine.squaresize * animation_factor, 0)

    def update_objects(self):
        if self.frame == 0:
            current_objects = self.pp_engine.objects

            # Remove objects
            for object_id in self.pp_engine.objects_removed:
                self.gui_canvas.delete(self.gui_objects[object_id])

            # Create new objects
            for object_id in self.pp_engine.objects_created:
                for object in current_objects:
                    if object.id == object_id:
                        temp = self.gui_canvas.create_image(object.x * self.pp_engine.squaresize + self.pp_engine.squaresize // 2, object.y * self.pp_engine.squaresize + self.pp_engine.squaresize // 2, image=self.gfx_dict[object.gfx])
                        self.gui_objects[object.id] = temp


            # Save object list
            self.objects = current_objects

        # Move objects that already exist
        for object in self.objects:
            action = object.action
            animation_factor = 1.0/self.frames_until_update
            gui_element = self.gui_objects[object.id]

            if action:
                if action[0] == 'MOVE':
                    if action[1] == 'UP':
                        self.gui_canvas.move(gui_element, 0, -action[2] * self.pp_engine.squaresize * animation_factor)

                    elif action[1] == 'DOWN':
                        self.gui_canvas.move(gui_element, 0, action[2] * self.pp_engine.squaresize * animation_factor)

                    elif action[1] == 'LEFT':
                        self.gui_canvas.move(gui_element, -action[2] * self.pp_engine.squaresize * animation_factor, 0)

                    elif action[1] == 'RIGHT':
                        self.gui_canvas.move(gui_element, action[2] * self.pp_engine.squaresize * animation_factor, 0)


    def render_frame(self):
        if self.kbd_handler.humanup:
            self.kbd_handler.humanup = False
            self.human_player += 1
            if self.human_player >= len(self.pp_engine.players):
                self.human_player = -1
            self.set_human_player()

        if self.kbd_handler.humandown:
            self.kbd_handler.humandown = False
            self.human_player -= 1
            if self.human_player < -1:
                self.human_player = len(self.pp_engine.players) - 1
            self.set_human_player()

        if self.kbd_handler.restart:
            self.gui_canvas.delete("all")
            self.pp_engine = PredPreyEngine()
            self.pp_engine.add_player(Pred)
            self.pp_engine.add_player(Pred)
            self.pp_engine.add_player(Prey)
            self.pp_engine.add_player(Prey)
            self.pp_engine.init_engine()
            self.setup_game_window()
            #self.set_human_player()
            self.kbd_handler.restart = False

        if self.kbd_handler.playpause:
            self.kbd_handler.playpause = False
            self.sim_running = not self.sim_running

        if self.sim_running:
            self.frame += 1

            if self.frame >= self.frames_until_update:
                self.frame = 0

                update = None
                human_action = self.get_human_action()

                # If simulation is running, get updates
                if self.pp_engine.check_running():
                    if self.human_player < 0:
                        self.pp_engine.update_ai()
                        update = self.pp_engine.next()
                    elif self.human_player >= 0 and (self.playing_real_time or human_action):
                        self.pp_engine.update_ai()
                        self.pp_engine.set_action(player=self.human_player, action=human_action)
                        update = self.pp_engine.next()

                # Store the update
                self.current_update = update

            # === Movement (animated)
            # Update the GUI
            self.update_gui()

            # Move characters
            self.update_characters(self.current_update)

            # Draw objects
            self.update_objects()

        # Maintain loop
        time_to_next = self.frame_length
        if self.kbd_handler.quadspeed:
            time_to_next //= 4
        self.tkinter_instance.after(time_to_next, self.render_frame)


def main():
    pp_engine = PredPreyEngine()
    pp_engine.add_player(Pred)
    pp_engine.add_player(Pred)
    pp_engine.add_player(Prey)
    pp_engine.add_player(Prey)
    pp_engine.init_engine()

    gui = PredPreyGUI(pp_engine)
    gui.run_simulation()

    # while pp_engine.check_running():
    #     pp_engine.update_ai()
    #     pp_engine.next()
    # print("Finished in", pp_engine.time, "steps.")


if __name__ == "__main__":
    main()
