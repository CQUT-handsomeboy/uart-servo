import serial
from icecream import ic


class Servo:
    def __init__(self, port: str = "COM10") -> None:
        try:
            self.ser = serial.Serial(port, 1000000, timeout=25)
            self.status = True  # 串口占用，失败
        except serial.serialutil.SerialException:
            self.status = False  # 串口占用，失败

    def __calculate_check_sum(self, id, instruction: int, parameters: list[int]):
        """
        计算校验和
        """
        check_sum = (
            (id + len(parameters) + 2 + instruction) + sum(parameters) ^ 0xFF
        ) & 0xFF
        return check_sum

    def __uart_command_write(
        self, id: int, instruction: int, parameters: list[int] = []
    ):
        """
        有效数据长度 = `有效数据长度位`后面`所有位`的数量
        """
        length = len(parameters) + 2  # 参数位 + 指令位 + 校验位

        hex_list = [0xFF, 0xFF]
        hex_list.append(id)
        hex_list.append(length)
        hex_list.append(instruction)
        hex_list += parameters

        check_sum = self.__calculate_check_sum(id, instruction, parameters)
        hex_list.append(check_sum)

        try:
            bytes_hex = bytes(hex_list)
        except ValueError:
            ic(hex_list)

        self.ser.write(bytes_hex)

    def __uart_read_info(self) -> bytes:
        bytes_hex_1 = self.ser.read(4)
        assert len(bytes_hex_1) != 0
        valid_data_length = bytes_hex_1[-1]  # 有效数据长度
        bytes_hex_2 = self.ser.read(valid_data_length)
        bytes_hex = bytes_hex_1 + bytes_hex_2

        return bytes_hex

    def ping(self, id: int) -> bool:
        """
        查询工作状态
        """
        self.__uart_command_write(id, 0x01)
        try:
            bytes_hex = self.__uart_read_info()
        except AssertionError:
            # 这说明没读到信息，工作状态错误
            return False
        working_status = True if bytes_hex[4] == 0 else False
        return working_status

    def revolve(self, id: int, position: int, time_gap: int, speed: int):
        """
        舵机转动
        """
        position = 1024 if position > 1024 else position
        position = 0 if position < 0 else position

        instruction = 0x03
        parameters = [
            0x2A,  # 目标地址
            (position) >> 8,  # 高位
            position & 0xFF,  # 低位
            (time_gap) >> 8,  # 高位
            time_gap & 0xFF,  # 低位
            (speed) >> 8,  # 高位
            speed & 0xFF,  # 低位
        ]
        self.__uart_command_write(id, instruction, parameters)
        bytes_hex = self.__uart_read_info()

    def get_current_position(self, id) -> int:
        """
        这个函数只能在最开始的时候调用
        后面调用不会返回参数
        """
        self.__uart_command_write(id, 0x02, [0x38, 0x02])
        bytes_hex = self.__uart_read_info()
        assert bytes_hex[4] == 0
        if len(bytes_hex) != 8:
            return
        position = (bytes_hex[5] << 8) | (bytes_hex[6])

        return position
