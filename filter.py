from typing import Any
import numpy as np

class KalmanFilter:
    def __init__(self, Q=0.01, R=0.25):
        self.LastP = 0.02  # 上次估算协方差
        self.Now_P = 0     # 当前估算协方差
        self.out = 0       # 卡尔曼滤波器输出
        self.Kg = 0        # 卡尔曼增益
        self.Q = Q         # 过程噪声协方差
        self.R = R         # 观测噪声协方差

    def __call__(self, input):
        # 预测协方差方程
        self.Now_P = self.LastP + self.Q
        # 卡尔曼增益方程
        self.Kg = self.Now_P / (self.Now_P + self.R)
        # 更新最优值方程
        self.out += self.Kg * (input - self.out)
        # 更新协方差方程
        self.LastP = (1 - self.Kg) * self.Now_P

        return self.out

class RealtimeFilter:
    def __init__(self, alpha=0.2):
        """
        初始化实时滤波器。
        
        参数:
            alpha (float): 滤波因子，范围为(0, 1)，默认为0.2。
        """
        self.alpha = alpha
        self.filtered_value = None

    def __call__(self, value):
        """
        对输入值进行滤波。
        
        参数:
            value (float): 需要滤波的值。
            
        返回:
            float: 滤波后的值。
        """
        if self.filtered_value is None:
            self.filtered_value = value
        else:
            self.filtered_value = self.alpha * value + (1 - self.alpha) * self.filtered_value
        return self.filtered_value