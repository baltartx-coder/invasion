import pygame
import random
import math

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
ANCHO, ALTO = 640, 480
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego Simple")

# Cargar imagen del personaje y enemigo
try:
    sprite = pygame.image.load("fulano.png.png")
    enemigo_img = pygame.image.load("strngerious.png")
    atacante = pygame.image.load("bloodious.gif") 
    suelo = pygame.image.load("suelo.jpg")

    boss_img = pygame.image.load("bossious.gif")
    boss_img = pygame.transform.scale(boss_img, (boss_img.get_width() * 2, boss_img.get_height() * 2))

    # Nueva imagen para la moneda
    moneda_img = pygame.image.load("coin.png") 

except pygame.error as e:
    print(f"Error al cargar imagen: {e}")
    print("Asegúrate de que todas las imágenes estén en la misma carpeta que el script.")
    pygame.quit()
    exit()

sprite_rect = sprite.get_rect()
sprite_rect.topleft = (ANCHO // 2, ALTO // 2)

boss_img_rect = boss_img.get_rect()
boss_img_rect.topleft = (0, 0) # Posición inicial del jefe: esquina superior izquierda

# Variables del juego
VELOCIDAD = 5
VELOCIDAD_ENEMIGOS = 2
VELOCIDAD_ATACANTE = 1 
VELOCIDAD_BOSS = 1 
vida_boss = 20
boss_aparece = False
victoria = False 
vidas = 3 # Vidas iniciales del personaje

# Temporizadores y listas
ultimo_disparo_boss = pygame.time.get_ticks()
intervalo_disparo_boss = random.randint(1500, 3000)
tiempo_ultimo_enemigo = pygame.time.get_ticks()
intervalo_generacion_enemigo = 3000
incremento_intervalo = 50
tiempo_ultimo_atacante = pygame.time.get_ticks()
intervalo_generacion_atacante = 10000 
tiempo_ultima_moneda = pygame.time.get_ticks()
intervalo_generacion_moneda = 5000 # Intervalo para generar monedas

enemigos = []
enemigos_atacantes = [] 
proyectiles = []
proyectiles_enemigos = [] 
proyectiles_boss = []
monedas = [] # Lista para almacenar las monedas

# --- BOMBA ---
tiempo_ultima_bomba = pygame.time.get_ticks() - 20000  # Permite tirar la bomba al inicio
intervalo_bomba = 20000  # 20 segundos
bomba_efecto_tiempo = 0
bomba_efecto_duracion = 1000  # 1 segundo para mostrar el efecto

# Clase para los proyectiles
class Proyectil:
    def __init__(self, x_inicio, y_inicio, x_objetivo, y_objetivo, es_enemigo=False):
        self.radio = 5
        self.color = (255, 0, 0)
        self.velocidad = 10
        self.pos_x = float(x_inicio)
        self.pos_y = float(y_inicio)
        self.es_enemigo = es_enemigo 
        if self.es_enemigo:
            self.color = (0, 0, 255)

        self.dx = x_objetivo - x_inicio
        self.dy = y_objetivo - y_inicio
        dist = math.hypot(self.dx, self.dy)
        if dist != 0:
            self.dx /= dist
            self.dy /= dist
        else:
            self.dx = 0
            self.dy = 0

    def actualizar(self):
        self.pos_x += self.dx * self.velocidad
        self.pos_y += self.dy * self.velocidad

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, self.color, (int(self.pos_x), int(self.pos_y)), self.radio)

    def get_rect(self):
        return pygame.Rect(self.pos_x - self.radio, self.pos_y - self.radio, self.radio * 2, self.radio * 2)

    def esta_fuera_de_pantalla(self, ancho_pantalla, alto_pantalla):
        return (self.pos_x < -self.radio or self.pos_x > ancho_pantalla + self.radio or
                self.pos_y < -self.radio or self.pos_y > alto_pantalla + self.radio)

# Clase para el enemigo atacante (Bloodius)
class EnemigoAtacante(pygame.Rect):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.ultima_vez_disparo = pygame.time.get_ticks()
        self.velocidad = VELOCIDAD_ATACANTE

    def mover(self):
        self.x += random.choice([-self.velocidad, 0, self.velocidad])
        self.y += random.choice([-self.velocidad, 0, self.velocidad])
        self.left = max(0, self.left)
        self.right = min(ANCHO, self.right)
        self.top = max(0, self.top)
        self.bottom = min(ALTO, self.bottom)

    def disparar(self, jugador_pos):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultima_vez_disparo > 3000:
            proyectil_atacante = Proyectil(self.centerx, self.centery, jugador_pos[0], jugador_pos[1], es_enemigo=True)
            self.ultima_vez_disparo = ahora
            return proyectil_atacante
        return None

# Nueva clase para las monedas
class Moneda(pygame.Rect):
    def __init__(self, x, y):
        self.img = pygame.transform.scale(moneda_img, (20, 20))
        super().__init__(x, y, self.img.get_width(), self.img.get_height())
        self.tiempo_creacion = pygame.time.get_ticks()
        self.duracion = 7000 # La moneda dura 7 segundos

# Configuración de FPS
FPS = 60
reloj = pygame.time.Clock()

# Bucle de inicio
inicio_juego = True
tiempo_inicio = pygame.time.get_ticks()
fuente_inicio = pygame.font.Font(None, 50)
texto_inicio = fuente_inicio.render("¿Listo para combatir?", True, (255, 255, 255))
texto_rect_inicio = texto_inicio.get_rect(center=(ANCHO // 2, ALTO // 2))

while inicio_juego:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()

    pantalla.fill((0,0,0)) # Fondo negro para el mensaje
    pantalla.blit(texto_inicio, texto_rect_inicio)
    pygame.display.flip()

    if pygame.time.get_ticks() - tiempo_inicio > 3000:
        inicio_juego = False

# Bucle principal del juego
ejecutando = True
game_over = False
Puntaje = 0
fuente_puntaje = pygame.font.Font(None,36)

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if evento.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if evento.button == 1:
                personaje_centro_x, personaje_centro_y = sprite_rect.center
                mouse_x, mouse_y = evento.pos
                nuevo_proyectil = Proyectil(personaje_centro_x, personaje_centro_y, mouse_x, mouse_y)
                proyectiles.append(nuevo_proyectil)

    if not game_over:
        # Lógica para que el boss aparezca
        #el puntaje para que el boss aparezca
        if Puntaje >= 1000 and not boss_aparece:
            boss_aparece = True
            vida_boss = 20

        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_LEFT]: sprite_rect.x -= VELOCIDAD
        if teclas[pygame.K_RIGHT]: sprite_rect.x += VELOCIDAD
        if teclas[pygame.K_UP]: sprite_rect.y -= VELOCIDAD
        if teclas[pygame.K_DOWN]: sprite_rect.y += VELOCIDAD

        sprite_rect.left = max(0, sprite_rect.left)
        sprite_rect.right = min(ANCHO, sprite_rect.right)
        sprite_rect.top = max(0, sprite_rect.top)
        sprite_rect.bottom = min(ALTO, sprite_rect.bottom)

        # --- BOMBA ---
        tiempo_actual = pygame.time.get_ticks()
        if teclas[pygame.K_z] and (tiempo_actual - tiempo_ultima_bomba > intervalo_bomba):
            # Estalla la bomba
            enemigos.clear()
            enemigos_atacantes.clear()
            proyectiles_enemigos.clear()
            proyectiles_boss.clear()
            Puntaje += 100
            tiempo_ultima_bomba = tiempo_actual
            bomba_efecto_tiempo = tiempo_actual  # Para mostrar el efecto

        # Generar nuevos enemigos (Strngerious)
        if tiempo_actual - tiempo_ultimo_enemigo > intervalo_generacion_enemigo:
            lado = random.choice(["arriba", "abajo", "izquierda", "derecha"])
            if lado == "arriba":
                x = random.randint(0, ANCHO - enemigo_img.get_width())
                y = -enemigo_img.get_height()
            elif lado == "abajo":
                x = random.randint(0, ANCHO - enemigo_img.get_width())
                y = ALTO
            elif lado == "izquierda":
                x = -enemigo_img.get_width()
                y = random.randint(0, ALTO - enemigo_img.get_height())
            else:
                x = ANCHO
                y = random.randint(0, ALTO - enemigo_img.get_height())

            enemigo_rect = enemigo_img.get_rect(topleft=(x, y))
            enemigos.append(enemigo_rect)
            tiempo_ultimo_enemigo = tiempo_actual
            intervalo_generacion_enemigo = max(200, intervalo_generacion_enemigo - incremento_intervalo)

        # Generar nuevos atacantes (Bloodius)
        if tiempo_actual - tiempo_ultimo_atacante > intervalo_generacion_atacante:
            x = random.randint(0, ANCHO - atacante.get_width())
            y = random.randint(0, ALTO - atacante.get_height())
            nuevo_atacante = EnemigoAtacante(x, y, atacante.get_width(), atacante.get_height())
            enemigos_atacantes.append(nuevo_atacante)
            tiempo_ultimo_atacante = tiempo_actual

        # Generar monedas
        if tiempo_actual - tiempo_ultima_moneda > intervalo_generacion_moneda:
            x = random.randint(0, ANCHO - moneda_img.get_width())
            y = random.randint(0, ALTO - moneda_img.get_height())
            nueva_moneda = Moneda(x, y)
            monedas.append(nueva_moneda)
            tiempo_ultima_moneda = tiempo_actual

        # Mover enemigos y actualizar proyectiles (el código de esta sección no cambia)
        for enemigo_rect in enemigos:
            dx = sprite_rect.centerx - enemigo_rect.centerx
            dy = sprite_rect.centery - enemigo_rect.centery
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx_norm = dx / dist
                dy_norm = dy / dist
            else:
                dx_norm = 0
                dy_norm = 0
            enemigo_rect.x += dx_norm * VELOCIDAD_ENEMIGOS
            enemigo_rect.y += dy_norm * VELOCIDAD_ENEMIGOS

        if boss_aparece and not victoria:
            dx_boss = sprite_rect.centerx - boss_img_rect.centerx
            dy_boss = sprite_rect.centery - boss_img_rect.centery
            dist_boss = math.hypot(dx_boss, dy_boss)
            if dist_boss != 0:
                boss_img_rect.x += (dx_boss / dist_boss) * VELOCIDAD_BOSS
                boss_img_rect.y += (dy_boss / dist_boss) * VELOCIDAD_BOSS
            boss_img_rect.left = max(0, boss_img_rect.left)
            boss_img_rect.right = min(ANCHO, boss_img_rect.right)
            boss_img_rect.top = max(0, boss_img_rect.top)
            boss_img_rect.bottom = min(ALTO, boss_img_rect.bottom)

            ahora = pygame.time.get_ticks()
            if ahora - ultimo_disparo_boss > intervalo_disparo_boss:
                proyectil_jefe = Proyectil(boss_img_rect.centerx, boss_img_rect.centery, sprite_rect.centerx, sprite_rect.centery, es_enemigo=True)
                proyectiles_boss.append(proyectil_jefe)
                ultimo_disparo_boss = ahora
                intervalo_disparo_boss = random.randint(1500, 3000)

        for atacante_rect in enemigos_atacantes:
            atacante_rect.mover()
            proyectil_disparado = atacante_rect.disparar(sprite_rect.center)
            if proyectil_disparado:
                proyectiles_enemigos.append(proyectil_disparado)

        proyectiles_a_mantener = []
        for proyectil in proyectiles:
            proyectil.actualizar()
            if not proyectil.esta_fuera_de_pantalla(ANCHO, ALTO):
                proyectiles_a_mantener.append(proyectil)
        proyectiles = proyectiles_a_mantener

        proyectiles_enemigos_a_mantener = []
        for proyectil in proyectiles_enemigos:
            proyectil.actualizar()
            if not proyectil.esta_fuera_de_pantalla(ANCHO, ALTO):
                proyectiles_enemigos_a_mantener.append(proyectil)
        proyectiles_enemigos = proyectiles_enemigos_a_mantener

        proyectiles_boss_a_mantener = []
        for proyectil in proyectiles_boss:
            proyectil.actualizar()
            if not proyectil.esta_fuera_de_pantalla(ANCHO, ALTO):
                proyectiles_boss_a_mantener.append(proyectil)
        proyectiles_boss = proyectiles_boss_a_mantener

        # Lógica de colisiones con los enemigos y proyectiles
        if sprite_rect.colliderect(boss_img_rect) and boss_aparece and not victoria:
            vidas -= 1
            if vidas <= 0:
                game_over = True

        for enemigo_rect in enemigos:
            if enemigo_rect.colliderect(sprite_rect):
                vidas -= 1
                enemigos.remove(enemigo_rect)
                if vidas <= 0:
                    game_over = True
                break

        for proyectil_enemigo in proyectiles_enemigos:
            if proyectil_enemigo.get_rect().colliderect(sprite_rect):
                vidas -= 1
                proyectiles_enemigos.remove(proyectil_enemigo)
                if vidas <= 0:
                    game_over = True
                break

        for proyectil_boss_shot in proyectiles_boss:
            if proyectil_boss_shot.get_rect().colliderect(sprite_rect):
                vidas -= 1
                proyectiles_boss.remove(proyectil_boss_shot)
                if vidas <= 0:
                    game_over = True
                break

        # Lógica de colisiones de los proyectiles del jugador
        enemigos_vivos = []
        for enemigo_rect in enemigos:
            enemigo_golpeado = False
            proyectiles_a_mantener_temp = []
            for proyectil in proyectiles:
                if proyectil.get_rect().colliderect(enemigo_rect):
                    Puntaje +=10
                    enemigo_golpeado = True
                else:
                    proyectiles_a_mantener_temp.append(proyectil)
            proyectiles = proyectiles_a_mantener_temp
            if not enemigo_golpeado:
                enemigos_vivos.append(enemigo_rect)
        enemigos = enemigos_vivos

        atacantes_vivos = []
        for atacante_rect in enemigos_atacantes:
            atacante_golpeado = False
            proyectiles_a_mantener_despues_de_atacante = []
            for proyectil in proyectiles:
                if proyectil.get_rect().colliderect(atacante_rect):
                    Puntaje += 25
                    atacante_golpeado = True
                else:
                    proyectiles_a_mantener_despues_de_atacante.append(proyectil)
            proyectiles = proyectiles_a_mantener_despues_de_atacante
            if not atacante_golpeado:
                atacantes_vivos.append(atacante_rect)
        enemigos_atacantes = atacantes_vivos

        if boss_aparece and not victoria:
            proyectiles_a_mantener_despues_de_boss = []
            for proyectil in proyectiles:
                if proyectil.get_rect().colliderect(boss_img_rect):
                    vida_boss -= 1
                    if vida_boss <= 0:
                        victoria = True
                        game_over = True
                        boss_aparece = False
                        proyectiles_boss.clear()
                        Puntaje += 500 # Puntos extra por derrotar al jefe
                else:
                    proyectiles_a_mantener_despues_de_boss.append(proyectil)
            proyectiles = proyectiles_a_mantener_despues_de_boss

        # Lógica de recolección de monedas
        monedas_a_mantener = []
        for moneda in monedas:
            if sprite_rect.colliderect(moneda):
                Puntaje += 5 # Puntos por cada moneda
            else:
                if pygame.time.get_ticks() - moneda.tiempo_creacion < moneda.duracion:
                    monedas_a_mantener.append(moneda)
        monedas = monedas_a_mantener

    # --- Dibujar en la pantalla ---
    pantalla.fill((255, 255, 0))

    for x in range(0, ANCHO, suelo.get_width()):
        for y in range(0, ALTO, suelo.get_height()):
            pantalla.blit(suelo, (x, y))

    for moneda in monedas:
        pantalla.blit(moneda.img, moneda)

    pantalla.blit(sprite, sprite_rect)

    for enemigo_rect in enemigos:
        pantalla.blit(enemigo_img, enemigo_rect)

    for atacante_rect in enemigos_atacantes:
        pantalla.blit(atacante, atacante_rect)

    if boss_aparece and not victoria:
        pantalla.blit(boss_img, boss_img_rect)

    for proyectil in proyectiles:
        proyectil.dibujar(pantalla)

    for proyectil_enemigo in proyectiles_enemigos:
        proyectil_enemigo.dibujar(pantalla)

    for proyectil_boss_shot in proyectiles_boss:
        proyectil_boss_shot.dibujar(pantalla)

    # --- Efecto visual de bomba ---
    if bomba_efecto_tiempo and (pygame.time.get_ticks() - bomba_efecto_tiempo < bomba_efecto_duracion):
        s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        s.fill((255, 0, 0, 128))  # Rojo semitransparente
        pantalla.blit(s, (0, 0))
        fuente_bomba = pygame.font.Font(None, 60)
        texto_bomba = fuente_bomba.render("¡BOMBA!", True, (255,255,255))
        texto_bomba_rect = texto_bomba.get_rect(center=(ANCHO//2, ALTO//2))
        pantalla.blit(texto_bomba, texto_bomba_rect)
    elif bomba_efecto_tiempo and (pygame.time.get_ticks() - bomba_efecto_tiempo >= bomba_efecto_duracion):
        bomba_efecto_tiempo = 0

    # Dibujar información en la pantalla
    texto_puntaje = fuente_puntaje.render(f"Puntaje: {Puntaje}", True,(0,0,0))
    pantalla.blit(texto_puntaje, (10,10))

    texto_vidas = fuente_puntaje.render(f"Vidas: {vidas}", True,(0,0,0))
    pantalla.blit(texto_vidas, (10, 40))

    # --- Tiempo restante para la bomba ---
    tiempo_restante_bomba = max(0, (intervalo_bomba - (pygame.time.get_ticks() - tiempo_ultima_bomba)) // 1000)
    texto_bomba = fuente_puntaje.render(f"Bomba en: {tiempo_restante_bomba}s", True, (255,0,0))
    pantalla.blit(texto_bomba, (10, 70))

    if boss_aparece and not victoria:
        texto_vida_boss = fuente_puntaje.render(f"Vida Boss: {vida_boss}", True, (0,0,0))
        pantalla.blit(texto_vida_boss, (ANCHO - texto_vida_boss.get_width() - 10, 10))

    if game_over:
        fuente = pygame.font.Font(None, 74)
        if victoria:
            texto = fuente.render('¡VICTORIA!', True, (0, 255, 0))
        else:
            texto = fuente.render('GAME OVER', True, (255, 0, 0))
        texto_rect = texto.get_rect(center=(ANCHO // 2, ALTO // 2))
        pantalla.blit(texto, texto_rect)

    pygame.display.flip()

    reloj.tick(FPS)

pygame.quit()