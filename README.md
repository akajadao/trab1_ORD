# README - Organização e Recuperação de Dados

Este programa gerencia um arquivo binário com registros, permitindo imprimir a Lista de Espaços Disponíveis (LED), realizar operações de busca, inserção e remoção de registros, e desfragmentar o arquivo para otimizar seu espaço.

---

## Como usar

O programa é executado via linha de comando usando Python 3.

python main.py <flag> <arquivo_binario> [arquivo_operacoes] <br/>
Flags disponíveis<br/>
-p — Imprimir a LED (Lista de Espaços Disponíveis)<br/>
Exibe os espaços livres no arquivo binário, indicando offsets e tamanhos disponíveis.<br/>
Uso:<br/>
python main.py -p arquivo_binario<br/>
Imprime a LED.<br/>

-e — Executar operações no arquivo<br/>
Realiza operações de busca, inserção e remoção de registros, conforme especificado num arquivo de operações texto.<br/>
Uso:<br/>
python main.py -e arquivo_binario arquivo_operacoes<br/>
Formato do arquivo de operações:<br/>
Cada linha representa uma operação.<br/>
Operações possíveis:<br/>
Operação	Formato da linha	Descrição<br/>
Busca	b <id>	Busca registro pelo ID<br/>
Inserção	i <registro>	Insere um novo registro<br/>
Remoção	r <id>	Remove registro pelo ID<br/>

Exemplo do arquivo de operações:<br/>
b 123<br/>
i 456|Nome|OutroCampo<br/>
r 789<br/>

-c — Compactar (desfragmentar) o arquivo binário<br/>
Remove os espaços livres causados por registros removidos, reorganizando o arquivo para otimizar espaço.<br/>
Uso:<br/>
python main.py -c arquivo_binario<br/>

Requisitos<br/>
Python 3.09+<br/>

Os módulos .py correspondentes (readLed.py, findRegister.py, removeRegister.py, insertRegister.py, defragFile.py, readReg.py) devem estar no mesmo diretório.<br/>

Se precisar de ajuda ou encontrar bugs, abra uma issue ou contate os autores.<br/>

Autores:<br/>
Jader Alves dos Santos (RA: 120286)<br/>
Janaina Maria Cera da Silva (RA: 115832)<br/>
Lucas Rodrigues Fedrigo (RA: 129060)<br/>
