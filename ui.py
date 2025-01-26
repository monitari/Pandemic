import pygame
from slider import Slider
import random
from pygame import gfxdraw
from constants import COLORS  # COLORS 임포트 추가

# 색상 상수 정의
HEALTHY_COLOR = (0, 255, 0)
INFECTED_COLOR = (255, 0, 0)
ASYMPTOMATIC_COLOR = (255, 105, 180)
RECOVERED_COLOR = (0, 0, 255)
DEAD_COLOR = (0, 0, 0)

class UI:
    def __init__(self, screen, cities, disease):
        self.screen = screen
        self.cities = cities
        self.disease = disease
        self.font = pygame.font.SysFont('malgungothic', 12)
        self.infectivity = 0.3
        self.mortality_rate = 0.05
        self.recovery_rate = 0.1
        self.legend = [
            ("건강한", HEALTHY_COLOR),
            ("감염된", INFECTED_COLOR),
            ("무증상", ASYMPTOMATIC_COLOR),
            ("회복된", RECOVERED_COLOR),
            ("사망한", DEAD_COLOR)
        ]
        self.screen_width, self.screen_height = screen.get_size()
        self.panel_width = int(self.screen_width * 0.35)  # 패널 너비
        
        # 슬라이더 생성 위치를 동적으로 계산
        self.sliders = [
            Slider(self.screen_width - self.panel_width + 50, 50, 200, "감염률", 0.1, 0.9, disease.infectivity),
            Slider(self.screen_width - self.panel_width + 50, 100, 200, "치사율", 0.01, 0.5, disease.mortality_rate),
            Slider(self.screen_width - self.panel_width + 50, 150, 200, "회복률", 0.05, 0.5, disease.recovery_rate),
            Slider(self.screen_width - self.panel_width + 50, 200, 200, "무증상율", 0.1, 0.8, disease.asymptomatic_rate)
        ]
        
        self.sliders.append(
            Slider(self.screen_width - self.panel_width + 50, 250, 200, "항체 발생률", 0.0, 1.0, disease.antibody_rate)
        )
        
        # 버튼 영역 동적 위치 설정
        self.apply_rect = pygame.Rect(self.screen_width - self.panel_width + 50, 300, 200, 40)
        self.logs = [] # 로그 추가
        self._cached_stats = {}
        self._last_stats_update = 0
        self._stats_update_interval = 0.5  # 0.5초마다 통계 업데이트

    def handle_event(self, event, disease):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.apply_rect.collidepoint(event.pos):
                self.update_disease_params()
                return True  # 이벤트 처리됨을 반환
            for slider in self.sliders:
                if slider.handle_rect.collidepoint(event.pos):
                    slider.handle_event(event)
                    return True  # 이벤트 처리됨을 반환
        elif event.type in [pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
            for slider in self.sliders:
                if slider.dragging:
                    slider.handle_event(event)
                    return True  # 이벤트 처리됨을 반환
        return False  # 이벤트 처리되지 않음

    def update_disease_params(self):
        self.disease.infectivity = self.sliders[0].value
        self.disease.mortality_rate = self.sliders[1].value
        self.disease.recovery_rate = self.sliders[2].value
        self.disease.asymptomatic_rate = self.sliders[3].value
        self.disease.antibody_rate = self.sliders[4].value  # 추가된 슬라이더 값을 적용

    def update(self):
        pass

    def draw(self, camera, fps):
        # 화면 크기 동적 업데이트
        self.screen_width, self.screen_height = self.screen.get_size()
        panel = pygame.Rect(self.screen_width - self.panel_width, 0, self.panel_width, self.screen_height)
        pygame.draw.rect(self.screen, (255, 255, 255), panel)
        
        # 슬라이더 위치 업데이트
        for i, slider in enumerate(self.sliders):
            slider.y = 50 + i * 50
            slider.draw(self.screen)
            
        # 적용 버튼 위치 업데이트
        self.apply_rect.x = self.screen_width - self.panel_width + 50
        pygame.draw.rect(self.screen, (50, 150, 50), self.apply_rect)
        text = self.font.render("매개변수 적용", True, (255, 255, 255))
        self.screen.blit(text, (self.apply_rect.x + 10, self.apply_rect.y + 10))
        
        # 통계 정보 캐싱 및 업데이트
        current_time = pygame.time.get_ticks() / 1000
        if current_time - self._last_stats_update >= self._stats_update_interval:
            self._cached_stats = {city: city.get_stats() for city in self.cities}
            self._last_stats_update = current_time

        # 캐시된 통계 정보 표시
        y = 400
        total_stats = {'healthy': 0, 'infected': 0, 'asymptomatic': 0, 'recovered': 0, 'dead': 0}
        for city in self.cities:
            stats = self._cached_stats.get(city, city.get_stats())
            total = sum(stats.values())
            discrepancy = total - city.original_population
            discrepancy_text = ""
            if discrepancy != 0:
                discrepancy_text = f" (차이: {discrepancy})"

            text = self.font.render(
                f"{city.name}: 인구 {total}/{city.original_population}{discrepancy_text} "
                f"(건강 {stats['healthy']} 감염 {stats['infected']} "
                f"무증상 {stats['asymptomatic']} 회복 {stats['recovered']} "
                f"사망 {stats['dead']})",
                True, (0, 0, 0)
            )
            self.screen.blit(text, (self.screen_width - self.panel_width + 50, y))
            y += 20

            # 총합 계산
            for key in total_stats:
                total_stats[key] += stats[key]

        # 총합 표시
        total_text = self.font.render(
            f"총합: 건강 {total_stats['healthy']} 감염 {total_stats['infected']} "
            f"무증상 {total_stats['asymptomatic']} 회복 {total_stats['recovered']} "
            f"사망 {total_stats['dead']}",
            True, (0, 0, 0)
        )
        self.screen.blit(total_text, (self.screen_width - self.panel_width + 50, y))
        y += 30

        # 동일 상태의 사람들 일괄 렌더링
        for state in ['healthy', 'infected', 'asymptomatic', 'recovered', 'dead']:
            people_group = [p for city in self.cities for p in city.people if p.state == state]
            if people_group:
                positions = [camera.world_to_screen((p.x, p.y)) for p in people_group]
                radius = max(2, int(3 * camera.scale))
                for pos in positions:
                    gfxdraw.aacircle(self.screen, int(pos[0]), int(pos[1]), radius, COLORS[state])
                    gfxdraw.filled_circle(self.screen, int(pos[0]), int(pos[1]), radius, COLORS[state])

        # 로그 표시
        log_y = self.screen_height - 50
        for log in reversed(self.logs):
            text = self.font.render(log, True, (255, 0, 0))
            self.screen.blit(text, (self.screen_width - self.panel_width + 50, log_y))
            log_y -= 20

        # 프레임 표시
        fps_text = self.font.render(f"FPS: {fps:.2f}", True, (0, 0, 0))
        self.screen.blit(fps_text, (10, 10))

    def draw_legend(self):
        x, y = 10, 50
        for label, color in self.legend:
            pygame.draw.circle(self.screen, color, (x, y), 5)
            text = self.font.render(label, True, (0, 0, 0))
            self.screen.blit(text, (x + 15, y - 5))
            y += 20
