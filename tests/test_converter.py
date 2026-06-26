import numpy as np
from src.converter.ascii_converter import AsciiConverter


def test_to_grayscale_shape():
    converter = AsciiConverter()
    frame = np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)
    gray = converter.to_grayscale(frame)
    assert gray.shape == (100, 200)
    assert gray.dtype == np.uint8


def test_to_grayscale_blue():
    converter = AsciiConverter()
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    frame[:, :, 0] = 255
    gray = converter.to_grayscale(frame)
    expected = int(255 * 0.114)
    assert np.all(gray == expected)


def test_map_to_ascii_shape():
    converter = AsciiConverter()
    gray = np.zeros((5, 10), dtype=np.uint8)
    indices = converter.map_to_ascii(gray)
    assert indices.shape == (5, 10)
    assert indices.dtype == np.uint8


def test_map_to_ascii_black():
    converter = AsciiConverter()
    gray = np.zeros((10, 10), dtype=np.uint8)
    indices = converter.map_to_ascii(gray)
    assert np.all(indices == 0)


def test_map_to_ascii_white():
    converter = AsciiConverter()
    gray = np.full((10, 10), 255, dtype=np.uint8)
    indices = converter.map_to_ascii(gray)
    assert np.all(indices == len(converter.char_set) - 1)


def test_map_to_ascii_mid():
    converter = AsciiConverter()
    gray = np.full((5, 5), 128, dtype=np.uint8)
    indices = converter.map_to_ascii(gray)
    expected = round(128 / 255 * (len(converter.char_set) - 1))
    assert np.all(indices == expected)


def test_convert_output_width():
    converter = AsciiConverter()
    frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    indices = converter.convert(frame, cols=80)
    _, w = indices.shape
    assert w == 80


def test_convert_custom_rows():
    converter = AsciiConverter()
    frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    indices = converter.convert(frame, cols=80, rows=30)
    assert indices.shape == (30, 80)


def test_convert_auto_rows():
    converter = AsciiConverter()
    frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    indices = converter.convert(frame, cols=120)
    _, w = indices.shape
    assert w == 120
    assert indices.shape[0] > 0
