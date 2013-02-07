import os
import Tkinter as tk
from PIL import Image, ImageTk
from datetime import timedelta
from simulator import World #, Simulator

class AppWindow(object):
    def __init__(self):
        self._is_playing = False
        self._images = {}

        self._create_layout()

    def run(self):
        self._root.mainloop()

    def _get_image(self, name):
        image = self._images.get(name)
        if image is None:
            image = ImageTk.PhotoImage(Image.open(os.path.join('resources/icons', name)))
            self._images[name] = image
        return image

    def _create_simulator(self):
        world = World()
        world.build_from_file('settings.xml')

        self._view.tag_bind('robot', '<Button-1>', self._focus_view)

        # self._simulator = Simulator(world, 0.01)
        # self._simulator.step()

    def _create_layout(self):
        self._root = tk.Tk()
        self._root.title('Sim.I.am')
        self._root.geometry('800x600')

        # % Create UI buttons
        # icon_file = fullfile(obj.root_, 'resources/splash/simiam_splash.png');
        # if(isunix)
        #     icon_url = ['file://' icon_file];
        # else
        #     icon_url = strrep(['file:/' icon_file],'\','/');
        # end
        # button_string = ['<html><div style="text-align: center"><img src="' icon_url '"/>' ...
        #        '<br>Welcome to <b>Sim.I.am</b>, a robot simulator.' ...
        #        '<br>This release is codenamed <em>Sim the First</em>.' ...
        #        '<br>The simulator is maintained by the GRITSLab at' ...
        #        '<br><a href="http://gritslab.gatech.edu/projects/robot-simulator">http://gritslab.gatech.edu/projects/robot-simulator</a>' ...
        #        '</div><br><ol><li>Start the demo by clicking the play button.</li><li>Use the mouse to pan and zoom.</li><li>Double click anywhere on the grid to send the robot to that location.</li><li>Select the robot to follow it</li><li>If your robot crashes, press the rewind button.</li></ol>' ...
        #        '</html>'];
        # ui_args = {'Style','pushbutton', 'String', button_string, 'ForegroundColor', 'w', 'FontWeight', 'bold', 'BackgroundColor', obj.ui_colors_.gray, 'Callback', @obj.ui_button_start};
        # ui_parent = obj.layout_.Cell(2,1);
        # obj.logo_ = uicontrol(ui_parent, ui_args{:});
        # set(obj.logo_, 'Enable', 'off');
        # set(findjobj(obj.logo_), 'Border', []);
        # set(obj.logo_, 'BackgroundColor', [96 184 206]/255);


        button_config = [
            ('play', self._on_start, 'ui_control_play.png', tk.NORMAL, (4, 6)),
            ('reset', self._on_reset, 'ui_control_reset.png', tk.DISABLED, (4, 5)),
            ('home', self._on_home, 'ui_control_home.png', tk.DISABLED, (4, 1)),
            ('zoom_in', self._on_zoom_in, 'ui_control_zoom_in.png', tk.DISABLED, (4, 11)),
            ('zoom_out', self._on_zoom_out, 'ui_control_zoom_out.png', tk.DISABLED, (4, 10))
        ]

        self._buttons = {}

        for config in button_config:
            button = tk.Button(
                self._root,
                command=config[1],
                image=self._get_image(config[2]),
                state=config[3])
            button.grid(row=config[4][0], column=config[4][1])
            self._buttons[config[0]] = button

        tk.Label(
            self._root,
            image=self._get_image('ui_status_ok.png'),
            ).grid(row=1, column=9)

        tk.Label(
            self._root,
            image=self._get_image('ui_status_clock.png'),
            ).grid(row=1, column=10)

        self._time_label = tk.Label(self._root)
        self._time_label.grid(row=1, column=11)
        self._set_time(timedelta(0))

    def _on_start(self):
        self._view = tk.Canvas(self._root)
        self._view.grid(row=2, column=1)
                          
#             % Target Marker
#             obj.target_marker_ = plot(obj.view_, inf, inf, ...
#                 'Marker', 'o', ...
#                 'MarkerFaceColor', obj.ui_colors_.green, ...
#                 'MarkerEdgeColor', obj.ui_colors_.green, ...
#                 'MarkerSize', 10);
            
#             set(obj.view_, 'XGrid', 'on');
#             set(obj.view_, 'YGrid', 'on');
#             set(obj.view_, 'XTickMode', 'manual');
#             set(obj.view_, 'YTickMode', 'manual');
#             set(obj.view_, 'Units', 'pixels');
#             view_quad = get(obj.view_, 'Position');
#             set(obj.view_, 'Units', 'normal');
            
#             width = view_quad(3); 
#             height = view_quad(4);
            
#             obj.ratio_ = width/height;          
#             obj.zoom_level_ = 1;
#             obj.boundary_ = 2.5;
            
#             obj.ui_set_axes();
                        
#             obj.create_callbacks();

        self._create_simulator()
            
        self._is_playing = True
        self._buttons['play'].config(
            image=self._get_image('ui_control_pause.png'),
            command=self._on_play)
            
#             obj.is_ready_ = true;
        self._buttons['home'].config(state=tk.NORMAL)
        self._buttons['zoom_in'].config(state=tk.NORMAL)
        self._buttons['zoom_out'].config(state=tk.NORMAL)

        self._set_time(timedelta(0))

#             obj.simulator_.start();

    def _on_play(self):
        self._is_playing = not self._is_playing
        if self._is_playing:
            self._buttons['play'].config(image=self._get_image('ui_control_pause.png'))
            #self._simulator.start()
        else:
            self._buttons['play'].config(image=self._get_image('ui_control_play.png'))
            #self._simulator.stop()

    def _on_reset(self):
        pass

    def _on_home(self):
        pass

    def _on_zoom_in(self):
        pass

    def _on_zoom_out(self):
        pass

    def _focus_view(self):
        pass

    def _set_time(self, value):
        self._time = value
        self._time_label.config(text=str(self._time))

    def _update_time(self, delta):
        self._set_time(self._time + delta)
