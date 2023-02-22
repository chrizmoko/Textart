"""
File: textart/gui.py

The module that defines and maintains the GUI of the program. Moreover, the
module is also an entry point to the program.
"""


import sys
import os.path


# Path resolution to allow package modules to be referenced as "textart.*"
package_path = os.path.dirname(__file__)
path, _ = os.path.split(package_path)
if path not in sys.path:
    sys.path.insert(0, path)


from textart import utils
import tkinter as tk
import tkinter.font as font
from tkinter import ttk, filedialog


class Application:
    """This is the application window and is responsible for the appearance
    and functionality of the program.
    """

    _TITLE = 'Textart'
    _SIZE = (400, 300)

    _INNER_PAD = 5
    _OUTER_PAD = 10

    def __init__(self, root, palette_factory):
        self._palette_factory = palette_factory

        self._image_path = None
        self._image = None
        self._palette = None
        self._text_image = None

        self._tk_root = root

        # References to various interaction widgets (initialized in setup)
        self._open_image_button = None
        self._process_image_button = None
        self._notice_label = None
        self._reverse_palette_check = None
        self._double_output_width_check = None

        self._char_width_str = tk.StringVar()
        self._char_height_str = tk.StringVar()
        self._palette_str = tk.StringVar()
        self._output_display_size_str = tk.StringVar()

        self._palette_display_text = None
        self._output_image_text = None

        # Setup the gui
        self._setup_window()
        self._setup_widgets()

    def run(self):
        """Starts and runs the application."""
        self._tk_root.mainloop()

    def _cmd_open_image(self):
        """Command method for opening (and pre-processing) an image."""
        # Attempt to open and read an image file
        try:
            file_path = filedialog.askopenfilename(title='Open Image')
            self._image = utils.read_image_file(file_path)
            self._image_path = file_path
        except utils.TextartError as e:
            self._notice_label.set_text(e.get_message(), color='red')
            return

        # Update the GUI
        self._notice_label.set_text('Image read successfully. (' +
                                    self._image_path + ')')
        self._process_image_button['state'] = 'normal'

    def _cmd_process_image(self):
        """Command method for processing an opened image."""
        if self._palette is None:
            error = utils.TextartError('A palette has not been selected. '
                                       'Please select a palette.')
            self._notice_label.set_text(error.get_message(), color='red')
            return

        # Obtain max width/height from entry boxes or default to image size
        width_str = self._char_width_str.get()
        width = None if width_str == '' else int(width_str)

        height_str = self._char_height_str.get()
        height = None if height_str == '' else int(height_str)

        # Process the image
        base_image = utils.BaseImage(self._image, width, height)
        text_image = utils.TextImage(base_image, self._palette)
        self._text_image = text_image

        # Update the GUI
        self._notice_label.set_text('Image processed successfully. (' +
                                    self._image_path + ')')
        self._double_output_width_check['state'] = 'normal'
        self._cmd_double_output_width()

    def _cmd_select_palette(self, _):
        """Command method for handling the palette combobox selection."""
        # Get palette from the combobox selection
        palette_name = self._palette_str.get()
        palette = self._palette_factory.get_palette(palette_name)

        # If checkbox is checked, uncheck the checkbox
        if (self._palette is not None and
            'selected' in self._reverse_palette_check.state()):
            self._reverse_palette_check.invoke()

        # Update the GUI
        self._palette_display_text.set_text(palette)
        self._reverse_palette_check['state'] = 'normal'

        # Store the palette
        self._palette = palette

    def _cmd_reverse_palette(self):
        """Command method for reversing the order of the selected palette."""
        # Reverse the palette and update GUI
        self._palette.reverse()
        self._palette_display_text.set_text(self._palette)
    
    def _cmd_select_output_display_size(self, _):
        """Command method for handling display size combobox selection."""
        # Get output display font size from the combobox selection
        output_display_size = int(self._output_display_size_str.get())

        # Change display font size
        font_name = 'TkFixedFont'
        output_display_font = font.Font(font=font.nametofont(font_name))
        output_display_font.configure(size=output_display_size)
        self._output_image_text.configure(font=output_display_font)

    def _cmd_double_output_width(self):
        """Command method for doubling the width of the output text image."""
        # Generate the image and set size of text output
        if 'selected' in self._double_output_width_check.state():
            output_text = self._text_image.format(stretch=(2, 1))
            self._output_image_text['width'] = self._text_image.get_width() * 2
        else:
            output_text = self._text_image.format(stretch=(1, 1))
            self._output_image_text['width'] = self._text_image.get_width()
        self._output_image_text['height'] = self._text_image.get_height()
        self._output_image_text.set_text(output_text)

    def _setup_window(self):
        """Helper method that sets up the window's title and dimensions."""
        self._tk_root.title(Application._TITLE)
        self._tk_root.minsize(*Application._SIZE)
        self._tk_root.geometry(str(Application._SIZE[0]) + 'x' +
                               str(Application._SIZE[1]))

    def _setup_widgets(self):
        """Helper method that creates all widgets for the application."""
        self._setup_management_widgets()

        sep1 = ttk.Separator(self._tk_root, orient='horizontal')
        sep1.pack(fill='x', padx=Application._OUTER_PAD)

        self._setup_options_widgets()

        sep2 = ttk.Separator(self._tk_root, orient='horizontal')
        sep2.pack(fill='x', padx=Application._OUTER_PAD)

        self._setup_output_widgets()

    def _setup_management_widgets(self):
        """Helper method that creates all widgets related to image management
        functions.
        """
        frame = tk.Frame(self._tk_root)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.pack(
            side='top',
            fill='x',
            expand=False,
            padx=Application._OUTER_PAD,
            pady=Application._OUTER_PAD
        )

        open_image_button = tk.Button(frame,
            text='Open Image', 
            command=self._cmd_open_image, 
            width=16
        )
        open_image_button.grid(
            row=0,
            column=0
        )

        process_image_button = tk.Button(frame,
            text='Process Image',
            command=self._cmd_process_image,
            state='disabled',
            width=16
        )
        process_image_button.grid(
            row=0,
            column=1
        )
        self._process_image_button = process_image_button

        notice_label = Label(
            frame,
            text=('Click the "Open Image" button to select an image to '
                  'convert.'),
            justify='left'
        )
        notice_label.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky='w',
            pady=(Application._INNER_PAD, 0)
        )
        self._notice_label = notice_label

    def _setup_options_widgets(self):
        """Helper method that creates all widgets related to palettes."""
        frame = tk.Frame(self._tk_root)
        frame.pack(
            side='top',
            fill='x',
            expand=False,
            padx=Application._OUTER_PAD,
            pady=Application._OUTER_PAD
        )

        # Image size management frame
        image_size_management_frame = tk.Frame(frame)
        image_size_management_frame.columnconfigure(0, weight=0)
        image_size_management_frame.columnconfigure(1, weight=1)
        image_size_management_frame.pack(
            side='top',
            fill='x',
            expand=True
        )

        width_label = tk.Label(image_size_management_frame,
            text='Maximum character width',
            justify='left'
        )
        width_label.grid(
            row=0,
            column=0,
            sticky='w',
            padx=(0, Application._INNER_PAD)
        )

        height_label = tk.Label(image_size_management_frame,
            text='Maximum character height',
            justify='left'
        )
        height_label.grid(
            row=1,
            column=0,
            sticky='w',
            padx=(0, Application._INNER_PAD)
        )

        width_entry = IntEntry(image_size_management_frame,
            textvariable=self._char_width_str
        )
        width_entry.grid(
            row=0,
            column=1,
            sticky='ew'
        )

        height_entry = IntEntry(image_size_management_frame,
            textvariable=self._char_height_str
        )
        height_entry.grid(
            row=1,
            column=1,
            sticky='ew'
        )

        info_label = Label(image_size_management_frame, 
            text='NOTICE: Both fields empty defaults to original resolution.',
            justify='left'
        )
        info_label.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky='w'
        )

        # Palette management frame
        palette_management_frame = tk.Frame(frame)
        palette_management_frame.pack(
            side='top',
            fill='x',
            expand=True,
            pady=(Application._INNER_PAD, 0)
        )

        palette_combobox = ttk.Combobox(
            palette_management_frame,
            textvariable=self._palette_str,
            values=tuple(self._palette_factory.names()),
            state='readonly'
        )
        palette_combobox.bind(
            '<<ComboboxSelected>>',
            self._cmd_select_palette
        )
        palette_combobox.set('Select palette...')
        palette_combobox.pack(
            side='left'
        )

        reverse_palette_check = ttk.Checkbutton(
            palette_management_frame,
            text='Reverse palette',
            command=self._cmd_reverse_palette,
            state='disabled'
        )
        reverse_palette_check.pack(
            side='left',
            padx=(Application._INNER_PAD, 0)
        )
        self._reverse_palette_check = reverse_palette_check

        # Palette display
        palette_display_text = Text(
            frame,
            width=128,
            height=1,
            state='disabled',
        )
        palette_display_text.pack(
            fill='x',
            expand=True,
            pady=(Application._INNER_PAD, 0)
        )
        self._palette_display_text = palette_display_text

    def _setup_output_widgets(self):
        """Helper method that creates all widgets related to the text output."""
        frame = tk.Frame(self._tk_root)
        frame.pack(
            side='bottom',
            fill='both',
            expand=True,
            padx=Application._OUTER_PAD,
            pady=Application._OUTER_PAD
        )

        # Output display management frame
        output_display_management_frame = tk.Frame(frame)
        output_display_management_frame.columnconfigure(0, weight=0)
        output_display_management_frame.columnconfigure(1, weight=1)
        output_display_management_frame.pack(
            side='top',
            fill='x',
            expand=True
        )

        monospace_font = font.nametofont('TkFixedFont')
        max_difference = 7
        font_sizes = (monospace_font['size'] - i for i in range(max_difference))

        size_combobox = ttk.Combobox(
            output_display_management_frame,
            textvariable=self._output_display_size_str,
            values=tuple(font_sizes),
            state='readonly'
        )
        size_combobox.bind(
            '<<ComboboxSelected>>',
            self._cmd_select_output_display_size
        )
        size_combobox.set('Select display font size...')
        size_combobox.pack(
            side='left'
        )

        double_output_width_check = ttk.Checkbutton(
            output_display_management_frame,
            text='Stretch output width by double',
            command=self._cmd_double_output_width,
            state='disabled'
        )
        double_output_width_check.pack(
            side='top',
            fill='x',
        )
        self._double_output_width_check = double_output_width_check

        output_image_text = Text(frame,
            wrap='none',
            state='disabled'
        )
        output_image_text.pack(
            side='bottom',
            fill='both',
            expand=True,
            pady=(Application._INNER_PAD, 0)
        )
        self._output_image_text = output_image_text


class Label(tk.Label):
    """An extension to the 'tkinter.Label' class that makes setting the text
    content in the widget more convenient.
    """

    _TEXT_ATTRIBUTE = 'text'
    _COLOR_ATTRIBUTE = 'foreground'

    def clear_text(self):
        """Removes all text content in the label."""
        self[Label._TEXT_ATTRIBUTE] = ''

    def set_text(self, text, color='black'):
        """Replaces the current text with new text that can be colored. If not
        specified, the default text color is black.
        """
        self[Label._TEXT_ATTRIBUTE] = text
        self[Label._COLOR_ATTRIBUTE] = color

    def set_color(self, color):
        """Changes the color of the text."""
        self[Label._COLOR_ATTRIBUTE] = color

    def get_color(self):
        """Returns the color of the text."""
        return self[Label._COLOR_ATTRIBUTE]


class Text(tk.Text):
    """An extension to the 'tkinter.Text' class that makes setting the text
    content in the widget more convenient.
    """

    _STATE_ATTRIBUTE = 'state'

    def clear_text(self):
        """Removes all text content in the textbox."""
        prev_state = self[Text._STATE_ATTRIBUTE]
        self[Text._STATE_ATTRIBUTE] = tk.NORMAL
        self.delete('1.0', 'end')
        self[Text._STATE_ATTRIBUTE] = prev_state

    def set_text(self, content):
        """Replaces the contents of the textbox with new text content."""
        prev_state = self[Text._STATE_ATTRIBUTE]
        self[Text._STATE_ATTRIBUTE] = tk.NORMAL
        self.replace('1.0', 'end', content)
        self[Text._STATE_ATTRIBUTE] = prev_state

    def is_enabled(self):
        """Determines if the text state is normal or disabled."""
        return self[Text._STATE_ATTRIBUTE] == 'normal'


class IntEntry(tk.Entry):
    """An extension to the 'tkinter.Entry' class that only accepts non-negative
    integer values.
    """

    def __init__(self, *args, **kwargs):
        tk.Entry.__init__(self, *args, **kwargs)
        if ('validate' not in kwargs) and ('validatecommand' not in kwargs):
            # Want to validate on key press
            self['validate'] = 'key'

            # Track the value that is inserted/deleted
            script_substitutions = ('%S',)
            self['validatecommand'] = (self.register(lambda S: S.isdigit()), 
                                       *script_substitutions)


def main():
    """The entry point of the application."""
    # Create palette factory from json file
    path = os.path.dirname(__file__) + os.path.sep
    palette_factory = utils.read_palette_file(path + 'defaultpalettes.json')

    # Create and run the application
    Application(tk.Tk(), palette_factory).run()


if __name__ == '__main__':
    main()
