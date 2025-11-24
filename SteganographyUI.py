import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
from Crypto.Cipher import AES
from sympy import randprime
import numpy as np
from numpy import binary_repr
import cv2 as cv
import math
from hashlib import pbkdf2_hmac
import struct

class SteganographyUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography Tool")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Variables
        self.selected_image = None
        self.selected_file = None
        self.selected_encoded_image = None
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create Encode, Decode, and Compare tabs
        self.encode_frame = ttk.Frame(self.notebook)
        self.decode_frame = ttk.Frame(self.notebook)
        self.compare_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.encode_frame, text='Encode')
        self.notebook.add(self.decode_frame, text='Decode')
        self.notebook.add(self.compare_frame, text='Compare')
        
        self.setup_encode_tab()
        self.setup_decode_tab()
        self.setup_compare_tab()
    
    def setup_encode_tab(self):
        """Setup the encoding tab UI"""
        # Title
        title = ttk.Label(self.encode_frame, text="Hide Message in Image", 
                         font=('Arial', 14, 'bold'))
        title.pack(pady=20)
        
        # Image selection
        image_frame = ttk.Frame(self.encode_frame)
        image_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(image_frame, text="Select Image:").pack(side='left')
        self.image_label = ttk.Label(image_frame, text="No image selected", 
                                     foreground='gray')
        self.image_label.pack(side='left', padx=10)
        
        ttk.Button(image_frame, text="Browse", 
                  command=self.browse_image).pack(side='right')
        
        # File selection
        file_frame = ttk.Frame(self.encode_frame)
        file_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(file_frame, text="Select File to Hide:").pack(side='left')
        self.file_label = ttk.Label(file_frame, text="No file selected", 
                                    foreground='gray')
        self.file_label.pack(side='left', padx=10)
        
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_file).pack(side='right')
        
        # Password entry
        password_frame = ttk.Frame(self.encode_frame)
        password_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(password_frame, text="Encryption Password:").pack(side='left')
        self.password_entry = ttk.Entry(password_frame, show='*', width=30)
        self.password_entry.pack(side='left', padx=10)
        
        # Encode button
        encode_btn = ttk.Button(self.encode_frame, text="Encode Message", 
                               command=self.encode_message,
                               style='Accent.TButton')
        encode_btn.pack(pady=30)
        
        # Status label
        self.encode_status = ttk.Label(self.encode_frame, text="", 
                                      foreground='green')
        self.encode_status.pack(pady=5)
    
    def setup_decode_tab(self):
        """Setup the decoding tab UI"""
        # Title
        title = ttk.Label(self.decode_frame, text="Extract Hidden Message", 
                         font=('Arial', 14, 'bold'))
        title.pack(pady=20)
        
        # Image selection
        decode_image_frame = ttk.Frame(self.decode_frame)
        decode_image_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(decode_image_frame, text="Select Encoded Image:").pack(side='left')
        self.decode_image_label = ttk.Label(decode_image_frame, 
                                           text="No image selected", 
                                           foreground='gray')
        self.decode_image_label.pack(side='left', padx=10)
        
        ttk.Button(decode_image_frame, text="Browse", 
                  command=self.browse_encoded_image).pack(side='right')
        
        # Encoding key entry
        key_frame = ttk.Frame(self.decode_frame)
        key_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(key_frame, text="Encoding Key:").pack(side='left')
        self.key_entry = ttk.Entry(key_frame, width=30)
        self.key_entry.pack(side='left', padx=10)
        
        # Password entry
        decode_password_frame = ttk.Frame(self.decode_frame)
        decode_password_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(decode_password_frame, text="Decryption Password:").pack(side='left')
        self.decode_password_entry = ttk.Entry(decode_password_frame, show='*', width=30)
        self.decode_password_entry.pack(side='left', padx=10)
        
        # Decode button
        decode_btn = ttk.Button(self.decode_frame, text="Decode Message", 
                               command=self.decode_message,
                               style='Accent.TButton')
        decode_btn.pack(pady=30)
        
        # Status label
        self.decode_status = ttk.Label(self.decode_frame, text="", 
                                      foreground='green')
        self.decode_status.pack(pady=5)
    
    def setup_compare_tab(self):
        """Setup the image comparison tab UI"""
        # Title
        title = ttk.Label(self.compare_frame, text="Compare Original and Encoded Images", 
                         font=('Arial', 14, 'bold'))
        title.pack(pady=20)
        
        # Original image selection
        original_frame = ttk.Frame(self.compare_frame)
        original_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(original_frame, text="Original Image:").pack(side='left')
        self.compare_original_label = ttk.Label(original_frame, 
                                               text="No image selected", 
                                               foreground='gray')
        self.compare_original_label.pack(side='left', padx=10)
        
        ttk.Button(original_frame, text="Browse", 
                  command=self.browse_original_compare).pack(side='right')
        
        # Encoded image selection
        encoded_frame = ttk.Frame(self.compare_frame)
        encoded_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(encoded_frame, text="Encoded Image:").pack(side='left')
        self.compare_encoded_label = ttk.Label(encoded_frame, 
                                              text="No image selected", 
                                              foreground='gray')
        self.compare_encoded_label.pack(side='left', padx=10)
        
        ttk.Button(encoded_frame, text="Browse", 
                  command=self.browse_encoded_compare).pack(side='right')
        
        # Compare button
        compare_btn = ttk.Button(self.compare_frame, text="Compare Images", 
                                command=self.compare_images,
                                style='Accent.TButton')
        compare_btn.pack(pady=20)
        
        # Status label
        self.compare_status = ttk.Label(self.compare_frame, text="", 
                                       foreground='green')
        self.compare_status.pack(pady=5)
    
    def browse_original_compare(self):
        """Browse for original image to compare"""
        filename = filedialog.askopenfilename(
            title="Select Original Image",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.compare_original_image = filename
            self.compare_original_label.config(text=os.path.basename(filename), 
                                              foreground='black')
    
    def browse_encoded_compare(self):
        """Browse for encoded image to compare"""
        filename = filedialog.askopenfilename(
            title="Select Encoded Image",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.compare_encoded_image = filename
            self.compare_encoded_label.config(text=os.path.basename(filename), 
                                             foreground='black')
    
    def compare_images(self):
       """Compare logic goes here"""
       
    def browse_image(self):
        """Browse for image to encode"""
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.selected_image = filename
            self.image_label.config(text=os.path.basename(filename), 
                                   foreground='black')
    
    def browse_file(self):
        """Browse for file to hide"""
        filename = filedialog.askopenfilename(
            title="Select File to Hide",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.selected_file = filename
            self.file_label.config(text=os.path.basename(filename), 
                                  foreground='black')
    
    def browse_encoded_image(self):
        """Browse for encoded image to decode"""
        filename = filedialog.askopenfilename(
            title="Select Encoded Image",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.selected_encoded_image = filename
            self.decode_image_label.config(text=os.path.basename(filename), 
                                          foreground='black')
    
    def encrypt(self, file, encryptionKey):
        """Encrypt file content - from ImageEncoder.py"""
        salt = os.urandom(16) #need a salt to ensure secure encryption against rainbow tables
    
        key32 = pbkdf2_hmac(   #AES requires a 32 bit key, so we use sha256 hash function
            hash_name="sha256",
            password=encryptionKey.encode(),
            salt=salt,
            iterations=100_000,
            dklen=32
            )
    
        with open(file, "rb") as f: #read the file byte by byte
            plaintext = f.read()
    
        cipher = AES.new(key32, AES.MODE_GCM) #make the cipher based on the 32 bit key
        ciphertext, tag = cipher.encrypt_and_digest(plaintext) #encrypt the plaintext, tag is for integrity assurance
        nonce = cipher.nonce
    
        header = struct.pack(">I", len(ciphertext))
        binary_blob = salt + nonce + tag + header + ciphertext #puts all the encryption information except the password into the beginning of cipher
        bit_string = ''.join(f"{byte:08b}" for byte in binary_blob) #converts the bytes to just 0 and 1s
        #print(bit_string)
    
        return bit_string
    
    def encodeImage(self, imagePath, binaryFile, output_path="encoded_image.png"):
        """Encode binary data into image - adapted from ImageEncoder.py"""
        img = cv.imread(imagePath)
        if img is None:
            raise ValueError("Invalid image path")
        
        rows, columns, channels = img.shape
        totalVals = rows * columns * channels
        
        # Check if message fits
        if len(binaryFile) > totalVals:
            raise ValueError(f"Message too large! Image can hold {totalVals} bits, but message is {len(binaryFile)} bits.")
        
        stepKey = randprime(6, 1000)
        while math.gcd(stepKey, totalVals) != 1: #checks to make sure the key is coprime, to ensure each pixel will only be accessed once
            stepKey = randprime(6, 1000)
        
        valueDict = {}
        count = 0
        for px in range(0, rows): #puts each BGR value into a corresponding key, left to right, top to bottom
            for px2 in range(0, columns):
                for value in range(0, channels):
                    valueDict[count] = [px, px2, value]
                    count += 1
        
        steppedDict = {}
        keyList = list(valueDict.keys())    
        visitedCount = 0
        index = 0
        
        while visitedCount < len(keyList): #creates the steppedDict, which uses the prime step
            key = keyList[index % len(keyList)]
            if key not in steppedDict:
                steppedDict[key] = valueDict[key]
                index += stepKey
                visitedCount += 1
            else:
                break
            
        for i in range(totalVals):
            if i not in steppedDict: #double checks to make sure there aren't any keys missing from steppedDict
                print("Missing key: ", i)
        
        steppedKeyList = list(steppedDict.keys())
        
        charIndex = 0
        for char in binaryFile:
            #print("Message char: ", char)
            r, c, ch = steppedDict[steppedKeyList[charIndex]]
            string = binary_repr(img[r, c, ch], 8)
            checkValue = string[7]
            #print("Image values: ", img[r, c])
            #print("Last digit of Pixel: ", string[7])
            if char == checkValue:
                #print("Char == checkValue")
                pass
            else:
                #print("Char != checkValue")
                #print("Old String: ", string)
                val = img[r, c, ch]
                if val == 255:
                    img[r, c, ch] = val - 1
                    #print("Value: ", val)
                    #print("New String: ", binary_repr(img[r, c, ch], 8))
                else:
                    img[r, c, ch] = val + 1
                    #print("Value: ", val)
                    #print("New String: ", binary_repr(img[r, c, ch], 8))
            charIndex += 1
        
        cv.imwrite(output_path, img, [cv.IMWRITE_PNG_COMPRESSION, 0])
        
        return stepKey
    
    def encode_message(self):
        """Handle encode button click"""
        self.encode_status.config(text="")
        
        # Validate inputs
        if not self.selected_image:
            messagebox.showerror("Error", "Please select an image")
            return
        
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file to hide")
            return
        
        password = self.password_entry.get()
        if not password:
            messagebox.showerror("Error", "Please enter an encryption password")
            return
        
        try:
            # Encrypt the file
            binary_data = self.encrypt(self.selected_file, password)
            
            # Encode into image
            output_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                title="Save Encoded Image As"
            )
            
            if not output_path:
                return
            
            step_key = self.encodeImage(self.selected_image, binary_data, output_path)
            
            # Save key info
            info_path = output_path.rsplit('.', 1)[0] + "_info.txt"
            with open(info_path, "w") as f:
                f.write(f"Encoding Key: {step_key}\n")
                f.write(f"Encoded Image: {os.path.basename(output_path)}\n")
                f.write(f"Original File: {os.path.basename(self.selected_file)}")
            
            messagebox.showinfo("Success", 
                              f"Message encoded successfully!\n\n"
                              f"Encoded image: {os.path.basename(output_path)}\n"
                              f"Encoding key: {step_key}\n\n"
                              f"Key saved to: {os.path.basename(info_path)}\n\n"
                              f"Keep the key and password safe!")
            
            self.encode_status.config(text=f"✓ Encoded successfully! Key: {step_key}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Encoding failed: {str(e)}")
    
    def decode_message(self):
        """Handle decode button click"""
        self.decode_status.config(text="")
        
        # Validate inputs
        if not self.selected_encoded_image:
            messagebox.showerror("Error", "Please select an encoded image")
            return
        
        key = self.key_entry.get()
        if not key:
            messagebox.showerror("Error", "Please enter the encoding key")
            return
        
        password = self.decode_password_entry.get()
        if not password:
            messagebox.showerror("Error", "Please enter the decryption password")
            return
        
        ## Decoder logic goes here vvvvvvv
        ## try:
            


def main():
    try:
        root = tk.Tk()
        app = SteganographyUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting UI: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    print("Starting Steganography UI...")
    main()
