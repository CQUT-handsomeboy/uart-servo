class IncreasementalPID:
    """
    增量式PID
    """

    def __init__(self, kp: float, ki: float, kd: float, target: float) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.target = target

        self.error = 0
        self.prev_error = 0
        self.prev_prev_error = 0
        self.error_sum = 0

    def __call__(self, input: float) -> float:
        self.error = self.target - input
        P = (self.error - self.prev_error) * self.kp
        I = self.error * self.ki
        D = (
            (self.error - self.prev_error) - (self.prev_error - self.prev_prev_error)
        ) * self.kd

        self.prev_prev_error = self.prev_error
        self.prev_error = self.error

        output = P + I + D

        return output