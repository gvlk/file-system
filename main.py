# Guilherme Azambuja - 149429
# Pablo Guaicurus - 149449
# Rafaela Barcelos - 149438
# https://github.com/gvlk/file-system
# Leia o README.md

from file_system import FileSystem
from pickle import load
from time import sleep


def show_menu1():
    print("\nMenu:")
    print("1. Criar um novo sistema de arquivos")
    print("2. Utilizar arquivo .fs existente")


def show_menu2():
    print("\nMenu:")
    print("1. Copiar arquivo para o sistema")
    print("2. Copiar arquivo do sistema")
    print("3. Renomear arquivo")
    print("4. Remover arquivo")
    print("5. Listar arquivos")
    print("6. Mostrar informações de espaço ocupado")
    print("7. Sair")


def main():
    fs: FileSystem | None

    while True:
        sleep(1)
        show_menu1()
        choice = input("Escolha uma opção: ")

        if choice == "1":
            size = float(input("Informe o tamanho do sistema em bytes: "))
            fs = FileSystem(size)
            print(f"\nSistema de arquivos criado com sucesso! {fs}")
            exit()

        elif choice == "2":
            nome = str(input("Informe o nome do arquivo: "))
            with open(nome, "rb") as file:
                fs = load(file)
            print(f"\nSistema de arquivos acessado! {fs}")
            break

        else:
            print("\nEscolha uma opção válida.")

    while True:
        sleep(1)
        show_menu2()
        choice = input("Escolha uma opção: ")

        if choice == "1":
            file_path = input("Informe o caminho do arquivo a ser copiado: ")
            try:
                fs.copy_to_fs(file_path)
                print("\nArquivo copiado para o sistema com sucesso!")
            except Exception as e:
                print(f"\nErro ao copiar arquivo para o sistema: {str(e)}")

        elif choice == "2":
            file_name = input("Informe o nome do arquivo a ser copiado do sistema: ")
            try:
                fs.copy_from_fs(file_name)
                print("Arquivo copiado do sistema com sucesso!")
            except Exception as e:
                print(f"Erro ao copiar arquivo do sistema: {str(e)}")

        elif choice == "3":
            old_name = input("Informe o nome antigo do arquivo: ")
            new_name = input("Informe o novo nome do arquivo: ")
            try:
                fs.rename(old_name, new_name)
                print("Arquivo renomeado com sucesso!")
            except Exception as e:
                print(f"Erro ao renomear arquivo: {str(e)}")

        elif choice == "4":
            file_name = input("Informe o nome do arquivo a ser removido: ")
            try:
                fs.remove(file_name)
                print("Arquivo removido com sucesso!")
            except Exception as e:
                print(f"Erro ao remover arquivo: {str(e)}")

        elif choice == "5":
            fs.list_files()

        elif choice == "6":
            fs.usage_info()

        elif choice == "7":
            print("Encerrando o programa...")
            break

        else:
            print("Escolha uma opção válida.")


if __name__ == "__main__":
    main()
