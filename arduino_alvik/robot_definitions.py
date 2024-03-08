# Motor control and mechanical parameters
MOTOR_KP_DEFAULT = 32.0
MOTOR_KI_DEFAULT = 450.0
MOTOR_KD_DEFAULT = 0.0
MOTOR_MAX_RPM = 70.0
MOTOR_CONTROL_DEG_S = 40
MOTOR_CONTROL_MM_S = 40
WHEEL_TRACK_MM = 89.0

# Wheels parameters
WHEEL_DIAMETER_MM = 34.0

# Robot params
ROBOT_MAX_DEG_S = 6*(2*MOTOR_MAX_RPM*WHEEL_DIAMETER_MM)/WHEEL_TRACK_MM
