import sys
from pathlib import Path

PARSER_REPO_PATH = r"D:/n2t_Course/a_whole_compiler/mine_parser"
# Добавляем родительскую папку (чтобы работал импорт "from jack_parser...")
sys.path.append(PARSER_REPO_PATH) 
# Добавляем саму папку с файлами (чтобы файлы внутри jack_parser видели друг друга напрямую)
sys.path.append(f"{PARSER_REPO_PATH}/jack_parser") 


# Импортируем компоненты напрямую без перехвата ошибок
from jack_parser.tokenizer import Tokenizer
from jack_parser.parser import Parser
from code_writer import CodeWriter


def compile_file(jack_file_path: Path):
    if jack_file_path.suffix != '.jack':
        return

    print(f"Компиляция: {jack_file_path.name}")
    
    # 1. Токенизация и Инициализация парсера
    tokenizer = Tokenizer(jack_file_path.read_text(encoding='utf-8'))
    parser = Parser(tokenizer)
    
    # 2. Парсинг в AST (Ищем метод парсера для обработки всего класса)
    class_ast = parser.read_class() 

    # 3. Генерация VM кода через CodeWriter
    writer = CodeWriter()
    writer.write_class(class_ast)
    
    # Собираем строки кода воедино
    vm_code = "\n".join(writer.result_vm_code)
    
    # 4. Запись результата в .vm файл
    output_path = jack_file_path.with_suffix('.vm')
    output_path.write_text(vm_code, encoding='utf-8')
    print(f"Создан файл: {output_path.name}\n")

def main():
    if len(sys.argv) < 2:
        print("Использование: python compile.py <путь_к_файлу.jack_или_папке>")
        return

    target_path = Path(sys.argv[1])
    
    if not target_path.exists():
        print(f"Путь {target_path} не существует.")
        return

    # Поддержка компиляции как отдельного файла, так и целой папки
    if target_path.is_file():
        compile_file(target_path)
    elif target_path.is_dir():
        print(f"Сканирование папки: {target_path.name}")
        for file in target_path.glob("*.jack"):
            compile_file(file)

if __name__ == "__main__":
    main()
