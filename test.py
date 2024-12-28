#The image should be in png and the text should b clear
import pytesseract
from PIL import Image

# Update with the correct path to your tesseract executable
pytesseract.pytesseract.tesseract_cmd ="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Open the image
img = Image.open('img1.png')
img_2 = Image.open('img2.png')
# im=img.convert('L')
# im.show() 
# img_3 = Image.open('img3.png')

# Extract text from the image
text = pytesseract.image_to_string(img)
text_2 = pytesseract.image_to_string(img_2)
# text_3 = pytesseract.image_to_string(img_3)

# Print the extracted text
print(text)
print(text_2)
# print(text_3)
