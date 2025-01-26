#camera.py
import pygame
import cupy as cp

class Camera:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.dragging = False
        self.last_mouse = (0, 0)
        self.last_mouse_world = (0, 0)

    def handle_event(self, event):
        # 마우스 드래그 처리
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 왼쪽 버튼
                self.dragging = True
                self.last_mouse = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.last_mouse[0]
            dy = event.pos[1] - self.last_mouse[1]
            self.offset_x -= dx / self.scale
            self.offset_y -= dy / self.scale
            self.last_mouse = event.pos
        elif event.type == pygame.MOUSEWHEEL:
            # 확대/축소 처리
            zoom_factor = 1.1
            mouse_pos = pygame.mouse.get_pos()
            mouse_world_before_zoom = self.screen_to_world(mouse_pos)
            if event.y > 0:
                self.scale *= zoom_factor
            elif event.y < 0:
                self.scale /= zoom_factor
            self.scale = max(0.5, min(self.scale, 5.0))
            mouse_world_after_zoom = self.screen_to_world(mouse_pos)
            self.offset_x += mouse_world_before_zoom[0] - mouse_world_after_zoom[0]
            self.offset_y += mouse_world_before_zoom[1] - mouse_world_after_zoom[1]

    def world_to_screen(self, world_pos):
        x = (world_pos[0] - self.offset_x) * self.scale
        y = (world_pos[1] - self.offset_y) * self.scale
        return (int(x), int(y))

    def screen_to_world(self, screen_pos):
        x = screen_pos[0] / self.scale + self.offset_x
        y = screen_pos[1] / self.scale + self.offset_y
        return (x, y)

    def batch_world_to_screen(self, positions_gpu):
        x = (positions_gpu[:, 0] - self.offset_x) * self.scale
        y = (positions_gpu[:, 1] - self.offset_y) * self.scale
        return cp.stack([x, y], axis=1).astype(cp.int32)