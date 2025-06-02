from typing import BinaryIO, Optional, Tuple, Union
from readReg import readReg

def readLed(arq: BinaryIO, header: int) -> None:
    """This function just prints the LED to user."""
    try:
        if header == -1:
            print("LED -> fim")
            print("Total: 0 espaços disponíveis")
            print("A LED foi impressa com sucesso!")
            return

        total: int = 0
        output: str = "LED"

        while header != -1:
            arq.seek(header)
            data: Optional[Union[Tuple[str, int, int], Tuple[int, int, int]]] = readReg(arq, readLed=True)
            buffer, size, offset = data

            if buffer is None:
                break

            try:
                next: int = int(buffer)
            except Exception as e:
                print(e)
                break

            output += f" -> [offset: {header}, tam: {size}]"
            total += 1
            header = next

        output += " -> fim"
        print(output)
        print(f"Total: {total} espaços disponíveis")
        print("A LED foi impressa com sucesso!")
        return
    except Exception as e:
        print(f"Erro ao imprimir LED: {e}")
