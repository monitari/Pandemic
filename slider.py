# slider.py (신규 추가)
import pygame

class Slider:
    def __init__(self, x, y, width, label, min_val, max_val, initial_val):
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
        self.label = label
        self.min = min_val
        self.max = max_val
        self.value = initial_val
        self.dragging = False
        
        # 슬라이더 요소 계산
        self.slider_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.handle_rect = pygame.Rect(
            self.x + (self.value - self.min)/(self.max - self.min) * self.width - 5,
            self.y - 2,
            10,
            self.height + 4
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.handle_rect.x = max(self.x, min(event.pos[0] - 5, self.x + self.width - 5))
            self.value = self.min + (self.handle_rect.x - self.x) / self.width * (self.max - self.min)

    def draw(self, screen):
        font = pygame.font.SysFont('malgungothic', 12)
        # 슬라이더 바
        pygame.draw.rect(screen, (200, 200, 200), self.slider_rect)
        # 핸들
        pygame.draw.rect(screen, (50, 150, 250), self.handle_rect)
        # 라벨 및 값
        text = font.render(f"{self.label}: {self.value:.2f}", True, (0, 0, 0))
        screen.blit(text, (self.x, self.y - 25))