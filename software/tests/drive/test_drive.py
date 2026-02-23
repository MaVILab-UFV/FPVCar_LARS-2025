import cv2
import numpy as np
import os

def detectar_bordas_pista(imagem_caminho):
    # Carregar a imagem
    imagem = cv2.imread(imagem_caminho)
    if imagem is None:
        print("Erro ao carregar a imagem.")
        return

    # Redimensionar a imagem para facilitar o processamento (opcional)
    largura_desejada = 640
    altura_desejada = 480
    imagem = cv2.resize(imagem, (largura_desejada, altura_desejada))

    # Converter a imagem para escala de cinza
    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Aplicar desfoque gaussiano para reduzir ruídos
    imagem_borrada = cv2.GaussianBlur(imagem_cinza, (5, 5), 0)

    # Detectar bordas com o algoritmo de Canny
    bordas = cv2.Canny(imagem_borrada, 50, 150)

    # Criar uma máscara para isolar a região da pista (opcional)
    mascara = np.zeros_like(bordas)
    altura, largura = bordas.shape

    # Definir a região de interesse (ROI) para focar na pista
    regioes_interesse = np.array([
        [
            (int(0.1 * largura), altura),
            (int(0.9 * largura), altura),
            (int(0.6 * largura), int(0.5 * altura)),
            (int(0.4 * largura), int(0.5 * altura))
        ]
    ])

    # Preencher a ROI com branco na máscara
    cv2.fillPoly(mascara, regioes_interesse, 255)

    # Aplicar a máscara nas bordas
    bordas_segmentadas = cv2.bitwise_and(bordas, mascara)

    # Mostrar os resultados
    cv2.imshow('Imagem Original', imagem)
    cv2.imshow('Bordas Detectadas', bordas)
    cv2.imshow('Bordas Segmentadas', bordas_segmentadas)

def listar_arquivos(pasta):
    try:
        # Obter a lista de todos os arquivos e pastas no diretório especificado
        itens = os.listdir(pasta)

        # Filtrar apenas os arquivos
        arquivos = [item for item in itens if os.path.isfile(os.path.join(pasta, item))]

        # Imprimir os arquivos encontrados
        print(f"Arquivos na pasta '{pasta}':")
        for arquivo in arquivos:
            print(arquivo)

        return arquivos
    except FileNotFoundError:
        print(f"A pasta '{pasta}' não foi encontrada.")
    except PermissionError:
        print(f"Permissão negada para acessar a pasta '{pasta}'.")
        
def detectar_linhas(imagem_caminho):
    # Carregar a imagem
    imagem = cv2.imread(imagem_caminho)
    if imagem is None:
        print("Erro ao carregar a imagem.")
        return
    
    # Redimensionar a imagem (opcional)
    # largura_desejada = 640
    # altura_desejada = 480
    # imagem = cv2.resize(imagem, (largura_desejada, altura_desejada))
    
    imagem = imagem[240:, :]
    
    # Converter para escala de cinza
    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    
    # Aplicar detecção de bordas (Canny)
    bordas = cv2.Canny(imagem_cinza, 50, 150, apertureSize=3)
    
    bordas = cv2.dilate(bordas, np.ones((3,3), np.uint8), iterations=1)
    
    # Detectar linhas usando Transformada de Hough
    linhas = cv2.HoughLines(bordas, 1, np.pi / 180, 150)
    
    if linhas is not None:
        for linha in linhas:
            rho, theta = linha[0]
            a = np.cos(theta)
            b = np.sin(theta)
            if abs(a) <= 0.05:
                continue
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            cv2.line(imagem, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    # Exibir a imagem com linhas detectadas
    cv2.imshow('Linhas Detectadas', imagem)
    cv2.imshow('Bordas', bordas)

def detectar_linhas_probabilistico(imagem_caminho):
    # Carregar a imagem
    imagem = cv2.imread(imagem_caminho)
    if imagem is None:
        print("Erro ao carregar a imagem.")
        return
    
    # # Redimensionar a imagem (opcional)
    # largura_desejada = 640
    # altura_desejada = 480
    # imagem = cv2.resize(imagem, (largura_desejada, altura_desejada))
    
    imagem = imagem[240:, :]
    
    # Converter para escala de cinza
    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    
    # Aplicar detecção de bordas (Canny)
    bordas = cv2.Canny(imagem_cinza, 50, 150, apertureSize=3)
    
    bordas = cv2.dilate(bordas, np.ones((3,3), np.uint8), iterations=1)
    
    # Detectar linhas usando Hough Probabilístico
    linhas = cv2.HoughLinesP(bordas, 1, np.pi / 180, 100, minLineLength=50, maxLineGap=10)
    
    mask_linhas = np.zeros(shape=imagem.shape)
    
    if linhas is not None:
        for linha in linhas:
            x1, y1, x2, y2 = linha[0]
            if abs(y1 - y2) <= 3:
                continue
            cv2.line(imagem, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.line(mask_linhas, (x1, y1), (x2, y2), (255, 255, 255), 2)
    
    # Exibir a imagem com segmentos de linha detectados
    cv2.imshow('Linhas Detectadas (Probabilístico)', imagem)
    cv2.imshow('Bordas', bordas)
    cv2.imshow('mask_linhas', mask_linhas)

def remover_linhas_horizontais(imagem_caminho, salvar_resultado=False):
    # Carregar a imagem
    imagem = cv2.imread(imagem_caminho, cv2.IMREAD_GRAYSCALE)
    if imagem is None:
        print("Erro ao carregar a imagem.")
        return
    
    # Binarizar a imagem usando o limiar adaptativo
    _, imagem_bin = cv2.threshold(imagem, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Criar um kernel horizontal para detectar linhas horizontais
    kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (imagem.shape[1] // 30, 1))
    
    # Detectar as linhas horizontais usando morfologia
    linhas_horizontais = cv2.morphologyEx(imagem_bin, cv2.MORPH_OPEN, kernel_horizontal, iterations=2)
    
    # Subtrair as linhas horizontais da imagem binária original
    imagem_sem_linhas = cv2.bitwise_and(imagem_bin, cv2.bitwise_not(linhas_horizontais))
    
    # Inverter a imagem para restaurar a intensidade original
    imagem_resultado = cv2.bitwise_not(imagem_sem_linhas)
    
    # Salvar ou exibir a imagem resultante
    if salvar_resultado:
        cv2.imwrite("resultado_sem_linhas.png", imagem_resultado)
    
    # Exibir resultados
    cv2.imshow("Imagem Original", imagem)
    cv2.imshow("Linhas Horizontais Detectadas", linhas_horizontais)
    cv2.imshow("Imagem sem Linhas", imagem_resultado)

def remove_linhas(path):
    # Read image
    image = cv2.imread(path)
    mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
    
    print(image.shape)

    # Convert image to grayscale
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    
    # Use canny edge detection
    edges = cv2.Canny(gray,30,100,apertureSize=3)

    # Dilating
    img_dilation = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)

    
    # Apply HoughLinesP method to
    # to directly obtain line end points
    lines = cv2.HoughLinesP(
                img_dilation, # Input edge image
                1, # Distance resolution in pixels
                np.pi/180, # Angle resolution in radians
                threshold=100, # Min number of votes for valid line
                minLineLength=320, # Min allowed length of line
                maxLineGap=10 # Max allowed gap between line for joining them
                )

    lines_list = []

    if lines is not None:
        for points in lines:
            x1,y1,x2,y2=points[0]
            lines_list.append([(x1,y1),(x2,y2)])
            slope = ((y2-y1) / (x2-x1)) if (x2-x1) != 0 else np.inf
            
            if -0.1 <= slope <= 0.1:
                cv2.line(mask,(x1,y1),(x2,y2), color=(255, 255, 255),thickness = 2)
        
    result = cv2.inpaint(image,mask,3,cv2.INPAINT_TELEA)
    img_dilation = cv2.bitwise_and(img_dilation, cv2.bitwise_not(mask))
    cv2.imshow('image', image)
    cv2.imshow('result', result)
    cv2.imshow('mask', mask)
    cv2.imshow('gray', gray)
    cv2.imshow('edges', edges)
    cv2.imshow('img_dilation', img_dilation)

# Caminho para a imagem
caminho_imagem = "pista.jpg"  # Substitua pelo caminho da sua imagem
detectar_linhas_probabilistico(caminho_imagem)

# Caminho para a imagem
caminho_imagem = "pista.jpg"  # Substitua pelo caminho da sua imagem
detectar_linhas(caminho_imagem)

# Caminho da pasta que deseja listar
caminho_pasta = "tests/imgs"  # Substitua pelo caminho da sua pasta
lista = listar_arquivos(caminho_pasta)

print(len(lista))

i = 0
while True:
    path = f'tests/imgs/{lista[i]}'
    print(i)
    # detectar_linhas(path)
    detectar_linhas_probabilistico(path)
    # detectar_bordas_pista(path)
    # remover_linhas_horizontais(path)
    # remove_linhas(path)
    
    key = cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    if key == ord('q'):
        break

    if key == ord('d'):
        i = min(i+1, len(lista) - 1)
    
    if key == ord('a'):
        i = max(0, i-1)
        
cv2.destroyAllWindows()