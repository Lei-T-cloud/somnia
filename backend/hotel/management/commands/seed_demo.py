from hotel.management.commands.init_hotel import Command as InitHotelCommand


class Command(InitHotelCommand):
    help = "已改为初始化酒店库存，不再写入演示住客"
