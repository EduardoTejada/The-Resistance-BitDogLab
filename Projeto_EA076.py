from machine import Pin, SoftI2C, ADC
from ssd1306 import SSD1306_I2C
import utime, time, random, neopixel


# Configuração dos botões
button_a = Pin(5, Pin.IN, Pin.PULL_UP)
button_b = Pin(6, Pin.IN, Pin.PULL_UP)

# Configuração do LED RGB
red_led = Pin(12, Pin.OUT)
green_led = Pin(13, Pin.OUT)
blue_led = Pin(11, Pin.OUT)

# Desligando o LED RGB inicialmente
red_led.value(0)
green_led.value(0)
blue_led.value(0)

# Configuração OLED
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# Configuração dos pinos do joystick
vrx = ADC(Pin(27))  # Conectado ao eixo X do joystick

# Valor central esperado do joystick no eixo X
CENTRAL_X = 32768

np = neopixel.NeoPixel(machine.Pin(7), 25)

it=5# ontensidade do LED, pode variar de 1 a 255

# definir cores para os LEDs
BLU = (0, 0, 1*it)# BLUE
GRE = (0, 1*it, 0)# GREEN
RED = (1*it, 0, 0)
YEL = (1*it, 1*it, 0)# YELLOW
MAGE = (1*it, 0, 1*it)# MANGENTA
CYA = (0, 1*it, 1*it)# CYAN
WHI = (1*it, 1*it, 1*it)# WHIE
BLA = (0, 0, 0)# BLACK

heart = [
    [BLA, RED, BLA, RED, BLA],
    [RED, RED, RED, RED, RED],
    [RED, RED, RED, RED, RED],
    [BLA, RED, RED, RED, BLA],
    [BLA, BLA, RED, BLA, BLA]
]

vote_arrow = [
    [BLA, BLA, BLA, BLA, BLA],
    [BLA, RED, BLA, BLU, BLA],
    [RED, BLA, BLA, BLA, BLU],
    [BLA, RED, BLA, BLU, BLA],
    [BLA, BLA, BLA, BLA, BLA]
]

nothing = [
    [BLA, BLA, BLA, BLA, BLA],
    [BLA, BLA, BLA, BLA, BLA],
    [BLA, BLA, BLA, BLA, BLA],
    [BLA, BLA, BLA, BLA, BLA],
    [BLA, BLA, BLA, BLA, BLA]
]

mapa = [
    [WHI, WHI, WHI, WHI, WHI],
    [YEL, BLA, BLA, BLA, BLA],
    [BLA, BLA, BLA, BLA, BLA],
    [BLA, BLA, BLA, BLA, BLA],
    [BLA, BLA, BLA, BLA, BLA]
]

matriz_resultado = []


# Variáveis globais
numero_de_jogadores = 5
contador = 0 # apagar dps
estado_botao_a = 0
flag_botao_a = 0
estado_botao_b = 0
flag_botao_b = 0
missao_hover = 0
cargo = ["Assassino", "Comandante Falso", "Guarda Costas", "Comandante", "Resistencia", "Resistencia", "Agente Oculto", "Resistencia", "Resistencia", "Espiao", ""]
jogadores_missao = [3, 4, 4, 5, 5]
falhas_missao = [1, 1, 1, 2, 1]
missao = [0, 0, 0, 0, None]
missao_escolhida = None
votos_nao = [0, 0, 0, 0, 0]
num = 0
voto_atual = None


#Variável de estado
estado = 0
"""
0 - Estado inicial, seleção do número de jogadores
1 - Estado de confirmação do estado inicial
2 - Estado esperando revelar cargo
3 - Estado revelando cargo
4 - Estado escolhendo missões
5 - Estado confirmação da escolha da missão
6 - Estado de votação
7 - Estado de confirmação da votação
8 - Estado mostrando resultado da missão
9 - Estado resultado final
"""

# Função para ler o valor do eixo X do joystick
def ler_vrx():
    return vrx.read_u16()


# Função atualiza jogadores
def lerJoystick():
    valor_x = ler_vrx()
        
    # Se o valor do eixo X for maior que o valor central (movimento para a esquerda)
    if valor_x > (CENTRAL_X + 10000): #esquerda
        pos = -1
        time.sleep(0.2)  # Debounce time

    # Se o valor do eixo X for menor que o valor central (movimento para a direita)
    elif valor_x < (CENTRAL_X - 10000): #direita
        pos = 1
        time.sleep(0.2)  # Debounce time
    else:
        pos = 0
    
    # Pequena pausa para evitar sobrecarregar o processador
    time.sleep(0.1)
    
    return pos
    

def mostrarMatriz(desenho):
# definir a matriz 5x5
    led_matrix = desenho

# inverter a matriz
    inverted_matrix = led_matrix[::-1]
    inverted_matrix[0] = inverted_matrix[0][::-1]
    inverted_matrix[2] = inverted_matrix[2][::-1]
    inverted_matrix[4] = inverted_matrix[4][::-1]

# exibir a matriz invertida nos LEDs
    for i in range(5):
        for j in range(5):
            np[i*5+j] = inverted_matrix[i][j]

    np.write()

mostrarMatriz(heart)

def atualizaOled(numero_i = 0):
    global contador
    global numero_de_jogadores
    global estado
    global cargo
    global mapa
    
    oled.fill(0)  # Limpar display
    
    if estado == 0:
        oled.text("Num de jogadores: ", 0, 0)
        oled.text(str(numero_de_jogadores), 0, 10)
        oled.text("Pressione B", 0, 30)
    elif estado == 1:
        oled.text("B para confirmar", 0, 0)
        oled.text("A para voltar", 0, 10)
        oled.text("Jogadores: "+ str(numero_de_jogadores), 0, 30)
    elif estado == 2:
        oled.text("Jogador "+str(numero_i+1), 0, 0)
        oled.text("B para revelar", 0, 10)
    elif estado == 3:
        oled.text("Jogador "+str(numero_i+1), 0, 0)
        oled.text("Seu cargo e:", 0, 10)
        oled.text(str(cargo[numero_i]), 0, 20)
        oled.text("Time:", 0, 40)
        if str(cargo[numero_i]) == "Agente Oculto" or str(cargo[numero_i]) == "Comandante Falso" or str(cargo[numero_i]) == "Assassino" or str(cargo[numero_i]) == "Espiao":
            oled.text("Espioes", 0, 50)
        else:
            oled.text("Resistencia", 0, 50)
    elif estado == 4:
        if numero_i == 4 and (mapa[0][0] == WHI or mapa[0][1] == WHI or mapa[0][2] == WHI or mapa[0][3] == WHI):
            oled.text("Missao "+str(numero_i+1), 0, 0)
            oled.text("Jogadores "+str(jogadores_missao[numero_i]), 0, 10)
            oled.text("Falhas "+str(falhas_missao[numero_i]), 0, 20)        
            oled.text("Missao bloqueada", 0, 40)
            oled.text("Deixe por ultimo", 0, 50)
        else:
            oled.text("Missao "+str(numero_i+1), 0, 0)
            oled.text("Jogadores "+str(jogadores_missao[numero_i]), 0, 10)
            oled.text("Falhas "+str(falhas_missao[numero_i]), 0, 20)        
            oled.text("Selecionar: B", 0, 40)
            
    elif estado == 5:
        oled.text("B para confirmar", 0, 0)
        oled.text("A para voltar", 0, 10)
        oled.text("Missao: "+ str(numero_i+1), 0, 30)
        oled.text("Jogadores "+str(jogadores_missao[numero_i]), 0, 40)
        oled.text("Falhas "+str(falhas_missao[numero_i]), 0, 50)
    elif estado == 6:
        oled.text("Jogador "+str(numero_i+1), 0, 0)
        oled.text("", 0, 10)
        oled.text("A para rejeitar", 0, 20)
        oled.text("B para aprovar", 0, 30)
    elif estado == 7:
        oled.text("Jogador "+str(numero_i+1), 0, 0)
        oled.text("Confirma o voto?", 0, 10)
        oled.text("B para confirmar", 0, 20)
        oled.text("A para voltar", 0, 30)
    elif estado == 8:
        oled.text("Aperte B para", 0, 0)
        oled.text("revelar o", 0, 10)
        oled.text("resultado", 0, 20)
        
        
    oled.show()


def atualizaJogadores(pos):
    global numero_de_jogadores
    
    if pos == -1:
        numero_de_jogadores = numero_de_jogadores - 1 if numero_de_jogadores > 5 else 5
    elif pos == 1:
        numero_de_jogadores = numero_de_jogadores + 1 if numero_de_jogadores < 10 else 10


def confirmarNumDeJogadores():
    global estado_botao_a, estado_botao_b, estado, numero_de_jogadores, jogadores_missao
    
    atualizaOled()
    
    if button_a.value() == 0 and estado_botao_a == 0:
        estado_botao_a = 1
        estado = 0
    elif button_a.value() == 1 and estado_botao_a == 1:
        estado_botao_a = 0
    
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1
        estado = 2
        if numero_de_jogadores == 7:
            jogadores_missao = [2, 3, 3, 4, 4]
        elif numero_de_jogadores == 6:
            jogadores_missao = [2, 3, 4, 3, 4]
        elif numero_de_jogadores == 5:
            jogadores_missao = [2, 3, 2, 3, 3]
    
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0

def escolherNumDeJogadores():
    global estado
    global estado_botao_b
    
    posicaoJoystick = lerJoystick()
    atualizaJogadores(posicaoJoystick)
    atualizaOled()
    
    # Se o Botão B for pressionado
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1
        estado = 1
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0


def esperarParaRevelarCargo():
    global estado
    global estado_botao_b
    global numero_de_jogadores
    
    i = 0
    
    sortearCargos()
    
    while i < numero_de_jogadores:
        if estado == 2:
            atualizaOled(i)
            
            # Se o Botão B for pressionado
            if button_b.value() == 0 and estado_botao_b == 0:
                estado_botao_b = 1
                estado = 3
            elif button_b.value() == 1 and estado_botao_b == 1:
                estado_botao_b = 0

        elif estado == 3:
            atualizaOled(i)

            # Se o Botão B for pressionado
            if button_b.value() == 0 and estado_botao_b == 0:
                estado_botao_b = 1
                estado = 2
                i += 1
            elif button_b.value() == 1 and estado_botao_b == 1:
                estado_botao_b = 0
    
    estado = 4
    atualizaOled()

def sortearCargos():
    global numero_de_jogadores
    global cargo
    
    cargo = cargo[:numero_de_jogadores]

    last_index = numero_de_jogadores - 1

    while last_index > 0:
        rand_index = random.randint(0, last_index)
        cargo[last_index], cargo[rand_index] = cargo[rand_index], cargo[last_index]
        last_index -= 1


def escolherMissoes():
    global mapa, missao, missao_hover, jogadores_missao, falhas_missao, missao_escolhida, estado_botao_b, estado
    
    
    pos = lerJoystick()
    if pos == -1:
        missao_hover = missao_hover - 1 if missao_hover > 0 else 0
    elif pos == 1:
        missao_hover = missao_hover + 1 if missao_hover < 4 else 4
    
    mapa[1] = [BLA, BLA, BLA, BLA, BLA]
    mapa[3] = [BLA, BLA, BLA, BLA, BLA]
    mapa[4] = [BLA, BLA, BLA, BLA, BLA]
    
    mapa[1][missao_hover] = YEL
    
    for i in range (0, jogadores_missao[missao_hover]):
        mapa[3][i] = GRE
    for i in range (0, falhas_missao[missao_hover]):
        mapa[4][i] = RED
    
    atualizaOled(missao_hover)
    mostrarMatriz(mapa)
    
    # Se o Botão B for pressionado
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1
        if missao[missao_hover] == 0:
            estado = 5
            missao_escolhida = missao_hover
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0


def confirmarMissao():
    global estado_botao_a, estado_botao_b, estado, missao_escolhida
    
    atualizaOled(missao_escolhida)
    
    if button_a.value() == 0 and estado_botao_a == 0:
        estado_botao_a = 1
        estado = 4
    elif button_a.value() == 1 and estado_botao_a == 1:
        estado_botao_a = 0
    
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1
        estado = 6
    
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0


def escolherVoto():
    global vote_arrow, estado, estado_botao_a, estado_botao_b, missao_escolhida, votos_nao, num, voto_atual, missao_hover
    
    mostrarMatriz(vote_arrow)
    
    if num < jogadores_missao[missao_escolhida]:
        atualizaOled(num)
        if button_a.value() == 0 and estado_botao_a == 0:
            estado_botao_a = 1
            estado = 7
            voto_atual = False
        
        elif button_a.value() == 1 and estado_botao_a == 1:
            estado_botao_a = 0
        
        if button_b.value() == 0 and estado_botao_b == 0:
            estado_botao_b = 1
            estado = 7
            voto_atual = True
            
        elif button_b.value() == 1 and estado_botao_b == 1:
            estado_botao_b = 0
    else:
        estado = 8
        num = 0

def confirmarVoto():
    global estado, estado_botao_a, estado_botao_b, num, voto_atual, votos_nao
    
    atualizaOled(num)
    
    if button_a.value() == 0 and estado_botao_a == 0:
        estado_botao_a = 1
        estado = 6
    elif button_a.value() == 1 and estado_botao_a == 1:
        estado_botao_a = 0
    
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1
        estado = 6
        num += 1
        if voto_atual == False:
            votos_nao[missao_escolhida] += 1
            
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0


def mostrarVotos():
    global estado, estado_botao_a, estado_botao_b, votos_nao, jogadores_missao, falhas_missao, missao_escolhida, missao
    
    atualizaOled()
    
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1    
        
        animacaoMostraVotos()
        
        if votos_nao[missao_escolhida] >= falhas_missao[missao_escolhida]:
            missao[missao_escolhida] = -1
            mapa[0][missao_escolhida] = RED
            if missao.count(-1) >= 3:
                animacaoEspioes()
                estado = 9
            else:
                animacaoVotoNao()
        else:
            missao[missao_escolhida] = 1
            mapa[0][missao_escolhida] = BLU
            if missao.count(1) >= 3:
                animacaoResistencia()
                estado = 9
            else:
                animacaoVotoSim()
        if missao.count(0) == 0:
            missao[4] = 0
        if estado != 9:
            estado = 4
    
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0

def animacaoMostraVotos():
    global estado, estado_botao_a, estado_botao_b, votos_nao, jogadores_missao, falhas_missao, missao_escolhida, missao, matriz_resultado
    votos_sim = jogadores_missao[missao_escolhida] - votos_nao[missao_escolhida]
    
    mostrarMatriz(nothing)
    matriz_resultado = [[BLA, BLA, BLA, BLA, BLA],
                 [BLA, BLA, BLA, BLA, BLA],
                 [BLA, BLA, BLA, BLA, BLA],
                 [BLA, BLA, BLA, BLA, BLA],
                 [BLA, BLA, BLA, BLA, BLA]
                 ]
    i = 0
    for i in range(0, jogadores_missao[missao_escolhida]):
        if i < votos_sim:
            cor = BLU
        else:
            cor = RED
        matriz_resultado[0][i] = cor
        matriz_resultado[1][i] = cor
        matriz_resultado[2][i] = cor
        matriz_resultado[3][i] = cor
        matriz_resultado[4][i] = cor
        mostrarMatriz(matriz_resultado)
        time.sleep(2)

def animacaoVotoNao():
    global matriz_resultado
    nao = [
        [RED, BLA, BLA, BLA, RED],
        [BLA, RED, BLA, RED, BLA],
        [BLA, BLA, RED, BLA, BLA],
        [BLA, RED, BLA, RED, BLA],
        [RED, BLA, BLA, BLA, RED]
        ]
    mostrarMatriz(nao)
    #tocar uma musiquinha
    time.sleep(1)
    mostrarMatriz(matriz_resultado)
    time.sleep(1)
    mostrarMatriz(nao)
    #tocar uma musiquinha
    time.sleep(1)
    mostrarMatriz(matriz_resultado)
    time.sleep(1)
    mostrarMatriz(nao)
    time.sleep(1)

def animacaoVotoSim():
    global matriz_resultado
    sim = [
        [BLA, BLA, BLA, BLA, BLU],
        [BLA, BLA, BLA, BLU, BLA],
        [BLU, BLA, BLU, BLA, BLA],
        [BLA, BLU, BLA, BLA, BLA],
        [BLA, BLA, BLA, BLA, BLA]
        ]
    mostrarMatriz(sim)
    #tocar uma musiquinha
    time.sleep(1)
    mostrarMatriz(matriz_resultado)
    time.sleep(1)
    mostrarMatriz(sim)
    #tocar uma musiquinha
    time.sleep(1)
    mostrarMatriz(matriz_resultado)
    time.sleep(1)
    mostrarMatriz(sim)
    time.sleep(1)

def animacaoEspioes():
    mostrarMatriz([
        [RED, RED, RED, RED, RED],
        [RED, RED, RED, RED, RED],
        [RED, RED, RED, RED, RED],
        [RED, RED, RED, RED, RED],
        [RED, RED, RED, RED, RED]
        ])

def animacaoResistencia():
    mostrarMatriz([
        [BLU, BLU, BLU, BLU, BLU],
        [BLU, BLU, BLU, BLU, BLU],
        [BLU, BLU, BLU, BLU, BLU],
        [BLU, BLU, BLU, BLU, BLU],
        [BLU, BLU, BLU, BLU, BLU]
        ])

def main():
    while True:
        if estado == 0:
            escolherNumDeJogadores()
        elif estado == 1:
            confirmarNumDeJogadores()
        elif estado == 2:
            esperarParaRevelarCargo()
        elif estado == 4:
            escolherMissoes()
        elif estado == 5:
            confirmarMissao()
        elif estado == 6:
            escolherVoto()
        elif estado == 7:
            confirmarVoto()
        elif estado == 8:
            mostrarVotos()

# Executar a função principal
main()