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