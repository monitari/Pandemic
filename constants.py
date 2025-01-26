# constants.py: 상수를 정의하는 파일

# Simulation Constants
INFECTION_RADIUS_SQ = 225  # 15^2
GRID_SIZE = 30
UPDATE_INTERVAL = 1/30
DEFAULT_POPULATION = 400

# Colors
HEALTHY_COLOR = (0, 255, 0)
INFECTED_COLOR = (255, 0, 0)
ASYMPTOMATIC_COLOR = (255, 105, 180)
RECOVERED_COLOR = (0, 0, 255)
DEAD_COLOR = (0, 0, 0)
BACKGROUND_COLOR = (240, 240, 240)

COLORS = {
    'healthy': HEALTHY_COLOR,
    'infected': INFECTED_COLOR,
    'asymptomatic': ASYMPTOMATIC_COLOR,
    'recovered': RECOVERED_COLOR,
    'dead': DEAD_COLOR
}

# Disease Parameters
DEFAULT_INFECTIVITY = 0.3
DEFAULT_MORTALITY = 0.05
DEFAULT_RECOVERY = 0.1
DEFAULT_ASYMPTOMATIC = 0.2

# 추가 검증을 위한 상수 (필요 시 추가)
TOTAL_ORIGINAL_POPULATION = sum([
    600, 400, 450, 350, 300, 350, 300, 300, 250, 200  # 각 도시의 original_population
])

# 추가된 부분
TIME_SCALE = 1/60  # 1 real second = 1/60 game day (1분에 1일 경과)
