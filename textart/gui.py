"""
File: textart/gui.py

The module that defines and maintains the GUI of the program.
"""


import textart.utils as utils
import tkinter as tk
from tkinter import ttk, filedialog


class Application:
    """The application window."""
    
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
        
        # References to various widgets (initialized in setup)
        self._process_image_button = None
        self._notice_label = None
        self._reverse_check = None
        self._double_check = None

        self._char_width_str = tk.StringVar()
        self._char_height_str = tk.StringVar()
        self._palette_str = tk.StringVar()
        
        self._palette_output_text = None
        self._image_output_text = None
        
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
        self._notice_label.set_text('Image read successfully. (' + self._image_path + ')')
        self._process_image_button['state'] = tk.NORMAL
    
    def _cmd_process_image(self):
        """Command method for processing an opened image."""
        if self._palette == None:
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
        self._notice_label.set_text('Image processed successfully. (' + self._image_path + ')')
        self._double_check['state'] = 'normal'
        self._cmd_double_output()
    
    def _cmd_select_palette(self, _):
        """Command method for handling the palette combobox selection."""
        # Get palette from the combobox selection
        palette_name = self._palette_str.get()
        palette = self._palette_factory.get_palette(palette_name)
        
        # If checkbox is checked, uncheck the checkbox
        if self._palette != None and 'selected' in self._reverse_check.state():
            self._reverse_check.invoke()
        
        # Update the GUI
        self._palette_output_text.set_text(palette)
        self._reverse_check['state'] = 'normal'

        # Store the palette
        self._palette = palette
        
    def _cmd_reverse_palette(self):
        """Command method for reversing the order of the selected palette."""
        # Reverse the palette and update GUI
        self._palette.reverse()
        self._palette_output_text.set_text(self._palette)
    
    def _cmd_double_output(self):
        """Command method for doubling the width of the output text image."""
        # Generate the image and set size of text output
        if 'selected' in self._double_check.state():
            output_text = self._text_image.format(stretch=(2, 1))
            self._image_output_text['width'] = self._text_image.get_width() * 2
        else:
            output_text = self._text_image.format(stretch=(1, 1))
            self._image_output_text['width'] = self._text_image.get_width()
        self._image_output_text['height'] = self._text_image.get_height()
        self._image_output_text.set_text(output_text)
    
    def _setup_window(self):
        """Helper method that sets up the window's title and dimensions."""
        self._tk_root.title(Application._TITLE)
        self._tk_root.minsize(*Application._SIZE)
        self._tk_root.geometry(str(Application._SIZE[0]) + 'x' + str(Application._SIZE[1]))
    
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
        
        open_button = tk.Button(frame, text='Open Image', command=self._cmd_open_image, width=16)
        open_button.grid(row=0, column=0)
        
        process_button = tk.Button(frame, text='Process Image', command=self._cmd_process_image, state='disabled', width=16)
        process_button.grid(row=0, column=1)
        self._process_image_button = process_button
        
        notice_text = ('Click the "Open Image" button to choose an image to '
                        'convert.')
        notice_label = Label(frame, text=notice_text, justify='left')
        notice_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(Application._INNER_PAD, 0))
        self._notice_label = notice_label
        
        frame.pack(side='top', fill='x', expand=False, padx=Application._OUTER_PAD, pady=Application._OUTER_PAD)
    
    def _setup_options_widgets(self):
        """Helper method that creates all widgets related to palettes."""
        frame = tk.Frame(self._tk_root)
        
        # Image size options frame
        size_frame = tk.Frame(frame)
        size_frame.columnconfigure(0, weight=0)
        size_frame.columnconfigure(1, weight=1)
        
        width_label = tk.Label(size_frame, text='Maximum character width', justify='left')
        width_label.grid(row=0, column=0, sticky='w', padx=(0, Application._INNER_PAD))
        
        height_label = tk.Label(size_frame, text='Maximum character height', justify='left')
        height_label.grid(row=1, column=0, sticky='w', padx=(0, Application._INNER_PAD))
        
        width_entry = IntEntry(size_frame, textvariable=self._char_width_str)
        width_entry.grid(row=0, column=1, sticky='ew')
        
        height_entry = IntEntry(size_frame, textvariable=self._char_height_str)
        height_entry.grid(row=1, column=1, sticky='ew')
        
        info_text = 'NOTICE: Both fields empty defaults to original resolution.'
        info_label = Label(size_frame, text=info_text, justify='left')
        info_label.grid(row=2, column=0, columnspan=2, sticky='w')
        
        size_frame.pack(side='top', fill='x', expand=True)
        
        # Palette options frame
        palette_frame = tk.Frame(frame)
        
        palette_combobox_values = tuple(self._palette_factory.names())
        palette_combobox = ttk.Combobox(palette_frame, textvariable=self._palette_str, values=palette_combobox_values, state='readonly')
        palette_combobox.bind('<<ComboboxSelected>>', self._cmd_select_palette)
        palette_combobox.set('Select palette...')
        palette_combobox.pack(side='left')
        
        reverse_check = ttk.Checkbutton(palette_frame, text='Reverse palette', command=self._cmd_reverse_palette, state='disabled')
        reverse_check.pack(side='left', padx=(Application._INNER_PAD, 0))
        self._reverse_check = reverse_check
        
        palette_frame.pack(side='top', fill='x', expand=True, pady=(Application._INNER_PAD, 0))
        
        # Display
        palette_text = Text(frame, width=128, height=1, state='disabled')
        palette_text.pack(fill='x', expand=True, pady=(Application._INNER_PAD, 0))
        self._palette_output_text = palette_text
        
        frame.pack(side='top', fill='x', expand=False, padx=Application._OUTER_PAD, pady=Application._OUTER_PAD)
    
    def _setup_output_widgets(self):
        """Helper method that creates all widgets related to the text output."""
        frame = tk.Frame(self._tk_root)
        
        double_check = ttk.Checkbutton(frame, text='Stretch output width by double', command=self._cmd_double_output, state='disabled')
        double_check.pack(side='top', fill='x')
        self._double_check = double_check
        
        output = Text(frame, wrap='none', width=128, height=128, state='disabled')
        output.pack(side='bottom', fill='both', expand=True, pady=(Application._INNER_PAD, 0))
        self._image_output_text = output
        
        frame.pack(side=tk.BOTTOM, fill='both', expand=True, padx=Application._OUTER_PAD, pady=Application._OUTER_PAD)


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
            self['validatecommand'] = (self.register(lambda S : S.isdigit()), 
                                       *script_substitutions)


def main():
    """The entry point of the application."""
    palette_factory = utils.read_palette_file(r'./defaultpalettes.json')
    Application(tk.Tk(), palette_factory).run()


if __name__ == '__main__':
    main()