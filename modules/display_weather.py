import math
import logging
from data.env import (
    DEBUG, 
    RED, BLUE, BLACK, GREEN, WHITE, ORANGE, 
    BCOLOR, BACKGROUND, SATURATION, WEATHER_CODES, 
    FONT_TH, FONT_TI, FONT_TJ, FONT_SM,  FONT_LG,
    RAD, INNER_ARC_RAD, RADIAL_RAD, TEMP_RAD, RADIAL_WIDTH
)
from PIL import Image, ImageDraw
from inky.auto import auto
from datetime import datetime, timedelta
from modules.pastebin import get_birthday_list

logger = logging.getLogger(__name__)

def rotate_coords(image, x, y):                                                         # for rotating inky & wind direction icon
    (new_width, new_height) = image.size
    return (x - int((new_width - 28) / 2),
            y - int((new_height - 28) / 2))

def coords(image, x, y):                                                                # objects distributed around the circle
    (new_width, new_height) = image.size
    return (x - int(new_width / 2),
            y - int(new_height / 2))

def draw_source_icon(image, weather_source):
    logger.info(f"{weather_source}")
    icon_file = f"images/{weather_source[-1]}.png"
    im_source = Image.open(icon_file)
    image.paste(im_source, (46, 318))

def draw_four_day(image, draw, forecast):
    x, y = 45, 379
    for day in range(1, 5):
        min = forecast['daily'][day]['temp']['min']
        max = forecast['daily'][day]['temp']['max']
        id = forecast['daily'][day]['weather'][0]['id']
        try: code = WEATHER_CODES[f"{id}d"]                                             # lookup day version code from weather dictionary
        except:
            code = "000"
            logger.error(f"code not found: {id}")
        icon_filename = f"weather/{code}.png"
        im_weather = Image.open(icon_filename)                                          
        image.paste(im_weather, (x, y), im_weather)
        draw.text((x + 65, y + 8), 
                  "%0.0f°" % max, 
                  anchor="lt", 
                  font=FONT_TI, 
                  fill=BLACK)
        draw.text((x + 65, y + 30), 
                  "%0.0f°" % min, 
                  anchor="lt", 
                  font=FONT_TI, 
                  fill=BLACK)
        x += 105

def draw_inky(image, now, rain):
    x, y = 215, 165
    now_seconds = (now - now.replace(hour=0, minute=0, second=0)).total_seconds()       # seconds since midnight
    rotation = (((now_seconds % 43200) / 43200) * 360)
    inky_rotation =  360 - (int(rotation) - 15)                                         # with 15° adjustment
    if rain: inky_file = "images/inky-umbrella.png"
    else: inky_file = "images/inky-solo.png"
    im_inky = Image.open(inky_file).rotate(inky_rotation, 
                                           expand=True, 
                                           resample=Image.BICUBIC) 
    im_bubbles = Image.open("images/inky-bubbles.png")
    image.paste(im_bubbles, coords(im_bubbles, x, y))                                   # paste bubbles image
    image.paste(im_inky, coords(im_inky, x, y), im_inky)

def draw_12_hours(image, draw, current_weather):
    x, y = 215, 165
    for a in range(12):
        hour = int(datetime.fromtimestamp(current_weather.forecast['hourly'][a]['dt']).strftime("%H"))
        angle = (hour % 12) * 30
        wx = int(x + (RAD * math.sin(math.radians(angle))))                             # icon x/y
        wy = int(y - (RAD * math.cos(math.radians(angle))))
        tx = int(x + (TEMP_RAD * math.sin(math.radians(angle))))                        # temp x/y
        ty = int(y - (TEMP_RAD * math.cos(math.radians(angle))))   
        uvi = current_weather.forecast['hourly'][a]['uvi']                              # uv forecast 
        pop = current_weather.forecast['hourly'][a]['pop']                              # probability of precipitation
        temp = current_weather.forecast['hourly'][a]['temp']                            # temperature
        id = current_weather.forecast['hourly'][a]['weather'][0]['id']
        if id // 100 not in [8, 7]: current_weather.rain = True                         # forecast is for rain 8xx, 7xx # set flag for inky_umbrella
        sunset_h = int(current_weather.sunset.strftime("%H")) 
        sunrise_h = int(current_weather.sunrise_1.strftime("%I"))  
        try:
            if sunrise_h <= hour <= sunset_h:                                           # forecast hour between sunrise(tomorrow) and sunset
                code = WEATHER_CODES[f"{id}d"]                                          # set daytime code
            else:
                code = WEATHER_CODES[f"{id}n"]                                          # set nighttime code
        except:
            code = "000"
            logger.error(f"code not found: {id}")
        icon_filename = f"weather/{code}.png"
        im_weather = Image.open(icon_filename) 
        image.paste(im_weather, coords(im_weather, wx, wy), im_weather)                 # paste weather icon

        pie_end = angle - 75
        pie_start = angle - 105
        if pop >= 0.1:                                                                  # percentage of precipitation above 10%
            inner_radius = RADIAL_RAD - int(RADIAL_WIDTH * pop)
            logger.debug(f"inner_radius: {inner_radius}")           
            draw.pieslice((x - RADIAL_RAD,                                              # green segment
                           y - RADIAL_RAD, 
                           x + RADIAL_RAD, 
                           y + RADIAL_RAD), 
                          start=pie_start, 
                          end=pie_end, 
                          fill=GREEN)
            draw.pieslice((x - inner_radius,                                            # overlayed white
                           y - inner_radius, 
                           x + inner_radius, 
                           y + inner_radius), 
                          start=pie_start, 
                          end=pie_end, 
                          fill=WHITE)
            draw.arc((x - INNER_ARC_RAD,                                                # draw boundary 
                      y - INNER_ARC_RAD, 
                      x + INNER_ARC_RAD, 
                      y + INNER_ARC_RAD), 
                     start=pie_start,
                     end=pie_end,
                     fill=BLUE,
                     width=1)
        elif uvi >= 1:                                                                  # pop takes precedence over uvi
            uvi_radius = INNER_ARC_RAD + int(RADIAL_WIDTH * uvi / 9)                    # uv range set at 0 to 9
            logger.debug(f"uvi: {uvi}\tuvi_radius: {uvi_radius}")           
            draw.pieslice((x - uvi_radius,                                              # orange segment
                           y - uvi_radius, 
                           x + uvi_radius, 
                           y + uvi_radius), 
                          start=pie_start, 
                          end=pie_end, 
                          fill=ORANGE)
            draw.pieslice((x - INNER_ARC_RAD,                                           # overlayed white 
                           y - INNER_ARC_RAD, 
                           x + INNER_ARC_RAD, 
                           y + INNER_ARC_RAD), 
                          start=pie_start, 
                          end=pie_end, 
                          fill=WHITE)
            draw.arc((x - RADIAL_RAD,                                                   # draw boundary
                      y - RADIAL_RAD, 
                      x + RADIAL_RAD, 
                      y + RADIAL_RAD), 
                     start=pie_start, 
                     end=pie_end, 
                     fill=BLUE, 
                     width=1)            

        if a == 0:                                                                      # if current hour
            logger.debug("drawing current hour arc")
            arc_end = angle - 75
            arc_start = angle - 105
            draw.arc((x - RADIAL_RAD - 3, 
                      y - RADIAL_RAD - 3, 
                      x + RADIAL_RAD + 3, 
                      y + RADIAL_RAD + 3), 
                     start=arc_start, 
                     end=arc_end, 
                     fill=RED, 
                     width=4)    
        draw.text((tx, ty),                                                             # temperature  
                  "%0.0f°" % temp, 
                  anchor="mm", 
                  font=FONT_TI, 
                  stroke_width=2, 
                  stroke_fill=WHITE, 
                  fill=BLACK)
        logger.info(f"{angle}° a:{a} wx:{wx} wy:{wy} temp:{temp} hour:{hour}:00 pop:{pop} id:{id} code:{code} filename:{icon_filename}")           

def draw_birthday_list(image, draw):
    x, y = 364, 2
    for days, name, icon in get_birthday_list():
        im_days = Image.open(icon)
        image.paste(im_days, (x, y))  
        if days != 0:
            draw.text((x + 14, y + 14), 
                      str(days), 
                      anchor="mm", 
                      font=FONT_TH, 
                      fill=WHITE)
        draw.text((x + 32, y + 14), 
                  name.title(), 
                  anchor="lm", 
                  font=FONT_TI, 
                  fill=BLACK)
        x += 118

def draw_temp_humid_list(temp_humid_list, draw):
    x, y = 598, 78                                      
    logger.info(f"value list: {temp_humid_list}")
    for t, h in temp_humid_list:
        draw.text((x, y),                                                               # temperature
                  "%0.1f°" % t, 
                  anchor="rs", 
                  font=FONT_LG, 
                  fill=BLACK) 
        draw.text((x - 100, y),                                                         # humidity
                  "%0.0f%%" % h, 
                  anchor="rs", 
                  font=FONT_SM, 
                  fill=BLACK)
        y += 55
        
def draw_extra_icons(image, draw, current_weather):
    now = current_weather.now
    m5_date = current_weather.m5_date
    m5_volts = "%0.1fv" % current_weather.m5_volts
    sunset = current_weather.sunset
    sunrise_0 = current_weather.sunrise_0
    sunrise_1 = current_weather.sunrise_1
    if now > (m5_date + timedelta(hours=2)):                                            # no update from m5stack for 2 hours
        im_battery = Image.open("icons/battery-red.png")                                # show red battery icon
        image.paste(im_battery, (570, 268))
    if now < (sunrise_0 + timedelta(hours=1)): 
        sunrise_set = sunrise_0.strftime("%H:%M")                                       # today's sunrise
    elif now < (sunset + timedelta(hours=1)):
        sunrise_set = sunset.strftime("%H:%M")                                          # today's sunset
    else:
        sunrise_set = sunrise_1.strftime("%H:%M")                                       # tomorrow's sunrise
    x, y = 570, 446
    # anchor
    # a — ascender / top (horizontal text only)
    # r — right     Anchor is to the right of the text.
    # s — baseline (horizontal text only)
    # m — middle    Anchor is vertically centered with the text.
    draw.text((x - 14, y - 164),                                                        # m5stack volts
              m5_volts, 
              anchor="rm", 
              font=FONT_SM, 
              fill=BLACK)
    draw.text((x - 14, y - 114),                                                        # uv undex 
              "%0.1f" % float(current_weather.uv_high), 
              anchor="rm", 
              font=FONT_SM, 
              fill=BLACK)
    draw.text((x - 14, y - 64),                                                         # sunrise / sunset
              sunrise_set, 
              anchor="rm", 
              font=FONT_SM, 
              fill=BLACK)
    draw.text((x - 14, y - 11), 
              "m/s", 
              anchor="rm",  
              font=FONT_TI, 
              fill=BLACK) 
    bbox = draw.textbbox((0, 0), 
                         "m/s", 
                         font=FONT_TI)
    width = bbox[2] - bbox[0]
    draw.text((x - 10 - width, y - 14),                                                 # wind speed 
              "%0.1f " % float(current_weather.wind_speed), 
              anchor="rm", 
              font=FONT_SM, 
              fill=BLACK)
    draw.text((45, 355),                                                                # weather summary
              current_weather.summary, 
              anchor="ls", 
              font=FONT_TJ, 
              fill=BLACK)
    x, y = 570, 416
    im_wind_deg = Image.open("icons/wind.png").rotate(current_weather.wind_deg, 
                                                      expand=True, 
                                                      resample=Image.BICUBIC)
    image.paste(im_wind_deg, 
                rotate_coords(im_wind_deg, x, y), 
                im_wind_deg)     

def show_weather(current_weather, temp_humid_list):
    inky = auto(ask_user=True, verbose=True)
    main_image = Image.open(f"backgrounds/{BACKGROUND}")  
    draw = ImageDraw.Draw(main_image) 

    draw_12_hours(main_image, draw, current_weather)
    draw_four_day(main_image, draw, current_weather.forecast)  
    draw_inky(main_image, current_weather.now, current_weather.rain)
    draw_extra_icons(main_image, draw, current_weather)
    draw_source_icon(main_image, current_weather.weather_source)   
    draw_birthday_list(main_image, draw)
    draw_temp_humid_list(temp_humid_list, draw)

    # sequence = current_weather.now.strftime("%H%M")
    # print(f"image sequence: {sequence}")
    if DEBUG: main_image.save(f"images/inky-test.png")                                  # output to file
    inky.set_image(main_image, saturation=SATURATION)
    inky.set_border(BCOLOR)
    inky.show()                                                                         # output to eink display
    logger.info("inky.show <done>")
    