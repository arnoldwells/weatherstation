def get_weather():
    import math
    import board
    import requests
    import adafruit_sht4x
    from inky.auto import auto
    from datetime import datetime, timedelta
    from PIL import Image, ImageDraw, ImageFont    
    from config import ADAFRUIT_USER, ADAFRUIT_API_KEY, OPENWEATHERMAP_COORDS, OPENWEATHERMAP_API_KEY
    from constants import UNITS, EXCLUDES, FORECAST_URL, DEBUG, RED, BLUE, BLACK, GREEN, WHITE, BCOLOR, BACKGROUND, SATURATION, WEATHER_CODES
    
    from Adafruit_IO import Client                                                              # Import library and create instance of REST client.
    aio = Client(ADAFRUIT_USER, ADAFRUIT_API_KEY)

    font_lg = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=40)
    font_sm = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=28)
    font_ti = ImageFont.truetype("fonts/Roboto-Medium.ttf", size=20)

    temp_humid_list = []
    now = datetime.now()    
    inky = auto(ask_user=True, verbose=True)
    request_url = (FORECAST_URL + OPENWEATHERMAP_COORDS + OPENWEATHERMAP_API_KEY + UNITS + EXCLUDES)                  

    main_image = Image.open(f"backgrounds/{BACKGROUND}")
    draw = ImageDraw.Draw(main_image) 

    def rotate_coords(image, x, y):                                                             # for rotating objects (wind direction, inky)
        (new_width, new_height) = image.size
        return (x - int((new_width - 28) / 2), y - int((new_height - 28) / 2))

    def coords(image, x, y):                                                                    # objects distributed around the circle
        (new_width, new_height) = image.size
        return (x - int(new_width / 2), y - int(new_height / 2))


    try:                                                     # ====================== try fetching forecast from api.openweathermap.org ====================
        response = requests.get(request_url)
        forecast_dict = response.json()                                        
    except Exception as error:                               # create dummy data and add error message to summary
        try:
            code = response.status_code
        except:
            code = 0        
        print("\x1B[92mException openweathermap request\x1B[0m * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *")
        print(f"code:{code} Get api.openweathermap.org error\n{error}"[:500])        
        summary = f"code:{code} Get api.openweathermap.org error\n{error}"[:80]                 # truncate line
        uv = "0.0"
        wind_deg = 360
        wind_speed = "0.0 "
        sunset = datetime.fromtimestamp(1704139200)
        sunrise_0 = datetime.fromtimestamp(1704096000)
        sunrise_1 = datetime.fromtimestamp(1704153600)
        # moon_phase = 0.0
        forecast_dict = {
            'current': {
                'temp': -1,
                'humidity': -1
            },
            'daily': [ {} ],
            'hourly': []
        }       
        for day in range(1, 5):
            forecast_dict['daily'].append({})
            forecast_dict['daily'][day]['temp'] = {}
            forecast_dict['daily'][day]['temp']['min'] = -1
            forecast_dict['daily'][day]['temp']['max'] = -1            
            forecast_dict['daily'][day]['weather'] = []
            forecast_dict['daily'][day]['weather'].append({'id': 200})
        for hour in range(12):
            forecast_dict['hourly'].append({})   
            forecast_dict['hourly'][hour]['dt'] = 1704110400 + (hour * 3600)
            forecast_dict['hourly'][hour]['pop'] = 0
            forecast_dict['hourly'][hour]['temp'] = -1
            forecast_dict['hourly'][hour]['weather'] = []
            forecast_dict['hourly'][hour]['weather'].append({'id': 200})
        if DEBUG: print(forecast_dict)   
    else:
        uv = "%0.1f" % float(forecast_dict['daily'][0]['uvi'])
        wind_deg = 360 - (180 + forecast_dict['current']['wind_deg'])
        wind_speed = "%0.1f " % float(forecast_dict['current']['wind_speed'])       
        sunrise_0 = datetime.fromtimestamp(forecast_dict['daily'][0]['sunrise'])
        sunrise_1 = datetime.fromtimestamp(forecast_dict['daily'][1]['sunrise'])
        sunset = datetime.fromtimestamp(forecast_dict['daily'][0]['sunset'])
        if int(now.strftime("%H")) >= 20:                                                       # if after 20:00
            summary = "+" + forecast_dict['daily'][1]['summary']                                # use summary from tomorrow
        else:
            summary = forecast_dict['daily'][0]['summary']
        if draw.textsize(summary, font_ti)[0] > 410:                                            # insert newline if text is long
            position = summary.find(" ", len(summary)//2)                                        # find " " in second half of summary
            summary = summary[:position] + "\n" + summary[position + 1:]                        # insert \n
            # # split_summary = summary.split()                                                 # old method
            # # split_summary.insert(8, "\n")
            # summary = ' '.join(split_summary)         
        # moon_phase = forecast_dict['daily'][0]['moon_phase']
    finally:
        temp_humid_list.append((forecast_dict['current']['temp'], forecast_dict['current']['humidity']))


    try:                                       # ======================== retrieve temperature humidity values from io.adafruit.com ========================
        volts = "%0.1fv" % float(aio.receive('m5-voltage').value)
        m5_date = datetime.strptime(aio.receive('m5-voltage').updated_at, "%Y-%m-%dT%XZ")
        temp_humid_list.append((aio.receive('bedroom-temperature').value, aio.receive('bedroom-humidity').value))
        temp_humid_list.append((aio.receive('m5-temperature').value, aio.receive('m5-humidity').value))                
        # sensor_temp_humidity = (aio.receive('temperature').value, aio.receive('humidity').value)              # when sensor not locally attached
    except Exception as error:
        volts = "-1v"
        m5_date = datetime.fromtimestamp(1704067200)
        temp_humid_list.append((-1, -1))                                                        # bedroom
        temp_humid_list.append((-1, -1))                                                        # m5
        print("\x1B[92mException receiving data feed from io.adafruit.com\x1B[0m * * * * * * * * * * * * * * * * * * * * * * * * * *")
        print(error[:500])
        
                                                            # ================================== store values from sensor ==================================
                                                                    # i2c = busio.I2C(board.SCL, board.SDA)
    i2c = board.I2C()                                               # uses board.SCL and board.SDA
    try:
        sensor = adafruit_sht4x.SHT4x(i2c) 
        sensor.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION      # Can set the mode to enable heater # sensor.mode = adafruit_sht4x.Mode.LOWHEAT_100MS
        sensor_temp_humidity = sensor.measurements                  
    except:
        sensor_temp_humidity = (-1, -1)
        print("\x1B[92mException SHT4x sensor not working\x1B[0m * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *")
    else:
        print("Found SHT4x with serial number:", hex(sensor.serial_number))
        if DEBUG: print("Current sensor mode is:", adafruit_sht4x.Mode.string[sensor.mode])
    finally:
        temp_humid_list.append(sensor_temp_humidity)


    try:                                                      # ========================== send the values to a Adafruit IO feeds ==========================
        aio.send('temperature', sensor_temp_humidity[0])
        aio.send('humidity', sensor_temp_humidity[1])
        aio.send('outside', forecast_dict['current']['temp'])
    except Exception as error:
        print("\x1B[92mException sending data feed to io.adafruit.com\x1B[0m * * * * * * * * * * * * * * * * * * * * * * * * * * *")
        print(error[:500])
   

    x, y = 600 - 2, 0 + 78                                     # ======================== draw temperature temp and humiduty values ========================
    if DEBUG: print(temp_humid_list)
    for t, h in temp_humid_list:            
        draw.text((x, y), "%0.1f°" % float(t), anchor="rs", font=font_lg, fill=BLACK)
        draw.text((x - 100, y), "%0.0f%%" % float(h), anchor="rs", font=font_sm, fill=BLACK)
        y += 55
    
                                                               # ==================================== draw device icons ====================================
    im_outside = Image.open("icons/outside.png")               # could be added as a list and used in the for loop above
    im_bedroom = Image.open("icons/bedroom.png")
    im_m5stack = Image.open("icons/m5stack3.png")
    im_pimoroni = Image.open("icons/pimoroni.png")    
    main_image.paste(im_outside, (404, 50))   
    main_image.paste(im_bedroom, (404, 105))   
    main_image.paste(im_m5stack, (404, 160))   
    main_image.paste(im_pimoroni, (404, 215))   

                                                      # ================================== draw extra icons and values =====================================
    if now > (m5_date + timedelta(hours=2)):                                                    # no update to m5stack for 2 hours
        im_battery = Image.open("icons/battery-red.png")                                        # show red battery icon
        main_image.paste(im_battery, (570, 268))   
    if now < (sunrise_0 + timedelta(hours=1)): 
        sunriseset = sunrise_0.strftime("%H:%M")                                                # today's sunrise
    elif now < (sunset + timedelta(hours=1)):
        sunriseset = sunset.strftime("%H:%M")                                                   # today's sunset
    else:
        sunriseset = sunrise_1.strftime("%H:%M")                                                # tomorrow's sunrise

    x, y = 570, 446
    # anchor
    # a — ascender / top (horizontal text only)
    # r — right     Anchor is to the right of the text.
    # s — baseline (horizontal text only)
    # m — middle    Anchor is vertically centered with the text.
    draw.text((x - 14, y - 164), volts, anchor="rm", font=font_sm, fill=BLACK)                  # m5stack volts
    draw.text((x - 14, y - 114), uv, anchor="rm", font=font_sm, fill=BLACK)                     # uv undex
    draw.text((x - 14, y - 64), sunriseset, anchor="rm", font=font_sm, fill=BLACK)              # sunrise / sunset
    draw.text((x - 14, y - 11), "m/s", anchor="rm",  font=font_ti, fill=BLACK) 
    width_height = draw.textsize("m/s", font=font_ti)
    draw.text((x - 10 - width_height[0], y - 14), wind_speed, anchor="rm", font=font_sm, fill=BLACK)            # wind speed
    draw.text((45, 351), summary, anchor="ls", font=font_ti, fill=BLACK)                        # weather summary 

    x, y = 570, 416
    im_wind_deg = Image.open("icons/wind.png").rotate(wind_deg, expand=True, resample=Image.BICUBIC)
    if DEBUG: print("calling coords with im_wind_deg")
    main_image.paste(im_wind_deg, rotate_coords(im_wind_deg, x, y), im_wind_deg)     


    x, y = 215, 165                                        # ===================================== 12 hour forecast ========================================
    rain = False
    radius = 140
    rain_radius = radius - 36
    temp_radius = rain_radius - 19
    # rain_radius = temp_radius + 5
    arc_radius = 41                                                                             # inner arc
    rain_width = rain_radius - arc_radius                                                       # full width
    for a in range(12):
        hour = int(datetime.fromtimestamp(forecast_dict['hourly'][a]['dt']).strftime("%H"))
        angle = (hour % 12) * 30
        wx = int(x + (radius * math.sin(math.radians(angle))))                                  # weather icon x/y
        wy = int(y - (radius * math.cos(math.radians(angle))))
        tx = int(x + (temp_radius * math.sin(math.radians(angle))))                             # temp x/y
        ty = int(y - (temp_radius * math.cos(math.radians(angle))))     
        pop = forecast_dict['hourly'][a]['pop']                                                 # probability of precipitation
        temp = forecast_dict['hourly'][a]['temp']                                               # temperature
        id = forecast_dict['hourly'][a]['weather'][0]['id']
        if id // 100 not in [8, 7]:                                                             # forecast is for rain 8xx, 7xx
            rain = True                                                                         # set flag for inky_umbrella
        # if DEBUG: print("sunrise", sunrise_1.strftime("%I"), "sunset", sunset.strftime("%H")) 
        if int(sunrise_1.strftime("%I")) <= hour <= int(sunset.strftime("%H")):                 # forecast hour between sunrise(tomorrow) and sunset
            code = f"{id}d"                                                                     # set daytime code
        else:
            code = f"{id}n"                                                                     # set nighttime code
        icon_filename = f"weather/{WEATHER_CODES[code]}.png"
        im_weather = Image.open(icon_filename) 
        main_image.paste(im_weather, coords(im_weather, wx, wy), im_weather)                    # paste weather icon

        if pop >= 0.1:                                                                          # percentage of precipitation above 10%
            pie_end = angle - 75
            pie_start = angle - 105
            inner_radius = rain_radius - int(rain_width * pop)
            if DEBUG: print("inner_radius:", inner_radius)           
            draw.pieslice((x - rain_radius, y - rain_radius, x + rain_radius, y + rain_radius), start=pie_start, end=pie_end, fill=GREEN)       # green segment
            draw.pieslice((x - inner_radius, y - inner_radius, x + inner_radius, y + inner_radius), start=pie_start, end=pie_end, fill=WHITE)   # overlayed white
            draw.arc((x - arc_radius, y - arc_radius, x + arc_radius, y + arc_radius), start=pie_start, end=pie_end, fill=BLUE, width=1)        # to show boundary
        
        if a == 0:                                                                              # if current hour
            if DEBUG: print("drawing current hour arc")
            arc_end = angle - 75
            arc_start = angle - 105
            draw.arc((x - rain_radius - 3, y - rain_radius - 3, x + rain_radius + 3, y + rain_radius + 3), start=arc_start, end=arc_end, fill=RED, width=4)    

        draw.text((tx, ty), "%0.0f°" % temp, anchor="mm", font=font_ti, stroke_width=2, stroke_fill=WHITE, fill=BLACK)                          # black 
        if DEBUG: print(f"{angle}° a:{a} wx:{wx} wy:{wy} temp:{temp} hour:{hour}:00 pop:{pop} id:{id} code:{code} filename:{icon_filename}")
        


                                               # ========================================== draw inky and bubbles ==========================================
    now_seconds = (now - now.replace(hour=0, minute=0, second=0)).total_seconds()               # seconds since midnight
    rotation = (((now_seconds % 43200) / 43200) * 360)
    inky_rotation =  360 - (int(rotation) - 5)                                                  # with 5° minor adjustment
    if DEBUG: print("inky_rotation:", inky_rotation)

    inky_file = "images/inky-solo.png" if not rain else "images/inky-umbrella.png"
    im_inky = Image.open(inky_file).rotate(inky_rotation, expand=True, resample=Image.BICUBIC) 
    im_bubbles = Image.open("images/inky-bubbles.png")
    main_image.paste(im_bubbles, coords(im_bubbles, x, y))                                      # paste bubbles image
    main_image.paste(im_inky, coords(im_inky, x, y), im_inky)                                   # paste rotated inky image


    x, y = 45, 379                                    # ========================================== 4 day forecast ==========================================
    for day in range(1, 5):
        min = forecast_dict['daily'][day]['temp']['min'] 
        max = forecast_dict['daily'][day]['temp']['max']
        id = forecast_dict['daily'][day]['weather'][0]['id'] 
        code = f"{id}d"                                                                         # use day version of icons
        icon_filename = f"weather/{WEATHER_CODES[code]}.png"
        im_weather = Image.open(icon_filename)                                                  # lookup code from weather dictionary
        main_image.paste(im_weather, (x, y), im_weather)
        draw.text((x + 65, y + 8), "%0.0f°" % max, anchor="lt", font=font_ti, fill=BLACK)
        draw.text((x + 65, y + 30), "%0.0f°" % min, anchor="lt", font=font_ti, fill=BLACK)
        x += 105

                                                        # ========================================== output image ==========================================
    if DEBUG: main_image.save("images/inky-test.png")                                           # output to file
    inky.set_image(main_image, saturation=SATURATION)
    inky.set_border(BCOLOR)
    if DEBUG: print("inky.show <next>")
    inky.show()                                                                                 # output to eink display
    if DEBUG: print("inky.show <done>")

    return summary                                                                              # everything worked
