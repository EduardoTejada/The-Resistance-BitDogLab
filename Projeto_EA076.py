from machine import Pin, SoftI2C, ADC, PWM
from ssd1306 import SSD1306_I2C
import utime, time, random, neopixel

# Debug, quando True retira os atrasos de animações do código para debug mais rápido
debug = False

# Intensidade do LED, pode variar de 1 a 255
it=40

# Configuração dos botões
button_a = Pin(5, Pin.IN, Pin.PULL_UP)
button_b = Pin(6, Pin.IN, Pin.PULL_UP)

# Configuração do buzzer
buzzer = PWM(Pin(21))

# Configuração OLED
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# Configuração dos pinos do joystick
vrx = ADC(Pin(27))  # Conectado ao eixo X do joystick

# Valor central esperado do joystick no eixo X
CENTRAL_X = 32768

np = neopixel.NeoPixel(machine.Pin(7), 25)

# definir cores para os LEDs
BLU = (0, 0, 1*it)# BLUE
GRE = (0, 1*it, 0)# GREEN
RED = (1*it, 0, 0)#RED
YEL = (1*it, 1*it, 0)# YELLOW
MAGE = (1*it, 0, 1*it)# MANGENTA
CYA = (0, 1*it, 1*it)# CYAN
WHI = (1*it//3, 1*it//3, 1*it//3)# WHIE
BLA = (0, 0, 0)# BLACK

# Simbolos padrões no display matricial
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
estado_botao_a = 0
estado_botao_b = 0
missao_hover = 0
cargo = ["Assassino", "Comandante Falso", "Guarda Costas", "Comandante", "Resistencia", "Resistencia", "Agente Oculto", "Resistencia", "Resistencia", "Espiao", ""]
jogadores_missao = [3, 4, 4, 5, 5]
falhas_missao = [1, 1, 1, 2, 1]
missao = [0, 0, 0, 0, None]
missao_escolhida = None
votos_nao = [0, 0, 0, 0, 0]
jogador_atual = 0
voto_atual = None
time_vencedor = None


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

    # inverter a matriz para que seja mostrada exatamente como é escrita
    inverted_matrix = led_matrix[::-1]
    inverted_matrix[0] = inverted_matrix[0][::-1]
    inverted_matrix[2] = inverted_matrix[2][::-1]
    inverted_matrix[4] = inverted_matrix[4][::-1]

    # exibir a matriz invertida nos LEDs
    for i in range(5):
        for j in range(5):
            np[i*5+j] = inverted_matrix[i][j]

    np.write()

#mostrando inicialmente um coração no display matricial
mostrarMatriz(heart)


#função para mostrar no oled
def atualizaOled(numero_i = 0, tempo = 0):
    global numero_de_jogadores, estado, cargo, mapa, time_vencedor
    
    oled.fill(0)  # Limpar display
    
    #conforme o estado será mostrado ao diferente no display
    if estado == 0: #fase inicial: quantidade de jogadores
        oled.text("Num de jogadores: ", 0, 0)
        oled.text(str(numero_de_jogadores), 0, 10)
        oled.text("Pressione B", 0, 30)
    elif estado == 1: #confirmação da quantidade de jogadores
        oled.text("B para confirmar", 0, 0)
        oled.text("A para voltar", 0, 10)
        oled.text("Jogadores: "+ str(numero_de_jogadores), 0, 30)
    elif estado == 2: # pré revelação de cargo (espera de 2 segundos e confirmação)
        oled.text("Jogador "+str(numero_i+1), 0, 0)
        if tempo > 0:
            oled.text("Aguarde: "+str(tempo), 0, 30)
        else:
            oled.text("B para revelar", 0, 30)
    elif estado == 3: # revelação de cargo
        oled.text("Jogador "+str(numero_i+1), 0, 0)
        oled.text("Cargo:", 0, 10)
        oled.text(str(cargo[numero_i]), 0, 20)
        #oled.text("Time:", 0, 40)
        if str(cargo[numero_i]) == "Agente Oculto" or str(cargo[numero_i]) == "Comandante Falso" or str(cargo[numero_i]) == "Assassino" or str(cargo[numero_i]) == "Espiao":
            oled.text("Time: Espioes", 0, 30)
        else:
            oled.text("Time:Resistencia", 0, 30)
        oled.text("B para esconder", 0, 50)
    elif estado == 4: # mostrando informações de cada missão
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
            
    elif estado == 5: # confirmação de escolha da missão
        oled.text("B para confirmar", 0, 0)
        oled.text("A para voltar", 0, 10)
        oled.text("Missao: "+ str(numero_i+1), 0, 30)
        oled.text("Jogadores "+str(jogadores_missao[numero_i]), 0, 40)
        oled.text("Falhas "+str(falhas_missao[numero_i]), 0, 50)
    elif estado == 6: # votando na missão
        oled.text("Jogador "+str(numero_i+1), 0, 0)
        oled.text("", 0, 10)
        oled.text("A para rejeitar", 0, 20)
        oled.text("B para aprovar", 0, 30)
    elif estado == 7: # confirmação de voto da missão
        oled.text("Jogador "+str(numero_i+1), 0, 0)
        oled.text("Confirma o voto?", 0, 10)
        oled.text("B para confirmar", 0, 20)
        oled.text("A para voltar", 0, 30)
    elif estado == 8: # revelação de resultado da missão
        oled.text("Aperte B para", 0, 0)
        oled.text("revelar o", 0, 10)
        oled.text("resultado", 0, 20)
    elif estado == 9: # fim de jogo
        oled.text("Time vencedor:", 0, 0)
        oled.text(str(time_vencedor), 0, 10)
    oled.show()

#função para atualizar o numero de jogadores de acordo com a variavel "pos" de entrada que se refere a posição do joystick
def atualizaJogadores(pos):
    global numero_de_jogadores
    
    if pos == -1:
        numero_de_jogadores = numero_de_jogadores - 1 if numero_de_jogadores > 5 else 5 # numero minimo 5 jogadores
    elif pos == 1:
        numero_de_jogadores = numero_de_jogadores + 1 if numero_de_jogadores < 10 else 10 # numero máximo 10 jogadores


def confirmarNumDeJogadores():
    global estado_botao_a, estado_botao_b, estado, numero_de_jogadores, jogadores_missao
    
    atualizaOled()
    
    #leitura do botão A -> volta pro estado de escolha da quantidade de jogadores
    if button_a.value() == 0 and estado_botao_a == 0:
        estado_botao_a = 1
        estado = 0
    elif button_a.value() == 1 and estado_botao_a == 1:
        estado_botao_a = 0
    
    #leitura do botão B -> vai pro estado de revelação dos cargos
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1
        estado = 2
        if numero_de_jogadores == 7:            # configuração da quantidade de jogadores por missão de acordo com o número de jogadores total
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
    
    posicaoJoystick = lerJoystick()   # retorna -1 se joystick pra esquerda, 1 se joystick pra direita, 0 se joystick no meio
    atualizaJogadores(posicaoJoystick) # atualiza o número de jogadores
    atualizaOled()
    
    # Leitura do botão B -> vai pro estado de confirmação do número de jogadores
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1
        estado = 1
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0


def esperarParaRevelarCargo():
    global estado, estado_botao_b, numero_de_jogadores, debug
    
    i = 0
    
    sortearCargos()
    
    flag_sleep = True # indica se vai entrar no modo de espera
    
    while i < numero_de_jogadores: # iteração para cada jogador
        # verifica se esta no estado de esperar para revelar o cargo (2) ou se esta revelando o cargo (3)
        if estado == 2: # estado de espera e confirmação para revelar o cargo
            if flag_sleep and not debug: # verifica o modo de espera
                for k in range(0, 2): # loop para esperar 2 segundos e exibir no display o tempo
                    atualizaOled(i, 2-k)
                    time.sleep(1)
                atualizaOled(i, 0)
                flag_sleep = False # indica que a espera finalizou
            else:
                atualizaOled(i) #atualiza oled após espera finalizada mostrando a tela pré revelação de cargo
            
            # Leitura do botão B
            if button_b.value() == 0 and estado_botao_b == 0:
                estado_botao_b = 1
                estado = 3 # vai para o estado de revelação do cargo
            elif button_b.value() == 1 and estado_botao_b == 1:
                estado_botao_b = 0

        elif estado == 3: # estado de revelação do cargo
            atualizaOled(i) # mostra cargo
            # Leitura do botão B
            if button_b.value() == 0 and estado_botao_b == 0:
                estado_botao_b = 1
                estado = 2 # volta para o estado de espera e confirmação para revelar o cargo
                i += 1 # itera a variavel até chegar no ultimo jogador
                flag_sleep = True # indica para entrar no modo de espera novamente
            elif button_b.value() == 1 and estado_botao_b == 1:
                estado_botao_b = 0
    
    estado = 4 # após finalizar todos os jogadores vai para o estado de escolha das missões
    atualizaOled()

def sortearCargos():
    global numero_de_jogadores
    global cargo
    
    """ de acordo com o número de jogadores certos cargos não participam do jogo, usando slicing podemos cortar a lista de cargos
        a partir de uma determinada posição em diante, ela foi montada de tal forma que só fiquem os cargos que deveriam
        estar após o slicing. Ex.: com 6 jogadores são retirados: 1 Agente Oculto, 2 da Resistencia e 1 Espiao genérico,
        ainda, no final de "cargo" inicialmente tem uma string vazia "", que serve para podermos fazer o slicing mesmo com 10 jogadores """
    cargo = cargo[:numero_de_jogadores] 
    
    # repete o processo de sortear 2 vezes
    for k in range(0, 2):
        last_index = numero_de_jogadores - 1
        # faz N-1 swaps aleatórios na lista de cargos
        while last_index > 0:
            rand_index = random.randint(0, last_index)
            cargo[last_index], cargo[rand_index] = cargo[rand_index], cargo[last_index]
            last_index -= 1


def escolherMissoes():
    global mapa, missao, missao_hover, jogadores_missao, falhas_missao, missao_escolhida, estado_botao_b, estado
    
    # le a posiçao do joystick e muda a "seta" que é usada para escolher qual missão será selecionada
    pos = lerJoystick()
    if pos == -1:
        missao_hover = missao_hover - 1 if missao_hover > 0 else 0 # não pode ser menor que 0
    elif pos == 1:
        missao_hover = missao_hover + 1 if missao_hover < 4 else 4 # não pode ser maior que 4 (há 5 missões)
    
    #atualiza o mapa para mudar a posição da "seta" (missão_hover)
    mapa[1] = [BLA, BLA, BLA, BLA, BLA]
    mapa[3] = [BLA, BLA, BLA, BLA, BLA]
    mapa[4] = [BLA, BLA, BLA, BLA, BLA]
    
    mapa[1][missao_hover] = YEL
    
    # indica quantos jogadores vão na missão
    for i in range (0, jogadores_missao[missao_hover]):
        mapa[3][i] = GRE
    # indica quantos falhas a missão precisa para falhar
    for i in range (0, falhas_missao[missao_hover]):
        mapa[4][i] = RED
    
    atualizaOled(missao_hover)
    mostrarMatriz(mapa)
    
    # Se o Botão B for pressionado
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1
        if missao[missao_hover] == 0:
            estado = 5 # vai para o estado de confirmação da missão escolhida
            missao_escolhida = missao_hover
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0


def confirmarMissao():
    global estado_botao_a, estado_botao_b, estado, missao_escolhida
    
    atualizaOled(missao_escolhida)
    
    # Leitura do botão A
    if button_a.value() == 0 and estado_botao_a == 0:
        estado_botao_a = 1
        estado = 4 # volta para o estado de escolher missão
    elif button_a.value() == 1 and estado_botao_a == 1:
        estado_botao_a = 0
    
    # Leitura do botão B
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1
        estado = 6 # vai para o estado de votação
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0


def escolherVoto():
    global vote_arrow, estado, estado_botao_a, estado_botao_b, missao_escolhida, votos_nao, jogador_atual, voto_atual, missao_hover
    
    mostrarMatriz(vote_arrow)
    
    # "itera" entre a quantidade de jogadores da missão
    if jogador_atual < jogadores_missao[missao_escolhida]:
        atualizaOled(jogador_atual)
        
        # Leitura do botão A
        if button_a.value() == 0 and estado_botao_a == 0:
            estado_botao_a = 1
            estado = 7 #  vai para o estado de confirmação do voto
            voto_atual = False # configura voto como "Não"
        elif button_a.value() == 1 and estado_botao_a == 1:
            estado_botao_a = 0
        
        # Leitura do botão B
        if button_b.value() == 0 and estado_botao_b == 0:
            estado_botao_b = 1
            estado = 7 #  vai para o estado de confirmação do voto
            voto_atual = True  # configura voto como "Sim"
        elif button_b.value() == 1 and estado_botao_b == 1:
            estado_botao_b = 0
    else:
        estado = 8 # quando acaba os jogadores muda para o estado de revelação da missão
        jogador_atual = 0 # zera a variável de "iteração"

def confirmarVoto():
    global estado, estado_botao_a, estado_botao_b, jogador_atual, voto_atual, votos_nao
    
    atualizaOled(jogador_atual)
    
    # Leitura do botão A
    if button_a.value() == 0 and estado_botao_a == 0:
        estado_botao_a = 1
        estado = 6 # volta para o estado de escolher voto
    elif button_a.value() == 1 and estado_botao_a == 1:
        estado_botao_a = 0
    
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1
        estado = 6 # volta para o estado de escolher voto
        jogador_atual += 1 # incrementa o numero de jogadores que ja votaram
        if voto_atual == False:
            votos_nao[missao_escolhida] += 1 #  conta votos negados para a missão atual
            
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0


def mostrarVotos():
    global estado, estado_botao_a, estado_botao_b, votos_nao, jogadores_missao, falhas_missao, missao_escolhida, missao, time_vencedor
    
    atualizaOled()
    
    # Leitura do botão B
    if button_b.value() == 0 and estado_botao_b == 0:
        estado_botao_b = 1    
        
        animacaoMostraVotos()
        
        # Verifica se a missão deu falha ou sucesso
        if votos_nao[missao_escolhida] >= falhas_missao[missao_escolhida]:
            missao[missao_escolhida] = -1
            mapa[0][missao_escolhida] = RED
            if missao.count(-1) >= 3:
                animacaoEspioes()
                estado = 9
                time_vencedor = "ESPIOES"
            else:
                animacaoVotoNao()
        else:
            missao[missao_escolhida] = 1
            mapa[0][missao_escolhida] = BLU
            if missao.count(1) >= 3:
                animacaoResistencia()
                estado = 9
                time_vencedor = "RESISTENCIA"
            else:
                animacaoVotoSim()
        atualizaOled()
        if estado != 9: # verifica se o jogo não acabou
            estado = 4 #  volta para o estado de escolher missões
            if missao.count(0) == 0: # verifica se não as 4 primeiras missões ja foram jogadas
                missao[4] = 0 # libera a última missão
    
    elif button_b.value() == 1 and estado_botao_b == 1:
        estado_botao_b = 0

def animacaoMostraVotos():
    global estado, estado_botao_a, estado_botao_b, votos_nao, jogadores_missao, falhas_missao, missao_escolhida, missao, matriz_resultado, debug
    votos_sim = jogadores_missao[missao_escolhida] - votos_nao[missao_escolhida]
    
    mostrarMatriz(nothing)
    matriz_resultado = [[BLA, BLA, BLA, BLA, BLA],
                 [BLA, BLA, BLA, BLA, BLA],
                 [BLA, BLA, BLA, BLA, BLA],
                 [BLA, BLA, BLA, BLA, BLA],
                 [BLA, BLA, BLA, BLA, BLA]
                 ]
    i = 0
    
    # mostra os votos de maneira a não revelar a ordem em que eles ocorreram, mostrando primeiro os azuis
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
        if not debug:
            time.sleep(2)

def animacaoVotoNao():
    global matriz_resultado, debug
    nao = [
        [RED, BLA, BLA, BLA, RED],
        [BLA, RED, BLA, RED, BLA],
        [BLA, BLA, RED, BLA, BLA],
        [BLA, RED, BLA, RED, BLA],
        [RED, BLA, BLA, BLA, RED]
        ]
    mostrarMatriz(nao)
    som_derrota_classico()
    if not debug:
        time.sleep(1)
        mostrarMatriz(matriz_resultado)
        time.sleep(1)
        mostrarMatriz(nao)
        time.sleep(1)
        mostrarMatriz(matriz_resultado)
        time.sleep(1)
        mostrarMatriz(nao)
        time.sleep(1)

def animacaoVotoSim():
    global matriz_resultado, debug
    sim = [
        [BLA, BLA, BLA, BLA, BLU],
        [BLA, BLA, BLA, BLU, BLA],
        [BLU, BLA, BLU, BLA, BLA],
        [BLA, BLU, BLA, BLA, BLA],
        [BLA, BLA, BLA, BLA, BLA]
        ]
    mostrarMatriz(sim)
    som_vitoria()
    if not debug:
        time.sleep(1)
        mostrarMatriz(matriz_resultado)
        time.sleep(1)
        mostrarMatriz(sim)
        time.sleep(1)
        mostrarMatriz(matriz_resultado)
        time.sleep(1)
        mostrarMatriz(sim)
        time.sleep(1)

def animacaoEspioes():
    mostrarMatriz([
        [BLA, BLA, BLA, BLA, BLA],
        [BLA, RED, BLA, RED, BLA],
        [BLA, BLA, BLA, BLA, BLA],
        [RED, BLA, BLA, BLA, RED],
        [BLA, RED, RED, RED, BLA]
        ])
    som_derrota_classico()
    time.sleep(3)
    reiniciarJogo()

def animacaoResistencia():
    mostrarMatriz([
        [BLA, BLU, BLA, BLU, BLA],
        [BLA, BLU, BLA, BLU, BLA],
        [BLA, BLA, BLA, BLA, BLA],
        [BLU, BLA, BLA, BLA, BLU],
        [BLA, BLU, BLU, BLU, BLA]
        ])
    som_vitoria()
    time.sleep(3)
    reiniciarJogo()


def som_derrota_classico():
    # Sequência de notas descendentes
    notas = [523, 466, 392, 349]  # C5, A#4, G4, F4
    duracoes = [0.2, 0.2, 0.2, 0.6]  # Duracoes respectivas das notas
    
    for i in range(4):
        buzzer.freq(notas[i])  # Define a frequência da nota
        buzzer.duty_u16(32768)  # 50% duty cycle
        time.sleep(duracoes[i])  # Duração da nota
        buzzer.duty_u16(0)  # Pausa entre as notas
        time.sleep(0.05)
        
        
def som_vitoria():
    # Sequência de notas com um padrão alegre
    buzzer.freq(523)  # Nota C5 (523 Hz)
    buzzer.duty_u16(32768)  # 50% duty cycle
    time.sleep(0.15)  # Duração da nota
    buzzer.duty_u16(0)  # Pausa entre as notas
    time.sleep(0.05)

    buzzer.freq(659)  # Nota E5 (659 Hz)
    buzzer.duty_u16(32768)
    time.sleep(0.15)
    buzzer.duty_u16(0)
    time.sleep(0.05)

    buzzer.freq(784)  # Nota G5 (784 Hz)
    buzzer.duty_u16(32768)
    time.sleep(0.15)
    buzzer.duty_u16(0)
    time.sleep(0.05)

    buzzer.freq(1046)  # Nota C6 (1046 Hz) - uma oitava acima
    buzzer.duty_u16(32768)
    time.sleep(0.3)
    buzzer.duty_u16(0)


def reiniciarJogo():
    global estado, missao_hover, cargo, jogadores_missao, falhas_missao, missao, missao_escolhida, votos_nao, jogador_atual, voto_atual, time_vencedor, heart, mapa
    
    play_amongus()
    # reinicia todas as variaveis necessárias
    mostrarMatriz(heart)
    estado = 0
    missao_hover = 0
    cargo = ["Assassino", "Comandante Falso", "Guarda Costas", "Comandante", "Resistencia", "Resistencia", "Agente Oculto", "Resistencia", "Resistencia", "Espiao", ""]
    jogadores_missao = [3, 4, 4, 5, 5]
    falhas_missao = [1, 1, 1, 2, 1]
    missao = [0, 0, 0, 0, None]
    missao_escolhida = None
    votos_nao = [0, 0, 0, 0, 0]
    jogador_atual = 0
    voto_atual = None
    time_vencedor = None
    mapa = [
        [WHI, WHI, WHI, WHI, WHI],
        [YEL, BLA, BLA, BLA, BLA],
        [BLA, BLA, BLA, BLA, BLA],
        [BLA, BLA, BLA, BLA, BLA],
        [BLA, BLA, BLA, BLA, BLA]
    ]


def play_tone(frequency, duration):
    if frequency == 0:
        time.sleep(duration)
    else:
        buzzer.freq(frequency)
        buzzer.duty_u16(32768)  # 50% duty cycle
        time.sleep(duration)
        buzzer.duty_u16(0)  # Desliga o som
        time.sleep(0.05)  # Pausa curta entre as notas

def play_amongus():
    # Primeira parte da música
    play_tone(1046, 0.25)  # C6
    play_tone(1244, 0.25)  # D#6
    play_tone(1400, 0.25)  # F6 (aproximado)
    play_tone(1510, 0.25)  # F#6 (aproximado)
    play_tone(1400, 0.25)  # F6 (aproximado)
    play_tone(1244, 0.25)  # D#6
    play_tone(1046, 0.25)  # C6
    play_tone(0, 0.5)      # Pausa
    play_tone(932, 0.125)  # A#5
    play_tone(1174, 0.125) # D#6
    play_tone(1046, 0.25)  # C6
    play_tone(0, 0.5)      # Pausa
    play_tone(780, 0.25)   # G5
    play_tone(525, 0.25)   # C5 (aproximado)
    play_tone(0, 0.25)     # Pausa


def main():
    #loop infinito verificando a maquina de estados
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
        elif estado == 9:
            reiniciarJogo()

# Executar a função principal
main()
