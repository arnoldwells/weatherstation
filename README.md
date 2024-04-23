# [Pimoroni Inky Impression eink](https://shop.pimoroni.com/products/inky-impression-5-7?variant=32298701324371) weather station

The weather station runs on a Raspberry Pi Zero and displays weather forecast and sensor data. It retrieves the weather data from [openweathermap.org](https://openweathermap.org/) and stores and retrieves data from [io.adafruit.com](https://io.adafruit.com/). Using the current weather summary it generates a weather art image using [getimg.ai](https://getimg.ai/). A button press stores this image on Google Drive. The system can also display a slideshow containing the images previously stored on Google Drive.

Starting at 07:00 it updates the display every fifteen minutes with the weather and sensor data until 09:00, when it will generate and display the weather art image. The image will be displayed for an hour unless a button is pressed to shorten the duration. The art image is generated based on the weather summary in the style of a randomly selected [artist](artists-new.json) and can include optional keywords to influence the style associated with the artist. After midnight the display stops updating to allow it to rest.

![sped up animation](/doc/sped-up-animation.gif)

### Weather station guide
![weatherstation_guide](/doc/weatherstation-guide.png)
### [Example art images](https://github.com/arnoldwells/weatherstation/tree/main/generated) 
[![vangogh](/generated/2023-12-06-vangogh-Gw.jpg)](https://github.com/arnoldwells/weatherstation/tree/main/generated)

Image created in the style of Vincent van Gogh, with a prompt containing: A day of partly cloudy with clear spells in December
### [Getimg.ai generation data](https://docs.getimg.ai/reference/poststablediffusiontexttoimage)
```
generation_data = {                                                                            
    "model": "absolute-reality-v1-6",                                                           # Replace with your desired model
    "prompt": f"{summary} in {month}. {keywords}. Painting in the style of artist {artist_name}",        # Your prompt for generating the image
    "negative_prompt": "Disfigured, cartoon, blurry, nude",
    "output_format": "jpeg",                                                                    # Specify JPEG format
    "width": 576,                                                                               # Your desired width x 64
    "height": 448,                                                                              # Your desired height
    "steps": 25,
    "guidance": 6                                                                               # 0-20 Higher guidance forces the model to better follow the prompt
}      
 ```    

### Error handling
![openweathermap_error](/doc/openweathermap-error.png)

This image shows an error occurred fetching the openweathermap data and uses a thunderstorm icon and some -1 temperatures. The summary is used to show any error messages.

![other_errors](/doc/other-errors.png)

Examples of other errors: File error, Getimg.ai json error, Slideshow error

### Further improvements and features
- Query the google calendar and add a countdown for the next two birthday events
- Show the current moon phase
- Create more weather [icons](https://github.com/arnoldwells/weatherstation/tree/main/weather)
- Experiment with other colour options on the eink display
- Use another (less pessimistic) source for weather forecast data
- Detect a summary containing an error message and don't use it for getimg.ai
- Automatically remove old images from the [generated](https://github.com/arnoldwells/weatherstation/tree/main/generated) images folder
- Show UV index the same way as the PoP - resolving any overlap conflicts
- Retrieve the [artists-new.json](artists-new.json) file from Google Drive to facilitate easier updating
- Connect to a Xiaomi Mi Temperature / Humidity sensor through bluetooth

### This project was inspired by
[Enjoy the current weather with Picasso's painting](https://hackaday.io/project/190692-wow-enjoy-the-current-weather-with-picassos-pai)

[![current_weather_with_picassos_painting](https://cdn.hackaday.io/images/resize/600x600/7228091682003845608.jpg)](https://hackaday.io/project/190692-wow-enjoy-the-current-weather-with-picassos-pai)
