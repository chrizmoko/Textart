"""
File: textart/converter.py
"""


from PIL import Image, UnidentifiedImageError
import json
import os.path

from collections.abc import Iterable, Iterator


class TextartError(Exception):
    """A generic textart package error."""

    def __init__(self, message) -> None:
        self._message = message
        Exception.__init__(self, message)

    def get_message(self) -> str:
        """Returns the error message."""
        return '[ERROR] ' + self._message


class Palette:
    """Represents the palette of text characters to be substituted when
    converting from a value within [0, 1] to a character. The first character
    in the palette corresponds to a value of 0, and the last character a value
    of 1.
    """

    def __init__(self, characters: Iterable[str]) -> None:
        if len(characters) == 0:
            raise ValueError('Expected one or more characters.')
        self._palette = list(c for c in characters)
        self._is_reversed = False

    def get_character(self, value: float) -> str:
        """Returns the character corresponding to the value within [0, 1]."""
        return self[value]

    def set_character(self, value: float, character: str) -> None:
        """Sets the character corresponding to the value within [0, 1]."""
        self[value] = character

    def reverse(self) -> None:
        """Reverses the order of the palette."""
        self._palette = list(reversed(self._palette))
        self._is_reversed = not self._is_reversed

    def is_reversed(self) -> bool:
        """Determines if the palette is currently reversed."""
        return self._is_reversed

    def __getitem__(self, value: float) -> str:
        """Returns the character corresponding to the value within [0, 1]."""
        self._check_value_range(value)
        return self._palette[self._value_to_index(value)]

    def __setitem__(self, value: float, character: str) -> None:
        """Sets the character corresponding to the value within [0, 1]."""
        self._check_value_range(value)
        self._palette[self._value_to_index(value)] = character

    def __iter__(self) -> Iterator[str]:
        """An iterator over all the characters in the palette starting from the
        0-valued character to the 1-valued character.
        """
        return iter(self._palette)

    def __len__(self) -> int:
        """Returns the number of characters there are in the palette."""
        return len(self._palette)

    def __repr__(self) -> str:
        return repr(self.__class__)[8:-2] + '(' + repr(str(self)) + ')'

    def __str__(self) -> str:
        return ''.join(self._palette)

    def _value_to_index(self, value):
        """Helper function that thresholds a real value into an index."""
        return round(value * (len(self._palette) - 1))

    def _check_value_range(self, value):
        """Helper method that raises a ValueError for out of range values."""
        if value < 0 or value > 1:
            raise ValueError('Expected a value within the range [0, 1].')


class PaletteFactory:
    """Manages palettes and patterns."""

    def __init__(self) -> None:
        self._patterns = {}

    def register_pattern(self, name: str, pattern: str) -> None:
        """Registers a pattern to the factory."""
        self._patterns[name] = pattern

    def unregister_pattern(self, name: str) -> None:
        """Unregisters a pattern from the factory."""
        if name in self._patterns:
            del self._patterns[name]

    def get_palette(self, name: str) -> Palette:
        """Builds a palette from the pattern and returns it."""
        if name not in self._patterns:
            raise KeyError('Factory does not contain name.')
        return Palette(self._patterns[name])

    def names(self) -> Iterator[str]:
        """A view into the names registered to the factory."""
        return self._patterns.keys()

    def patterns(self) -> Iterator[str]:
        """A view into the patterns registered to the factory."""
        return self._patterns.values()

    def entries(self) -> Iterator[tuple[str, str]]:
        """A view into the names and their registered patterns."""
        return self._patterns.items()

    def __iter__(self) -> Iterator[str]:
        """A view into the names registered to the factory."""
        return self.names()

    def __repr__(self) -> str:
        entries = ','.join(repr(k) + ': ' + repr(v) for k, v in
                           self._patterns.items())
        return repr(self.__class__)[8:-2] + '({' + entries + '})'


def read_palette_file(file_path: str) -> PaletteFactory:
    """Reads a formatted json file and returns a PaletteFactory object based on
    the palettes stored in the file. Errors in reading the file results in an
    empty PaletteFactory object being returned.
    """
    with open(file_path, 'rb') as file:
        factory = PaletteFactory()

        # Read from json file and register to factory
        for key, value in json.load(file).items():
            if type(key) != str or type(value) != str:
                raise TypeError('JSON file data must all be type str.')
            factory.register_pattern(key, value)

        return factory

    return PaletteFactory()


def read_image_file(file_path: str) -> Image.Image:
    """Opens and reads an image file and returns a copy of it."""
    # Check file path
    if not os.path.exists(file_path):
        message = ('A file was not selected or does not exist. Please choose '
                   'a valid file.')
        raise TextartError(message)

    # Attempt to open file as image
    try:
        file = Image.open(file_path, 'r')
    except UnidentifiedImageError:
        message = ('The file selected could not be recognized as an image. '
                   'Please choose a file that is an image.')
        raise TextartError(message)

    # Copy image and close file
    image = file.copy()
    file.close()

    return image


class BaseImage:
    """An encapsulation of the 'PIL.Image.Image' class where the image is
    processed and converted into a usable image for creating the its text
    representation.

    The class does not hold a reference to the original image and does not
    maintain it.
    """

    def __init__(self, image: Image.Image, max_width: int = None,
                 max_height: int = None) -> None:
        # Set the size constraints
        max_width = image.width if max_width is None else max_width
        max_height = image.height if max_height is None else max_height

        # Check for invalid values
        if max_width < 0:
            raise ValueError('Expected max_width to be greater than 0.')
        if max_height < 0:
            raise ValueError('Expected max_height to be greater than 0.')

        # Process image
        new_image = BaseImage._downsize_image(image, max_width, max_height)
        new_image = BaseImage._grayscale_image(new_image)

        self._image = new_image

    def value_at(self, x: int, y: int) -> float:
        """Returns the value of the pixel at position (x, y) as a float within
        the range of [0, 1].
        """
        if x < 0 or x > self._image.width:
            raise IndexError('Pixel coordinate x is out of range.')
        if y < 0 or y > self._image.height:
            raise IndexError('Pixel coordinate y is out of range.')
        return self._image.getpixel((x, y)) / 255

    def get_width(self) -> int:
        """Returns the pixel width of the image."""
        return self._image.width

    def get_height(self) -> int:
        """Returns the pixel height of the image."""
        return self._image.height

    def get_size(self) -> tuple[int, int]:
        """Returns the pixel dimensions of the image."""
        return self._image.width, self._image.height

    def __iter__(self) -> Iterator[float]:
        """Returns the values of each pixel in the image as floats within the
        range of [0, 1]. The iterator starts at the top-left pixel of the image
        and traverses the image in row-major order until it completes at the
        bottom-right pixel of the image.
        """
        def iterator(image):
            for y in range(image.height):
                for x in range(image.width):
                    yield image.getpixel((x, y)) / 255
        return iterator(self._image)

    @staticmethod
    def _downsize_image(image, max_width, max_height):
        """Helper method that places constraints on the image's dimensions so
        that when the image is scaled down, the image maintains its aspect
        ratio while conforming to the dimension constraints.
        """
        width, height = image.size

        # Rescale image to max_width while maintaining aspect ratio
        if image.width > max_width:
            width = max_width
            height = int(max_width * image.height / image.width)

        # If height too large, rescale again while maintaining aspect ratio
        if height > max_height:
            height = max_height
            width = int(max_height * image.width / image.height)

        # Value must be a minimum of 1
        width = 1 if width == 0 else width
        height = 1 if height == 0 else height

        return image.resize((width, height))

    @staticmethod
    def _grayscale_image(image):
        """Helper method that converts an image to grayscale."""
        return image.convert('L')


class TextImage:
    """The character copy of the base image."""

    def __init__(self, base_image: BaseImage, palette: Palette) -> None:
        pixels = iter(base_image)
        width, height = base_image.get_size()

        def limited(iterator, maximum):
            for _ in range(maximum):
                yield next(iterator)

        self._lines = tuple(''.join(palette[v] for v in limited(pixels, width))
                            for _ in range(height))
        self._width = width
        self._height = height

    def get_width(self) -> int:
        """Returns the character width of the text image."""
        return self._width

    def get_height(self) -> int:
        """Returns the character height of the text image."""
        return self._height

    def get_size(self) -> tuple[int, int]:
        """Returns the character width and height of the text image."""
        return self._width, self._height

    def format(self, stretch: tuple[int, int] = (1, 1)) -> str:
        """Returns the text art string that has been formatted."""
        x_stretch, y_stretch = stretch
        return '\n'.join(
            '\n'.join(''.join(char * x_stretch for char in line)
                      for _ in range(y_stretch)) for line in self._lines)

    def __iter__(self) -> Iterator[str]:
        """Iterate through each text character in the image in row-major
        order.
        """
        def iterator(self):
            for y in range(self._height):
                for x in range(self._width):
                    yield self._lines[y][x]
        return iterator(self)

    def __len__(self) -> int:
        """Returns the number of characters that are in the text image."""
        return self._width * self._height

    def __str__(self) -> str:
        """Returns the text image as a string."""
        return '\n'.join(self._lines)
