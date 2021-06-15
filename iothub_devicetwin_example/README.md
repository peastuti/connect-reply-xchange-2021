# Install IDF

Follow this guide to install and configure ESP32 Environment
https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/index.html

This is a very detailed doc, you'll find anything there. 


## Most Important Steps

Finally, enter the project and execute the following commands

```sh
get_idf
idf.py set-target esp32
```

Use `idf.py menuconfig` to configure, under example configuration, `wifi ssid`, `password` and `iothub device connection string` that you took from the Cloud Configuration part.

Now you should be ready to build your code using

```
idf.py build
```

if everything goes well, you can upload your code to the ESP32.
Ensure that the board is connected and the cable works fine (this is most of the troubleshooting).

If you're on mac, upload your code using

```
idf.py -p /dev/cu.usbserial-0001 flash
```

otherwise you have to change the path of your USB:
- Windows: names like COM1
- Linux: starting with /dev/tty
- macOS: starting with /dev/cu.

Now, you should be able to monitor your code using

```
idf.py -p /dev/cu.usbserial-0001 monitor
```

And that's everything, we guess.
