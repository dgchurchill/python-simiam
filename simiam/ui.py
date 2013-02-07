import os
import Tkinter as tk
from PIL import Image, ImageTk
from datetime import timedelta

class AppWindow(object):
    def __init__(self):
        self._time = timedelta()

        self._create_layout()

    def run(self):
        self._root.mainloop()

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

        self._images = []
        def image(name):
            image = ImageTk.PhotoImage(Image.open(os.path.join('resources/icons', name)))
            self._images.append(image)
            return image

        tk.Button(
            self._root,
            image=image('ui_control_play.png'),
            command=self._on_start
            ).grid(row=4, column=6)

        tk.Button(
            self._root,
            image=image('ui_control_reset.png'),
            command=self._on_reset,
            state=tk.DISABLED
            ).grid(row=4, column=5)

        tk.Button(
            self._root,
            image=image('ui_control_home.png'),
            command=self._on_home,
            state=tk.DISABLED
            ).grid(row=4, column=1)

        tk.Button(
            self._root,
            image=image('ui_control_zoom_in.png'),
            command=self._on_zoom_in,
            state=tk.DISABLED
            ).grid(row=4, column=11)

        tk.Button(
            self._root,
            image=image('ui_control_zoom_out.png'),
            command=self._on_zoom_out,
            state=tk.DISABLED
            ).grid(row=4, column=10)

        tk.Label(
            self._root,
            image=image('ui_status_ok.png'),
            ).grid(row=1, column=9)

        tk.Label(
            self._root,
            image=image('ui_status_clock.png'),
            ).grid(row=1, column=10)

        self._time_label = tk.Label(self._root)
        self._time_label.grid(row=1, column=11)
        self._update_clock()

    def _on_start(self):
        pass

    def _on_reset(self):
        pass

    def _on_home(self):
        pass

    def _on_zoom_in(self):
        pass

    def _on_zoom_out(self):
        pass

    def _update_clock(self, delta=timedelta()):
        self._time += delta
        self._time_label.config(text=str(self._time))
