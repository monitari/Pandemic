# main.py (업데이트 버전)
import pygame
import numpy as np
from camera import Camera
from city import City
from disease import Disease
from ui import UI
import cProfile
import pstats

# 화면 설정
WIDTH, HEIGHT = 1500, 800
BACKGROUND_COLOR = (240, 240, 240)

# 초기화
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pandemic Simulation Game")
clock = pygame.time.Clock()

# 카메라 시스템 초기화
camera = Camera()

# 도시 생성 함수
def create_cities():
    cities = [
        City("Seoul", 200, 150, 600),
        City("Busan", 1200, 700, 400),
        City("Daegu", 600, 500, 450),
        City("Incheon", 1000, 300, 350),
        City("Gwangju", 800, 800, 300),
        City("Daejeon", 700, 400, 350),
        City("Ulsan", 1300, 500, 300),
        City("Suwon", 500, 350, 300),
        City("Changwon", 1100, 800, 250),
        City("Jeonju", 900, 600, 200)
    ]
    
    # 가장 가까운 도시들끼리 연결
    for city in cities:
        for other_city in cities:
            if city != other_city:
                distance = np.sqrt((city.x - other_city.x)**2 + (city.y - other_city.y)**2)
                if distance < 500:
                    city.connect(other_city)

    return cities

# 게임 초기화
cities = create_cities()
disease = Disease()
ui = UI(screen, cities, disease)

# 게임 루프
def main():
    global screen  # 전역 변수로 선언
    running = True
    
    # 프로파일러 시작
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        while running:
            screen.fill(BACKGROUND_COLOR)
            
            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    ui.screen_width, ui.screen_height = event.w, event.h
                    ui.panel_width = int(ui.screen_width * 0.35)  # 패널 너비 업데이트
                    ui.apply_rect = pygame.Rect(ui.screen_width - ui.panel_width + 50, 250, 200, 40)
                # UI 이벤트 처리
                if not ui.handle_event(event, disease):
                    # UI 이벤트가 처리되지 않은 경우에만 카메라 이벤트 처리
                    camera.handle_event(event)
                # 개인 클릭 이벤트
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = camera.screen_to_world(pygame.mouse.get_pos())
                    for city in cities:
                        city.infect_person_near(mouse_pos, disease)

            # 시스템 업데이트
            dt = clock.tick(60) / 1000  # 초당 60프레임으로 설정
            fps = clock.get_fps() # FPS 계산
            for city in cities:
                city.update(disease, dt)
                city.draw(screen, camera)
            
            # UI 렌더링
            ui.draw(camera, fps)

            pygame.display.flip()
            
    finally:
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats(20)  # 상위 20개 시간 소모 함수 출력

    pygame.quit()

if __name__ == "__main__":
    main()