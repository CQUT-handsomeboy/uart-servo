import serial
from icecream import ic


def calculate_check_sum(id, instruction: int, parameters: list[int]):
    """
    计算校验和
    """
    check_sum = (
        (id + len(parameters) + 2 + instruction) + sum(parameters) ^ 0xFF
    ) & 0xFF
    return check_sum


def uart_command_write(id: int, instruction: int, parameters: list[int] = []) -> bytes:
    """
    有效数据长度 = `有效数据长度位`后面`所有位`的数量
    """
    length = len(parameters) + 2  # 参数位 + 指令位 + 校验位

    hex_list = [0xFF, 0xFF]
    hex_list.append(id)
    hex_list.append(length)
    hex_list.append(instruction)
    hex_list += parameters

    check_sum = calculate_check_sum(id, instruction, parameters)
    hex_list.append(check_sum)

    ic("send", [hex(x) for x in hex_list])
    bytes_hex = bytes(hex_list)
    ic("bytes_hex", bytes_hex)
    ser.write(bytes_hex)

    bytes_hex_1 = ser.read(4)
    valid_data_length = bytes_hex_1[-1]  # 有效数据长度
    bytes_hex_2 = ser.read(valid_data_length)
    bytes_hex = bytes_hex_1 + bytes_hex_2

    return bytes_hex


def ping(id: int) -> bytes:
    """
    查询工作状态
    """
    bytes_hex = uart_command_write(id, 0x01)
    ic(bytes_hex)
    return bytes_hex


def servo_revolve(id: int, position: int, time_gap: int, speed: int):
    """
    舵机转动
    """
    instruction = 0x03
    parameters = [
        0x2A,  # 目标地址
        position & 0xFF,  # 低位
        position >> 8,  # 高位
        time_gap & 0xFF,  # 低位
        time_gap >> 8,  # 高位
        speed & 0xFF,  # 低位
        speed >> 8,  # 高位
    ]
    bytes_hex = uart_command_write(id, instruction, parameters)
    ic(bytes_hex)
    return bytes_hex


def main():
    bytes_hex = ping(1)
    ic("return", [hex(x) for x in bytes_hex])


"""
波特率 10000
超时时间 25
"""
ser = serial.Serial("COM10", 1000000, timeout=25)

try:
    main()
except serial.serialutil.SerialException:
    print("串口占用")
finally:
    ser.close()
    pass
