# README - Organização e Recuperação de Dados

Este programa gerencia um arquivo binário com registros, permitindo imprimir a Lista de Espaços Disponíveis (LED), realizar operações de busca, inserção e remoção de registros, e desfragmentar o arquivo para otimizar seu espaço.

---

## Como usar

O programa é executado via linha de comando usando Python 3.

python main.py <flag> <arquivo_binario> [arquivo_operacoes]
Flags disponíveis
-p — Imprimir a LED (Lista de Espaços Disponíveis)
Exibe os espaços livres no arquivo binário, indicando offsets e tamanhos disponíveis.
Uso:
python main.py -p arquivo_binario
Imprime a LED.

-e — Executar operações no arquivo
Realiza operações de busca, inserção e remoção de registros, conforme especificado num arquivo de operações texto.
Uso:
python main.py -e arquivo_binario arquivo_operacoes
Formato do arquivo de operações:
Cada linha representa uma operação.
Operações possíveis:
Operação	Formato da linha	Descrição
Busca	b <id>	Busca registro pelo ID
Inserção	i <registro>	Insere um novo registro
Remoção	r <id>	Remove registro pelo ID

Exemplo do arquivo de operações:
b 123
i 456|Nome|OutroCampo
r 789

-c — Compactar (desfragmentar) o arquivo binário
Remove os espaços livres causados por registros removidos, reorganizando o arquivo para otimizar espaço.
Uso:
python main.py -c arquivo_binario

Requisitos
Python 3.09+

Os módulos .py correspondentes (readLed.py, findRegister.py, removeRegister.py, insertRegister.py, defragFile.py, readReg.py) devem estar no mesmo diretório.

Se precisar de ajuda ou encontrar bugs, abra uma issue ou contate os autores.

Autores:
Jader Alves dos Santos (RA: 120286)
Janaina Maria Cera da Silva (RA: 115832)
Lucas Rodrigues Fedrigo (RA: 129060)
