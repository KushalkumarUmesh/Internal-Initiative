from PIL import Image

# ascii characters used to build the output text
#ASCII_CHARS = ["@","#","S","%","?","*","+",";",":",",","."]
ASCII_CHARS = chars = ["B","S","#","&","@","$","%","*","!",":","."] # ["@","#","s","%","?","*",".","+",":",",","+"]

#resize image according to a new width
def resize_image(image, new_width=100):
    width,height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return(resized_image)

#covert each pixel to greyscale
def greyfy(image):
    grescale_image = image.convert("L")
    return(grescale_image)

#convert pixels to a string of ASCCII characters
def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel//25] for pixel in pixels])
    return(characters)

def main(new_width=100):
    #attempt to open the image with user input
    path = input("Enter a valid pathname to an image:\n")
    try:
        image = Image.open(path)
    except:
        print(path,"is not a valid pathname to an image")   

    #convert image to ASCII
    new_image_data = pixels_to_ascii(greyfy(resize_image(image)))

    # format
    pixel_count = len(new_image_data)
    ascii_image = "\n".join(new_image_data[i:(i+new_width)] for i in range(0,pixel_count,new_width))     

    #print result
    print(ascii_image)

    #save result to "ascii_image.txt"
    with open("ascii_image.txt","w") as f:
        f.write(ascii_image) 

main()        