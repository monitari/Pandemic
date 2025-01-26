# city.py (업데이트 버전)
import pygame
import numpy as np
import cupy as cp
from person import Person
from collections import defaultdict
from constants import COLORS, INFECTION_RADIUS_SQ, GRID_SIZE, UPDATE_INTERVAL
import pygame.gfxdraw as gfxdraw

class City:
    def __init__(self, name, x, y, population):
        self.name = name
        self.x, self.y = x, y
        self.population = population
        self.original_population = population  # 원래 인구수 저장
        self.radius = 80  # 도시 반경
        self.connected_cities = []
        self.people = [Person(self, x, y) for _ in range(population)]
        self.travelers = []  # 이동 중인 사람들
        self.spatial_grid = defaultdict(list)
        self.grid_size = 30
        self._last_grid_update = 0
        self.grid_update_interval = 0.1  # Update grid every 100ms

    def connect(self, other_city):
        if other_city not in self.connected_cities:
            self.connected_cities.append(other_city)

    def exchange_people(self):
        """연결된 도시와 무작위로 일부 인원을 교환한다."""
        import random
        if not self.connected_cities:
            return
        for other_city in self.connected_cities:
            # 각 도시의 현재 거주자 중에서 교환
            num_exchange = random.randint(0, min(5, len(self.people)))
            for _ in range(num_exchange):
                if self.people:
                    person = self.people.pop()
                    person.city = other_city  # 현재 도시만 변경
                    other_city.people.append(person)
                    # home_city는 변경하지 않음

    def update_spatial_index(self):
        current_time = pygame.time.get_ticks() / 1000
        if current_time - self._last_grid_update >= self.grid_update_interval:
            self.spatial_grid.clear()
            for p in self.people:
                if p.is_healthy():
                    grid_pos = (int(p.x // self.grid_size), int(p.y // self.grid_size))
                    self.spatial_grid[grid_pos].append(p)
            self._last_grid_update = current_time

    def update(self, disease, dt):
        self.update_spatial_index()
        
        # 도시 간 이동 처리
        for person in self.people[:]:  # 복사본으로 반복
            person.update(disease, dt)
            if person.check_travel(self):
                target_city = np.random.choice(self.connected_cities)
                travel_prob = np.random.uniform(0.01, 0.05)
                if np.random.rand() < travel_prob:
                    self.people.remove(person)
                    person.target_city = target_city
                    self.travelers.append(person)
        
        # 이동 중인 사람들 업데이트
        for traveler in self.travelers[:]:
            traveler.update_travel(dt)
            if traveler.reached_destination():
                traveler.city = traveler.target_city  # 현재 도시만 변경
                traveler.target_city = None
                self.travelers.remove(traveler)
                traveler.city.people.append(traveler)  # 목적지 도시에 추가

        # 감염 전파 처리 성능 최적화
        infected_people = [p for p in self.people if p.is_infected()]
        if infected_people:  # 감염자가 있을 때만 검사
            # Vectorized infection checking
            infected_pos = cp.array([(p.x, p.y) for p in infected_people])
            healthy_people = [p for p in self.people if p.is_healthy()]
            healthy_pos = cp.array([(p.x, p.y) for p in healthy_people])

            if len(infected_pos) > 0 and len(healthy_pos) > 0:
                dx = infected_pos[:, cp.newaxis, 0] - healthy_pos[cp.newaxis, :, 0]
                dy = infected_pos[:, cp.newaxis, 1] - healthy_pos[cp.newaxis, :, 1]
                distances_sq = dx**2 + dy**2
                infection_mask = (distances_sq < INFECTION_RADIUS_SQ).any(axis=0).get()

                for i, person in enumerate(healthy_people):
                    if infection_mask[i]:
                        person.try_infect(disease)

        # 인접 도시의 사람들과의 감염 전파 처리
        if infected_people:
            infected_pos = cp.array([(p.x, p.y) for p in infected_people])
            for other_city in self.connected_cities:
                healthy_in_other = [p for p in other_city.people if p.is_healthy()]
                if not healthy_in_other:
                    continue
                
                healthy_pos = cp.array([(p.x, p.y) for p in healthy_in_other])
                dx = infected_pos[:, cp.newaxis, 0] - healthy_pos[cp.newaxis, :, 0]
                dy = infected_pos[:, cp.newaxis, 1] - healthy_pos[cp.newaxis, :, 1]
                distances_sq = dx**2 + dy**2
                adjacent_mask = (distances_sq < 225).any(axis=0).get()
                
                for i, person in enumerate(healthy_in_other):
                    if adjacent_mask[i]:
                        person.try_infect(disease)

        self.exchange_people()

    def draw(self, screen, camera):
        # 도시 원 그리기
        screen_pos = camera.world_to_screen((self.x, self.y))
        radius = int(self.radius * camera.scale)
        pygame.draw.circle(screen, (200, 200, 200), screen_pos, radius, 2)
        
        # Batch rendering by state
        for state in ['healthy', 'infected', 'asymptomatic', 'recovered', 'dead']:
            people_group = [p for p in self.people if p.state == state]
            if people_group:
                positions = [camera.world_to_screen((p.x, p.y)) for p in people_group]
                radius = max(2, int(3 * camera.scale))
                for pos in positions:
                    gfxdraw.aacircle(screen, int(pos[0]), int(pos[1]), radius, COLORS[state])
                    gfxdraw.filled_circle(screen, int(pos[0]), int(pos[1]), radius, COLORS[state])
        
        # 이동 중인 사람들 그리기
        for traveler in self.travelers:
            traveler.draw(screen, camera)

    def infect_person_near(self, world_pos, disease):
        for person in self.people:
            dx = person.x - world_pos[0]
            dy = person.y - world_pos[1]
            if dx**2 + dy**2 < 100:  # 10px 반경 내
                person.infect(disease)
                break

    def get_stats(self):
        stats = {
            'healthy': 0,
            'infected': 0,
            'asymptomatic': 0,
            'recovered': 0,
            'dead': 0
        }
        # 현재 도시에 있는 모든 사람 카운트 (홈 도시 무관)
        for p in self.people:
            stats[p.state] += 1
        # 현재 이동 중인 사람들 카운트 (목적지 도시 기준)
        for p in self.travelers:
            stats[p.state] += 1
        return stats