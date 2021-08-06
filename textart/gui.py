"""
File: textart/gui.py

The module that defines and maintains the GUI of the program.
"""


from textart.utils import Palette, PaletteFactory, read_palette_file
import tkinter as tk
from tkinter import ttk


class Application:
    """The application window."""
    
    def __init__(self, root):
        self._palette_factory = read_palette_file('./defaultpalettes.json')
        self._tk_root = root
        
        # Setup the gui
        self._setup_window()
        self._setup_widgets()
    
    def run(self):
        """Starts and runs the application."""
        self._tk_root.mainloop()
    
    def _setup_window(self):
        """Helper method that sets up the window's title and dimensions."""
        TITLE = 'Textart'
        SIZE = (400, 300)
        
        self._tk_root.title(TITLE)
        self._tk_root.minsize(*SIZE)
        self._tk_root.geometry(str(SIZE[0]) + 'x' + str(SIZE[1]))
    
    def _setup_widgets(self):
        """Helper method that creates all widgets for the application."""
        self._setup_management_widgets()
        
        sep1 = ttk.Separator(self._tk_root, orient=tk.HORIZONTAL)
        sep1.pack(fill=tk.X, padx=10)
        
        self._setup_palette_widgets()
        
        sep2 = ttk.Separator(self._tk_root, orient=tk.HORIZONTAL)
        sep2.pack(fill=tk.X, padx=10)
        
        self._setup_output_widgets()
    
    def _setup_management_widgets(self):
        """Helper method that creates all widgets related to image management
        functions.
        """
        frame = tk.Frame(self._tk_root)
        frame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        open_button = tk.Button(frame, text='Open image', command=None, width=16)
        open_button.grid(row=0, column=0)
        
        process_button = tk.Button(frame, text='Process image', command=None, state=tk.DISABLED, width=16)
        process_button.grid(row=0, column=1)
        
        message = tk.Label(frame, text='TODO: State String')
        message.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def _setup_palette_widgets(self):
        """Helper method that creates all widgets related to palettes."""
        frame = tk.Frame(self._tk_root)
        frame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=10, pady=10)
        
        # Options frame
        options_frame = tk.Frame(frame)
        
        palette_combobox_values = tuple('option ' + str(i) for i in range(20))
        palette_combobox = ttk.Combobox(options_frame, values=palette_combobox_values)
        palette_combobox.set('Select palette...')
        palette_combobox.pack(side=tk.LEFT, padx=(0, 5))
        
        reverse_check = ttk.Checkbutton(options_frame, text='Reverse palette', state=tk.DISABLED)
        reverse_check.pack(side=tk.LEFT, padx=(5, 0))
        
        options_frame.pack(side=tk.TOP, fill=tk.X, expand=True, pady=(0, 5))
        
        # Display frame
        display_frame = tk.Frame(frame)
        
        palette_text = Textbox(display_frame, width=128, height=1, state=tk.DISABLED)
        palette_text.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        display_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=True, pady=(5, 0))
    
    def _setup_output_widgets(self):
        """Helper method that creates all widgets related to the text output."""
        frame = tk.Frame(self._tk_root)
        
        output = Textbox(frame, wrap=tk.CHAR, width=128, height=128, state=tk.DISABLED)
        output.pack(fill=tk.BOTH, expand=True)
        
        frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)


class Textbox(tk.Text):
    """An extension to the 'tkinter.Text' class that makes setting the text
    content in the widget more convenient.
    """
    
    _STATE_ATTRIBUTE = 'state'
    
    def clear_content(self):
        """Removes all text content in the textbox."""
        prev_state = self[Textbox._STATE_ATTRIBUTE]
        self[Textbox._STATE_ATTRIBUTE] = tk.NORMAL
        self.delete('1.0', tk.END)
        self[Textbox._STATE_ATTRIBUTE] = prev_state

    def set_content(self, content):
        """Replaces the contents of the textbox with new text content."""
        prev_state = self[Textbox._STATE_ATTRIBUTE]
        self[Textbox._STATE_ATTRIBUTE] = tk.NORMAL
        self.delete('1.0', tk.END)
        self.insert('1.0', content)
        self[Textbox._STATE_ATTRIBUTE] = prev_state
        
    def is_enabled(self):
        """Determines if the text state is normal or disabled."""
        return self[Textbox._STATE_ATTRIBUTE] == tk.NORMAL


def main():
    """The entry point of the application."""
    app = Application(tk.Tk())
    app.run()


def main2():
    """Test application."""
    factory = read_palette_file(r'./defaultpalettes.json')
    print(factory)
    input('mmm')
    

if __name__ == '__main__':
    main()