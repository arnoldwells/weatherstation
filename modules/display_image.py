def show_image(image, background):                                                      # show artimage, slideshow or inky
    import random
    import logging
    import requests
    from PIL import Image
    from inky.auto import auto
    
    logger = logging.getLogger(__name__)
    logger.info(f"* * * showing image: {image} with {background} background")
    
    BCOLOR = 1                                                                          # white border # bcolor = 0 # black border
    SATURATION = 0.6                                                                    # 0.5 default
    inky = auto(ask_user=True, verbose=True)
    # resolution = (576, 448)                                                           # resolution = inky.resolution # (600, 448)
    x, y = 24, 0
    main_image = Image.open(f"backgrounds/{background}.png")
    
    if "https" in image:
        try: im = Image.open(requests.get(image, stream=True).raw)
        except: im = Image.open("images/slideshow-error.png")
    else: im = Image.open(image)

    if "inky" in image: x, y = random.randrange(600 - 36), random.randrange(448 - 74)   # show inky in random position at night                                    
    
    main_image.paste(im, (x, y))

    # image.resize(resolution)

    inky.set_image(main_image, saturation=SATURATION)
    inky.set_border(BCOLOR)
    inky.show()
    logger.info("done inky.show")
