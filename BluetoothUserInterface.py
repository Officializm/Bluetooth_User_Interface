#Kutuphanelerin import edilmesi.

import serial
import struct
import os
import sys
import glob

Flash_TAMAM                                         = 0x00
FLASH_HATA                                          = 0x01
Flash_MESGUL                                        = 0x02
Flash_HAL_TIMEOUT                                   = 0x03
Flash_GECERSIZ_ADDR                                 = 0x04


COMMAND_BL_GET_VER                                  =0x51
COMMAND_BL_FLASH_ERASE                              =0x56
COMMAND_BL_MEM_WRITE                                =0x57




COMMAND_BL_GET_VER_LEN                              =6
COMMAND_BL_FLASH_ERASE_LEN                          =8
COMMAND_BL_MEM_WRITE_LEN                            =11



verbose_mode = 1
mem_write_active =0

#----------------------------- file ops----------------------------------------
#dosyanin uzunlugunun hesaplanmasi
def calc_file_len():
    size = os.path.getsize("user_app.bin")
    return size

#dosyanin acilmasi
def open_the_file():
    global bin_file
    bin_file = open('user_app.bin','rb')
    

def close_the_file():
    bin_file.close()




#----------------------------- araclar ----------------------------------------
#Word to byte donusumu yapilmasi
def word_to_byte(addr, index , lowerfirst):
    value = (addr >> ( 8 * ( index -1)) & 0x000000FF )
    return value

def get_crc(buff, length): #crc veri hesaplaniyor
    Crc = 0xFFFFFFFF
    #print(length)
    for data in buff[0:length]:
        Crc = Crc ^ data
        for i in range(32):
            if(Crc & 0x80000000):
                Crc = (Crc << 1) ^ 0x04C11DB7
            else:
                Crc = (Crc << 1)
    return Crc

#----------------------------- Seri Port ----------------------------------------
#Com seri portu aciliyor
def serial_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def Serial_Port_Configuration(port):
    global ser
    try:
        ser = serial.Serial(port,115200,timeout=2) #baudrate ayarlaniyor
    except:
        print("\n  Girdiginiz port ismi  Gecersiz !!")
        
        port = serial_ports()
        if(not port):
            print("\n   Herhangi bir port tespit edilemedi!")
        else:
            print("\n   Bilgisayarınızda açık olan port listesi. Lutfen Tekrar Deneyiniz!")
            print("\n   ",port)
        return -1
    if ser.is_open:
        print("\n   Port Acık Başarılı.")
    else:
        print("\n   Port Acık Basarısız.")
    return 0

              
def read_serial_port(length):
    read_value = ser.read(length)
    return read_value

def Close_serial_port():
    pass
def purge_serial_port():
    ser.reset_input_buffer()
    
def Write_to_serial_port(value, *length): #Seri porta veri gonderiliyor
        data = struct.pack('>B', value)
        if (verbose_mode):
            value = bytearray(data)
            #print("   "+hex(value[0]), end='')
            print("   "+"0x{:02x}".format(value[0]),end=' ')
        if(mem_write_active and (not verbose_mode)):
                print("#",end=' ')
        ser.write(data)


        
#----------------------------- Fonksiyonlar ----------------------------------------

def process_COMMAND_BL_GET_VER(length):
    ver=read_serial_port(1)
    value = bytearray(ver)
    print("\n   Bootloader Ver. : ",hex(value[0]))





def process_COMMAND_BL_FLASH_ERASE(length):
    silme_durumu=0
    value = read_serial_port(length)
    if len(value):
        silme_durumu = bytearray(value)
        if(silme_durumu[0] == Flash_TAMAM):
            print("\n   Silme Durumu: KOD BASARILI: Flash_TAMAM")
        elif(silme_durumu[0] == FLASH_HATA):
            print("\n   Silme Durumu: KOD HATALI: FLASH_HATA")
        elif(silme_durumu[0] == Flash_MESGUL):
            print("\n   Silme Durumu: KOD HATALI: Flash_MESGUL")
        elif(silme_durumu[0] == Flash_HAL_TIMEOUT):
            print("\n   Silme Durumu: KOD HATALI: FLASH_HAL_TIMEOUT")
        elif(silme_durumu[0] == Flash_GECERSIZ_ADDR):
            print("\n   Silme Durumu: KOD HATALI: Flash_GECERSIZ_ADDR")
        else:
            print("\n   Silme Durumu: KOD HATALI: UNKNOWN_ERROR_CODE")
    else:
        print("Timeout: Bootloader is not responding")

def process_COMMAND_BL_MEM_WRITE(length):
    yazma_durumu=0
    value = read_serial_port(length)
    yazma_durumu = bytearray(value)
    if(yazma_durumu[0] == Flash_TAMAM):
        print("\n   Yazma Durumu: Flash_TAMAM")
    elif(yazma_durumu[0] == FLASH_HATA):
        print("\n   Yazma Durumu:: FLASH_HATA")
    elif(yazma_durumu[0] == Flash_MESGUL):
        print("\n   Yazma Durumu:: Flash_MESGUL")
    elif(yazma_durumu[0] == Flash_HAL_TIMEOUT):
        print("\n   Yazma Durumu:: FLASH_HAL_TIMEOUT")
    elif(yazma_durumu[0] == Flash_GECERSIZ_ADDR):
        print("\n   Yazma Durumu:: Flash_GECERSIZ_ADDR")
    else:
        print("\n   Yazma Durumu:: UNKNOWN_ERROR")
    print("\n")
    





def decode_menu_command_code(command):
    ret_value = 0
    data_buf = []
    for i in range(255):
        data_buf.append(0) #Dizinin tum elemanlari sifirlaniyor.
    
    if(command  == 0 ):
        print("\n   Çıkış Yapılıyor...!")
        raise SystemExit
    elif(command == 1):
        print("\n   Command == > BOOTLOADER_GET_VERSION")
        COMMAND_BL_GET_VER_LEN              = 6
        data_buf[0] = COMMAND_BL_GET_VER_LEN-1 
        data_buf[1] = COMMAND_BL_GET_VER 
        crc32       = get_crc(data_buf,COMMAND_BL_GET_VER_LEN-4)
        crc32 = crc32 & 0xffffffff
        data_buf[2] = word_to_byte(crc32,1,1) 
        data_buf[3] = word_to_byte(crc32,2,1) 
        data_buf[4] = word_to_byte(crc32,3,1) 
        data_buf[5] = word_to_byte(crc32,4,1) 

        
        Write_to_serial_port(data_buf[0],1)
        for i in data_buf[1:COMMAND_BL_GET_VER_LEN]:
            Write_to_serial_port(i,COMMAND_BL_GET_VER_LEN-1)
        

        ret_value = read_bootloader_reply(data_buf[1])
        
 
    elif(command == 2):
        data_buf[1] = COMMAND_BL_FLASH_ERASE
        print("\n   Command == > BL_FLASH_ERASE")
        data_buf[0] = COMMAND_BL_FLASH_ERASE_LEN-1
        sector_num = input("\n   Sektorun numarasını giriniz(0-7 veya 0xFF) :")
        sector_num = int(sector_num, 16)
        if(sector_num != 0xff):
            nsec=int(input("\n  Silmek istediğiniz sektorlerin sayısını giriniz(max 8) :"))
        
        data_buf[2]= sector_num 
        data_buf[3]= nsec 

        crc32       = get_crc(data_buf,COMMAND_BL_FLASH_ERASE_LEN-4) 
        data_buf[4] = word_to_byte(crc32,1,1) 
        data_buf[5] = word_to_byte(crc32,2,1) 
        data_buf[6] = word_to_byte(crc32,3,1) 
        data_buf[7] = word_to_byte(crc32,4,1) 

        Write_to_serial_port(data_buf[0],1)
        
        for i in data_buf[1:COMMAND_BL_FLASH_ERASE_LEN]:
            Write_to_serial_port(i,COMMAND_BL_FLASH_ERASE_LEN-1)
        
        ret_value = read_bootloader_reply(data_buf[1])
        
    elif(command == 3):
        print("\n   Command == > BL_MEM_WRITE")
        bytes_remaining=0
        t_len_of_file=0
        bytes_so_far_sent = 0
        len_to_read=0
        base_mem_address=0

        data_buf[1] = COMMAND_BL_MEM_WRITE

        #dosyanin uzunlugu degiskene ataniyor
        t_len_of_file =calc_file_len()

       
        open_the_file()

        bytes_remaining = t_len_of_file - bytes_so_far_sent

        base_mem_address = input("\n   Hafıza başlangıc  adresini giriniz :")
        base_mem_address = int(base_mem_address, 16)
        global mem_write_active
        while(bytes_remaining):
            mem_write_active=1
            if(bytes_remaining >= 128):
                len_to_read = 128
            else:
                len_to_read = bytes_remaining
            #get the bytes in to buffer by reading file
            for x in range(len_to_read):
                file_read_value = bin_file.read(1)
                file_read_value = bytearray(file_read_value)
                data_buf[7+x]= int(file_read_value[0])
            
            
            #dizinin elemanlari dolduruluyor
            data_buf[2] = word_to_byte(base_mem_address,1,1)
            data_buf[3] = word_to_byte(base_mem_address,2,1)
            data_buf[4] = word_to_byte(base_mem_address,3,1)
            data_buf[5] = word_to_byte(base_mem_address,4,1)

            data_buf[6] = len_to_read

           
            mem_write_cmd_total_len = COMMAND_BL_MEM_WRITE_LEN+len_to_read

            
            data_buf[0] =mem_write_cmd_total_len-1

            crc32       = get_crc(data_buf,mem_write_cmd_total_len-4)
            data_buf[7+len_to_read] = word_to_byte(crc32,1,1)
            data_buf[8+len_to_read] = word_to_byte(crc32,2,1)
            data_buf[9+len_to_read] = word_to_byte(crc32,3,1)
            data_buf[10+len_to_read] = word_to_byte(crc32,4,1)

          
            base_mem_address+=len_to_read
            #gonderilecek olan dizinin uzunlugu onceden seriporta yaziliyor.
            Write_to_serial_port(data_buf[0],1)
            #daha sonra diger elemanlar teker teker gonderiliyor
            for i in data_buf[1:mem_write_cmd_total_len]:
                Write_to_serial_port(i,mem_write_cmd_total_len-1)

            bytes_so_far_sent+=len_to_read
            bytes_remaining = t_len_of_file - bytes_so_far_sent
            print("\n   Gönderilen Byte:{0} -- Kalan Byte:{1}\n".format(bytes_so_far_sent,bytes_remaining)) 
        
            ret_value = read_bootloader_reply(data_buf[1])
        mem_write_active=0

  
    else:
        print("\n   Lütfen gecerli komut kodu giriniz !\n")
        return

    if ret_value == -2 :
        print("\n   TimeOut :Bootloader cevap vermiyor !")
        print("\n   Lutfen karti resetleyip tekrar deneyiniz !")
        return

def read_bootloader_reply(command_code):
    
    len_to_follow=0 
    ret = -2 

   
    ack=read_serial_port(2)
    if(len(ack) ):
        a_array=bytearray(ack)
        
        if (a_array[0]== 0xA5):
            
            len_to_follow=a_array[1]
            print("\n   CRC : BASARILI :",len_to_follow)
           
            if (command_code) == COMMAND_BL_GET_VER :
                process_COMMAND_BL_GET_VER(len_to_follow)
            
            elif(command_code) == COMMAND_BL_FLASH_ERASE:
                process_COMMAND_BL_FLASH_ERASE(len_to_follow)
                
            elif(command_code) == COMMAND_BL_MEM_WRITE:
                process_COMMAND_BL_MEM_WRITE(len_to_follow)
             
            else:
                print("\n   Gecersiz komut kodu\n")
                
            ret = 0
         
        elif a_array[0] == 0x7F:
            
            print("\n   CRC: HATA \n")
            ret= -1
    else:
        print("\n   Timeout : Bootloader cevap vermiyor!")
        
    return ret

            
            

#----------------------------- MENU----------------------------------------


name = input("Lutfen baglanmak istediginiz portun ismini yaziniz(ORN: COM3):")
ret = 0
ret=Serial_Port_Configuration(name)
if(ret < 0):
    decode_menu_command_code(0)
    

    
  
while True:
    print("\n +==========================================+")
    print(" |               Menu                       |")
    print(" |         STM32F4 BootLoader v1            |")
    print(" +==========================================+")

  
    
    print("\n Lutfen gondermek istediginiz komutu yazınız.\n")
    print("   BOOTLOADER_GET_VERSION-----------------------> 1")
    print("   BOOTLOADER_FLASH_ERASE-----------------------> 2")
    print("   BOOTLOADER_MEMORY_WRITE----------------------> 3")
    print("   MENU_EXIT------------------------------------> 0")

    command_code = input("\n   Komutu buraya giriniz :")

    if(not command_code.isdigit()):
        print("\n   Lutfen gecerli bir sayi giriniz")
    else:
        decode_menu_command_code(int(command_code))

    input("\n   Devam etmek icin herhangi bir tusa basiniz  :")
purge_serial_port()