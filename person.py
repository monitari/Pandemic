# person.py (업데이트 버전)
import pygame
import random
import numpy as np
import math
from constants import COLORS, UPDATE_INTERVAL, TIME_SCALE

class Person:
    __slots__ = ['x', 'y', 'state', 'city', 'home_city', 'age', 'infection_day',  # home_city 추가
                 'asymptomatic', 'color', 'target_city', 'speed', 'angle',
                 '_position_cache', '_last_update_time', 'antibody_level']  # 항체 레벨 추가

    def __init__(self, city, x, y):
        self.city = city
        self.home_city = city  # 원래 소속 도시 저장
        self.x = x + random.uniform(-city.radius, city.radius)
        self.y = y + random.uniform(-city.radius, city.radius)
        self.age = random.randint(10, 80)
        self.state = 'healthy'
        self.infection_day = 0
        self.asymptomatic = False
        self.update_color()
        self.target_city = None  # 목표 도시
        self.antibody_level = 0.0  # 항체 레벨

        # 이동 관련 파라미터
        self.speed = random.uniform(0.5, 1.5)
        self.angle = random.uniform(0, 2*np.pi)
        self._position_cache = None
        self._last_update_time = pygame.time.get_ticks() / 1000

    def update(self, disease, dt):
        if self.state == 'dead':
            return

        current_time = pygame.time.get_ticks() / 1000
        if current_time - self._last_update_time >= UPDATE_INTERVAL:
            if random.random() < 0.02:
                self.angle = random.uniform(0, 2 * np.pi)

            movement = np.array([
                np.cos(self.angle) * self.speed * UPDATE_INTERVAL * 60,
                np.sin(self.angle) * self.speed * UPDATE_INTERVAL * 60
            ])

            new_pos = np.array([self.x, self.y]) + movement
            if np.sum((new_pos - [self.city.x, self.city.y])**2) < (self.city.radius**2) * 0.9:
                self.x, self.y = new_pos

            self._last_update_time = current_time
            self._position_cache = None

        # 시간 스케일 적용된 상태 업데이트
        self.infection_day += dt * TIME_SCALE  # 게임 일수 누적

        if self.state in ['infected', 'asymptomatic']:
            mortality = disease.mortality_rate * (1 + self.age / 100)
            recovery = disease.recovery_rate * (1 - self.age / 200)

            # 시간 스케일 적용 확률 계산
            mortality_prob = mortality * dt * TIME_SCALE
            recovery_prob = recovery * dt * TIME_SCALE

            if random.random() < mortality_prob:
                self.state = 'dead'
                self.update_color()
            elif random.random() < recovery_prob:
                self.state = 'recovered'
                self.update_color()

    def update_travel(self, dt):
        if self.target_city:
            dx = self.target_city.x - self.x
            dy = self.target_city.y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 5:  # 도착 판정
                self.x = self.target_city.x
                self.y = self.target_city.y
                return True
            
            speed = 150 * dt  # 초당 150픽셀 이동
            self.x += dx/dist * speed
            self.y += dy/dist * speed
        return False

    def reached_destination(self):
        if self.target_city:
            distance_sq = (self.x - self.target_city.x)**2 + (self.y - self.target_city.y)**2
            return distance_sq < 100  # 목표 도시에 도착한 것으로 간주
        return False

    def try_infect(self, disease):
        if self.is_healthy():
            # 항체 레벨 적용
            infection_chance = disease.infectivity * (1.0 - self.antibody_level)
            if random.random() < infection_chance:
                self.infect(disease)

    def infect(self, disease):
        self.state = 'asymptomatic' if random.random() < disease.asymptomatic_rate else 'infected'
        self.infection_day = 0
        # 항체 발생률 고려
        if random.random() < disease.antibody_rate:
            self.antibody_level = random.uniform(0.2, 0.8)
        self.update_color()

    def check_travel(self, current_city):
        return random.random() < 0.01 and len(current_city.connected_cities) > 0

    def update_color(self):
        self.color = COLORS[self.state]  # COLORS 사용

    def draw(self, screen, camera):
        if self.state == 'dead':
            return
        screen_pos = camera.world_to_screen((self.x, self.y))
        pygame.draw.circle(screen, self.color, screen_pos, max(2, int(3 * camera.scale)))

    def is_healthy(self):
        return self.state == 'healthy'

    def is_infected(self):
        return self.state in ['infected', 'asymptomatic']