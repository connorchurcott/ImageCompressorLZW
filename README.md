<h1>BMP Image Parser & LZW Compressor<h1/>
A Python desktop application for loading, processing, and compressing BMP images using a hand-implemented LZW compression algorithm.
Features

Parses BMP files at the binary level, supporting 1, 4, 8, and 24-bit images with manual header and pixel decoding
LZW compression and decompression with dynamic dictionary growth up to 16-bit code limits (65,536 entries)
Custom .cmpt369 compressed file format with a structured binary header
RGB channel toggling (isolate or remove R, G, B independently)
Brightness adjustment via RGB → YUV → RGB conversion
Nearest-neighbour image scaling
Displays original and compressed/decompressed images side by side with compression ratio and timing stats

How to Run
bashpip install pillow
python main.py
Implementation Notes

BMP pixel data is stored bottom-to-top per the spec — this is handled during parsing
LZW dictionary is capped at 2^16 entries to match the 2-byte code storage in the compressed format
Brightness adjustment is done in YUV colour space to modify luminance independently of chrominance
