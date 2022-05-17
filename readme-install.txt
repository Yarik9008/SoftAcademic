1) установка armbian
    0) зажмите кнопку usb boot
    1) подключите одноплатник к пк (через ближний к краю платы usb разьем) 
    2) запустите программу RZ_USB_Boot_Helper_V1.0.0
    3) выберите в качестве файла для загрузки radxa-zero-erase-emmc.bin
    4) забустите запись (кнопка run)
    5) дождитесь пока закончиться запись и одноплатник стане определяться как usb накопитель 
    6) отворматируйте появившийся диск 
    7) запустите программу balenaEtcher-Setup-1.7.9
    8) выберете дистрибутиа линукса 
    9) выбирите usb накопитель который вы отформатировали 
    10) запустите запись образа и дожитесь заверщения загрузки
    11) после завершения загрузки отсоедините от пк одноплатник 

2) установка софта 

    пользователь по умолчанию: rock
    пароль по умолчанию: rock

    sudo apt-get update

    0) если есть необходимость в подключении к WIFI
        nmcli r wifi on

        nmcli dev wifi

        nmcli dev wifi connect "wifi_name" password "wifi_password"

        ifconfig

    1) скачивание репозитория 
        git clone https://github.com/Yarik9008/SoftAcademic

    2) установка библиотеки для джойстика 
        sudo apt install python3-pip

        sudo pip3 install pygame 

        sudo pip3 install pyserial

    3) подключение джойстика 
        sudo armbian-config

        #обновить драйвера блютуса 
        #подключть через кнопку джойстик 
    
    4) включение uart
        sudo nano /boot/uEnv.txt


3) добавление в автозапуск 
    crontab -e 
    1
    @reboot sleep 10 && /usr/bin/python3 /home/rock/SoftAcademic/raspberry-pult/main_pult.py &
