import tkinter as tk 
import struct
import os
import time
from tkinter import filedialog
from PIL import Image, ImageTk

# RootWindow completley sets up the application window so main can just create an object of this later
class RootWindow(tk.Tk):

    def __init__(self):
        self.pixelMap = None
        self.redToggledOff = False
        self.greenToggledOff = False
        self.blueToggledOff = False
        self.curBrightness = 50
        self.curScale = 50

        super().__init__() 
        self.styling()
        self.sizing()
        self.widgets()


    # Window Configuration Methods
    def styling(self): 
        self.title("Image App")
        self.configure(background="gray14")

    def sizing(self): 
        self.minsize(1500, 800)
        self.maxsize(1500, 800)

    def widgets(self): 
        self.browseFilesBtn = tk.Button(self, text="Browse Files", command=self.browse_files).grid(row=1, column=0, padx=(0, 40))
        self.redButton = tk.Button(self, text="Toggle Red", command=self.toggle_red).grid(row=0, column=1)
        self.greenButton = tk.Button(self, text="Toggle Green", command=self.toggle_green).grid(row=0, column=2)
        self.blueButton = tk.Button(self, text="Toggle Blue", command=self.toggle_blue).grid(row=0, column=3, padx=(0, 40))

        self.brightnessSlider = tk.Scale(self, from_=0, to=100, orient="horizontal", label="Adjust Brightness", command=self.adjust_brightness)
        self.brightnessSlider.grid(row=0, column=4, columnspan=1, padx=(0, 20))
        self.brightnessSlider.set(self.curBrightness)

        self.scaleSlider = tk.Scale(self, from_=0, to=100, orient="horizontal", label="Adjust Scale", command=self.adjust_scale)
        self.scaleSlider.grid(row=0, column=6, columnspan=1, padx=(0, 20))
        self.scaleSlider.set(self.curScale)

        self.fileSize = 0
        self.fileSizeTK = tk.StringVar()
        self.fileSizeTK.set(f"File Size: {self.fileSize}")
        tk.Label(self, textvariable=self.fileSizeTK).grid(row=0, column=8, padx=(0, 10))

        self.imgWidth = 0
        self.imgWidthTK = tk.StringVar()
        self.imgWidthTK.set(f"Image Width: {self.imgWidth}")
        tk.Label(self, textvariable=self.imgWidthTK).grid(row=0, column=9, padx=(0, 10))

        self.imgHeight = 0
        self.imgHeightTK = tk.StringVar()
        self.imgHeightTK.set(f"Image Height: {self.imgHeight}")
        tk.Label(self, textvariable=self.imgHeightTK).grid(row=0, column=10, padx=(0, 10))

        self.bitsPerPixel = 0
        self.bitsPerPixelTK = tk.StringVar()
        self.bitsPerPixelTK.set(f"Bits Per Pixel: {self.bitsPerPixel}")
        tk.Label(self, textvariable=self.bitsPerPixelTK).grid(row=0, column=11, padx=(0, 10))

        tk.Label(self, text="File Selected: ").grid(row=1, column=1, sticky="w", padx=(0, 0))
        self.selectedImg = ""
        self.selectedImgTK = tk.StringVar()
        self.selectedImgTK.set("")
        tk.Label(self, textvariable=self.selectedImgTK, wraplength=500, justify="left").grid(row=1, column=2, columnspan=5, pady=50, sticky="w", padx=(0, 20))

        self.imageFrame = tk.Frame(self, width=600, height=500, highlightbackground="white", highlightthickness=2, bd=0)
        self.imageFrame.grid(row=2, column=0, columnspan=10, rowspan=10, padx=20, pady=20, sticky="nw")
        self.imageFrame.grid_propagate(False)  
        self.imageFrame.pack_propagate(False)
        self.imageLabel = tk.Label(self.imageFrame, bg="gray22", fg="white", text="No image loaded", anchor="center", justify="center", wraplength=480)
        self.imageLabel.pack(expand=True, fill="both")

        # Stuff added in PA2 
        self.compressBtn = tk.Button(self, text="Compress", command=self.on_compress_button_hit) #ensure this gets threaded later
        self.compressBtn.grid(row=1, column=7, padx=5)

        self.decompressBtn = tk.Button(self, text="Decompress", command=self.on_decompress_button_hit) 
        self.decompressBtn.grid(row=1, column=8, padx=5)

        self.imageFrameCompressed = tk.Frame(self, width=600, height=500, highlightbackground="white", highlightthickness=2, bd=0)
        self.imageFrameCompressed.grid(row=2, column=6, columnspan=10, rowspan=10, padx=20, pady=20, sticky="nw")
        self.imageFrameCompressed.grid_propagate(False)
        self.imageFrameCompressed.pack_propagate(False)
        self.imageLabelCompressed = tk.Label(self.imageFrameCompressed, bg="gray22", fg="white", text="No image compressed / decompressed", anchor="center", justify="center", wraplength=480)
        self.imageLabelCompressed.pack(expand=True, fill="both")


        self.originalFileSizeTK = tk.StringVar()
        self.originalFileSizeTK.set(f"Original BMP File Size: {self.fileSize}")
        tk.Label(self, textvariable=self.originalFileSizeTK).grid(row=12, column=0, padx=(10, 10))

        self.compressedFileSize = 0
        self.compressedFileSizeTK = tk.StringVar()
        self.compressedFileSizeTK.set(f"Compressed File Size: {self.compressedFileSize}")
        tk.Label(self, textvariable=self.compressedFileSizeTK).grid(row=12, column=1, padx=(0, 10))

        self.compressionRatio = 0
        self.compresseionRatioTK = tk.StringVar()
        self.compresseionRatioTK.set(f"Compression Ratio: {self.compressionRatio}")
        tk.Label(self, textvariable=self.compresseionRatioTK).grid(row=12, column=2, padx=(0, 10))

        self.compressionTime = 0
        self.compressionTimeTK = tk.StringVar()
        self.compressionTimeTK.set(f"Compression Time: {self.compressionTime}")
        tk.Label(self, textvariable=self.compressionTimeTK).grid(row=12, column=3, padx=(0, 0))


    # Button Press & Slider methods
    def browse_files(self): 
        filename = filedialog.askopenfilename()

        # if a files is selected, update filename, check if file is valid, if valid then process the data
        if filename: 
            fileByteStream = read_image_as_byte_stream(filename)

            # check file signature and make sure it is bmp
            fileSignature = get_file_signature(fileByteStream)
            print(f"Signature: {fileSignature}")

            if fileSignature == b'C3': 
                self.imageLabel.config(text="Selected a .cmpt369 file. Decompress to view", image="")
                self.selectedImg = os.path.basename(filename)
                self.selectedImgTK.set(f"{self.selectedImg}")
                return
            
            if fileSignature != b'BM':
                self.imageLabel.config(text="Input file chosen is not of type BMP", image="")
                self.selectedImg = filename
                self.selectedImgTK.set(f"{self.selectedImg}")
                return
            
            self.selectedImg = os.path.basename(filename); 
            self.selectedImgTK.set(f"{self.selectedImg}")

            # parse meta data
            self.parse_meta_data_and_set_labels(fileByteStream)

            self.pixelMap = parse_pixel_map(fileByteStream, self.bitsPerPixel, self.imgWidth, self.imgHeight)
            generatedImg = generate_img(self.pixelMap)
            self.imageLabel.config(image=generatedImg, text="")
            self.imageLabel.image = generatedImg  
    

    def toggle_red(self):
        self.redToggledOff = not self.redToggledOff
        self.update_image_with_toggled_rgb()
    
    def toggle_green(self):
        self.greenToggledOff = not self.greenToggledOff
        self.update_image_with_toggled_rgb()
    
    def toggle_blue(self):
        self.blueToggledOff = not self.blueToggledOff
        self.update_image_with_toggled_rgb()

    def adjust_brightness(self, val): 
        if self.pixelMap == None: 
            return

        newBrightness = self.brightnessSlider.get() / 100
        ogImg = self.pixelMap
        width = self.imgWidth
        height = self.imgHeight

        modedPixels = []
        for i in range (height):
            modedRow = []

            for j in range(width):
                r, g, b = ogImg[i][j]

                # convert to yuv 
                y = 0.299 * r + 0.587 * g + 0.114 * b
                u = -0.299 * r + -0.587 * g + 0.886 * b
                v = 0.701 * r + -0.587 * g + -0.114 * b

                y *= newBrightness

                # convert back to rgb 
                rNew = y + 1.13983 * v 
                gNew = y + -0.39465 * u + -0.58060 * v
                bNew = y + 2.03211 * u

                # clamp
                rNew = max(0, min(255, rNew))
                gNew = max(0, min(255, gNew))
                bNew = max(0, min(255, bNew))

                modedRow.append((int(rNew), int(gNew), int(bNew)))
            modedPixels.append(modedRow)
        
        modedImg = generate_img(modedPixels)
        self.imageLabel.config(image=modedImg, text="")
        self.imageLabel.image = modedImg


    def adjust_scale(self, value):
        if self.pixelMap == None: 
            return
        
        newScale = self.scaleSlider.get() / 100
        ogImg = self.pixelMap
        width = self.imgWidth
        height = self.imgHeight

        newWidth = int(width * newScale)
        newHeight = int(height * newScale)

        modedPixels = []
        for i in range(newHeight):
            modedRow = []
            
            for j in range(newWidth):

                ogI = int(i / newScale)
                ogJ = int(j / newScale)

                ogI = min(ogI, height - 1)
                ogJ = min(ogJ, width - 1)

                modedRow.append(ogImg[ogI][ogJ])
            modedPixels.append(modedRow)
        
        modedImg = generate_img(modedPixels)
        self.imageLabel.config(image=modedImg, text="")
        self.imageLabel.image = modedImg

    # Main Methods Added for PA2
    def compress_lzw(self): 

        BYTE_CAP = 2**16 # i'm capping the dictionary size at this because I am storing 2 bytes of LWZ data in the save_as_cmpt365 function later on 

        if self.selectedImg == "":
            return

        dictionarySize = 256
        dictionary = {}
        for i in range(dictionarySize):
            dictionary[bytes([i])] = i
        

        rgbBytes = convert_pixels_to_bytes(self.pixelMap)

        currentSequence = b""
        result = []

        # go through each byte, check if the curPlusNext sequence is in it already. if yes then extend it. if no then add it if theres space
        for curByte in rgbBytes: 
            curPlusNext = currentSequence + bytes([curByte])
            if curPlusNext in dictionary:
                currentSequence = curPlusNext
            else:
                result.append(dictionary[currentSequence])
                if dictionarySize < BYTE_CAP: 
                    dictionary[curPlusNext] = dictionarySize
                    dictionarySize += 1
                currentSequence = bytes([curByte])
        
        if currentSequence: 
            result.append(dictionary[currentSequence])

        return result

    def on_compress_button_hit(self):

        startTime = time.time()
        compressedData = self.compress_lzw()
        endTime = time.time()

        # pipeline: save as .cmpt365 -> load the same .cmpt365 file -> decompress it -> convert it to pixels -> display it 
        newFileName = self.selectedImg + ".cmpt365"
        save_as_cmpt365(newFileName, compressedData, self.imgWidth, self.imgHeight, self.bitsPerPixel)

        codes, width, height, bitsPerPixel = load_cmpt365_file("./compressed imgs/" + newFileName)
        decompressedBytes = self.decompress_lzw(codes)
        pixels = convert_bytes_to_pixels(decompressedBytes, width, height)

        generatedCompressedImg = generate_img(pixels)
        self.imageLabelCompressed.config(image=generatedCompressedImg, text="")
        self.imageLabelCompressed.image = generatedCompressedImg 

        # then set the 4 specs at the bottom 
        self.originalFileSizeTK.set(f"Original BMP File Size: {self.fileSize}")

        self.compressedFileSize = os.path.getsize("./compressed imgs/" + newFileName)
        self.compressedFileSizeTK.set(f"Compressed File Size: {self.compressedFileSize}")

        self.compressionRatio = round(self.fileSize / self.compressedFileSize, 4)
        self.compresseionRatioTK.set(f"Compression Ratio: {self.compressionRatio}")

        self.compressionTime = round(endTime - startTime, 4)
        self.compressionTimeTK.set(f"Compression Time: {self.compressionTime}")




    def decompress_lzw(self, compressed):

        dictionarySize = 256 
        dictionary = {}
        for i in range(dictionarySize):
            dictionary[i] = bytes([i])

        result = []

        previousDecode = bytes([compressed[0]])
        result.extend(previousDecode)

        # go through all codes in compressed, exapand, and put into a result. 
        for curCode in compressed[1:]:
            if curCode in dictionary: 
                entry = dictionary[curCode]
            elif curCode == dictionarySize: 
                entry = previousDecode + previousDecode[:1]
            else: 
                print("error in decompress_lzw")
            
            result.extend(entry)

            dictionary[dictionarySize] = previousDecode + entry[:1]
            dictionarySize += 1
            previousDecode = entry

        return result
    
    def on_decompress_button_hit(self): 

        # just needs to fetch the currently selected .cmpt365 image then dispaly it just like the on compress button hit

        print(self.selectedImg)
        codes, width, height, bitsPerPixel = load_cmpt365_file("./compressed imgs/" + self.selectedImg)
        decompressedBytes = self.decompress_lzw(codes)
        pixels = convert_bytes_to_pixels(decompressedBytes, width, height)

        generatedCompressedImg = generate_img(pixels)
        self.imageLabelCompressed.config(image=generatedCompressedImg, text="")
        self.imageLabelCompressed.image = generatedCompressedImg 




        


    # Helper Methods
    def parse_meta_data_and_set_labels(self, fileByteStream): # obtains and sets the required meta data components
        cur_file_size = get_file_size(fileByteStream)
        self.fileSize = cur_file_size
        self.fileSizeTK.set(f"File Size: {self.fileSize}")

        cur_file_width = get_file_width(fileByteStream)
        self.imgWidth = cur_file_width
        self.imgHeightTK.set(f"Image Width: {self.imgWidth}")

        cur_file_height = get_file_height(fileByteStream)
        self.imgHeight = cur_file_height
        self.imgWidthTK.set(f"Image Height: {self.imgHeight}")

        cur_file_bits_per_pixel = get_file_bits_per_pixel(fileByteStream)
        self.bitsPerPixel = cur_file_bits_per_pixel
        self.bitsPerPixelTK.set(f"Bits Per Pixel: {self.bitsPerPixel}")  
    
    def update_image_with_toggled_rgb(self): # handels the toggleing and changing image of r g b buttons
        if self.pixelMap == None: 
            return 

        modedPixels = []
        for row in self.pixelMap:
            modedRow = []

            for red, green, blue in row: 
                if self.redToggledOff is True: 
                    r = 0
                else: 
                    r = red
                
                if self.greenToggledOff is True: 
                    g = 0
                else: 
                    g = green
                
                if self.blueToggledOff is True: 
                    b = 0
                else: 
                    b = blue

                modedRow.append((r, g, b))
            modedPixels.append(modedRow)
        
        modedImg = generate_img(modedPixels)
        self.imageLabel.config(image=modedImg, text="")
        self.imageLabel.image = modedImg





# Obtain Meta Data Functions
def read_image_as_byte_stream(image):
    with open(image, "rb") as f: 
        bmp_bytes = f.read()

    return bmp_bytes 

def get_file_signature(bmp_bytes): 
    signature = bmp_bytes[0:2]
    return signature

def get_file_size(bmp_bytes): 
    value = int.from_bytes(bmp_bytes[2:6], 'little')
    return value

def get_file_width(bmp_bytes): 
    value = int.from_bytes(bmp_bytes[18:22], 'little')
    return value

def get_file_height(bmp_bytes): 
    value = int.from_bytes(bmp_bytes[22:26], 'little')
    return value

def get_file_bits_per_pixel(bmp_bytes): 
    value = int.from_bytes(bmp_bytes[28:30], 'little')
    return value


def parse_palette(bmp_bytes, bitsPerPixel): # loads pallette information into an array so 1, 4, 8 bitsPerPixel images can refer to it later
    palette = []
    numColors = 2 ** bitsPerPixel

    for i in range(numColors):
        start = 54 + i * 4
        blue = bmp_bytes[start]
        green = bmp_bytes[start + 1]
        red = bmp_bytes[start + 2]
        
        palette.append((red, green, blue))
    
    return palette

def parse_pixel_map(bmp_bytes, bitsPerPixel, width, height): 
    pixels = []

    bytesPerRow = ((width * bitsPerPixel + 31) // 32) * 4
    offset = int.from_bytes(bmp_bytes[10:14], 'little')

    if bitsPerPixel <= 8: # only calculate palette if its needed for 1 4 or 8 sized imgs
        palette = parse_palette(bmp_bytes, bitsPerPixel)

    for row in range(height):
        rowPixels = []
        rowStart = offset + (height - row - 1) * bytesPerRow # start at end of pixel data because img is stored from bottom to top

        if bitsPerPixel == 24: # 3 bytes represent 1 pixel
            for col in range(width):
                i = rowStart + col * 3
                blue = bmp_bytes[i]
                green = bmp_bytes[i + 1]
                red = bmp_bytes[i + 2]
                rowPixels.append((red, green, blue))
        
        elif bitsPerPixel == 8: # each byte represents 1 pixel
            for col in range(width):
                i = bmp_bytes[rowStart + col]
                rowPixels.append(palette[i])

        elif bitsPerPixel == 4:  # each byte represents 2 pixels, 4 bits each
            for col in range(width): 
                i = rowStart + (col // 2)
                byte = bmp_bytes[i]

                if col % 2 == 0: 
                    i = (byte // 16) % 16
                else: 
                    i = byte % 16
                
                rowPixels.append(palette[i])

        elif bitsPerPixel == 1: # each bit represents a pixel 
            for col in range(width): 
                i = rowStart + (col // 8)
                byte = bmp_bytes[i]
                bitIndex = 7 - (col % 8)

                mask = 2 ** bitIndex
                val = (byte // mask) % 2

                rowPixels.append(palette[val])

    
        pixels.append(rowPixels)
    
    return pixels

def generate_img(pixels): # reads my parsed bitmap data and displays each byte using PIL library
    height = len(pixels)
    width = len(pixels[0])

    img = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            img.putpixel((x, y), pixels[y][x])
    
    return ImageTk.PhotoImage(img)

#Added for PA2
def convert_pixels_to_bytes(pixelmap): 
    byteArray = []

    for row in pixelmap: 
        for r, g, b in row: 
            byteArray.extend([r, g, b])

    return bytes(byteArray)

def convert_bytes_to_pixels(byteStream, width, height): 
    pixels = []
    i = 0 

    for y in range(height): 
        row = []
        for x in range(width):
            r = byteStream[i]
            g = byteStream[i + 1]
            b = byteStream[i + 2]
            
            row.append((r, g, b))
            i += 3
        pixels.append(row)

    return pixels



def save_as_cmpt365(filename, compressed, width, height, bitsPerPixel): 
    with open("./compressed imgs/" + filename, "wb") as newFile: 
        
        # Schema for header: 2 Bytes for C3 identifier, 1 byte for bitsPerPixel, 2 bytes for width, 2 bytes for height thus 7 bytes total
        header = struct.pack('<2sBHH', b'C3', bitsPerPixel, width, height)
        newFile.write(header)

        for i in compressed: 
            newFile.write(struct.pack('<H', i))

    return 

def load_cmpt365_file(filename): 
    with open(filename, "rb") as file: 
        header = file.read(7)
        id, bitsPerPixel, width, height = struct.unpack('<2sBHH', header)

        if id != b"C3": 
            print("Error in load_cmpt_file: input file is not of type .cmpt365")
            return

        compressed_data = file.read()

        codes = []

        for i in range(0, len(compressed_data), 2):
            twoBytes = compressed_data[i:i+2]
            value = struct.unpack('<H', twoBytes)[0]
            codes.append(value)

        return codes, width, height, bitsPerPixel




        
        
    



    











# -------------- Main loop --------------


def main():
    root = RootWindow()
    root.mainloop()
    


if __name__ == "__main__": 
    main()