# disease.py: 질병 클래스 정의
import pygame
from slider import Slider
import random

class Disease:
    def __init__(self):
        self.infectivity = 0.3
        self.mortality_rate = 0.05
        self.recovery_rate = 0.1
        self.asymptomatic_rate = 0.2
        self.mutation_history = []  # 변이 기록 추가
        self.antibody_rate = 0.2  # 항체 발생률 추가

    def get_mutation_history(self):
        return self.mutation_history