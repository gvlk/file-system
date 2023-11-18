import pickle
import sys
from math import ceil


class FileSystem:
    def __init__(self, size) -> None:
        self.fs_path = "furgfs.fs"

        # 0.04MB = 40.96KB || 4 blocks
        if size < 0.04:
            raise Exception("Escolha um tamanho maior para o sistema.")

        self.space = round(size * 1024 * 1024)  # 1 MB = 1048576 B
        self.block_size = 4 * 1024  # 4 KB = 4096 B
        self.blocks_total = self.space // self.block_size  # 200 MB / 4096 B = 51.200 blocks
        self.fs = [b"0" * self.block_size] * self.blocks_total
        self.header_size_blocks = 1

        fat_size_blocks = self.prepare_fat()
        address_fat = self.header_size_blocks
        address_root, root_size_blocks = self.prepare_root(fat_size_blocks)
        address_data = address_root + root_size_blocks

        self.prepare_header(address_fat, address_root, address_data)

        self.save()

    def __str__(self) -> str:
        system_blocks = self.read_block(0)[5] + 1
        system_bytes = system_blocks * self.block_size

        string = f"\n" \
                 f"{'*' * 50}\n" \
                 f"{self.fs_path}\n" \
                 f"Espaço total: {self.space}B | {self.space // 1024}KB | {self.space // 1048576}MB\n" \
                 f"Dados do sistema: {system_bytes}B | {system_bytes // 1024}KB | {system_bytes / 1048576:.1f}MB\n" \
                 f"Tamanho do bloco: {round(self.block_size / 1024)}KB\n" \
                 f"Quantidade total de blocos: {self.blocks_total}\n" \
                 f"Quantidade de blocos para o sistema: {system_blocks}\n" \
                 f"Quantidade de blocos para os dados: {self.blocks_total - system_blocks}\n" \
                 f"{'*' * 50}\n"
        return string

    def save(self) -> None:
        with open(self.fs_path, "wb") as fsfile:
            pickle.dump(self, fsfile)

    def read_block(self, block: int):
        return pickle.loads(self.fs[block])

    def update_fs(self, update_sheet: dict):
        for key, val in update_sheet.items():
            self.fs[key] = val
        self.save()

    def prepare_header(self, address_fat: int, address_root: int, address_data: int) -> None:
        header = (
            self.header_size_blocks,
            self.space,
            self.block_size,
            address_fat,
            address_root,
            address_data
        )
        self.fs[0] = pickle.dumps(header)

    def prepare_fat(self) -> int:
        fat_size = self.blocks_total - 1
        fat_size_blocks = ceil(sys.getsizeof([0] * fat_size) / self.block_size)

        # Each block can contain a list of n-1 elements
        n = 0
        while True:
            n += 1
            size_blocks = ceil(sys.getsizeof([-1] * n) / self.block_size)
            if size_blocks > 1:
                break

        empty = [-2] * (n - 1)
        for i in range(1, 1 + fat_size_blocks):
            self.fs[i] = pickle.dumps(empty)

        return fat_size_blocks

    def prepare_root(self, fat_size_blocks: int) -> tuple:
        filename_max_size = 64  # 64 B

        root_size = self.blocks_total - self.header_size_blocks - fat_size_blocks
        root_size_blocks = ceil(sys.getsizeof({str(i): i for i in range(root_size)}) / self.block_size)
        address_root = self.header_size_blocks + fat_size_blocks
        for i in range(address_root, address_root + root_size_blocks):
            self.fs[i] = pickle.dumps(dict())

        return address_root, root_size_blocks

    def copy_to_fs(self, file_path: str) -> None:
        update_sheet = dict()
        header = self.read_block(0)
        address_fat = header[3]
        address_root = header[4]
        address_data = header[5]
        fat_section_size = len(self.read_block(address_fat))

        # Test if file is already in the system
        for root_section_index in range(address_root, address_data):
            root_section = self.read_block(root_section_index)
            if file_path in root_section:
                raise Exception(f"O arquivo '{file_path}' já existe no sistema.")

        # Divide file into blocks
        with open(file_path, "r") as f:
            file_contents = f.read()
        serialized_contents = pickle.dumps(file_contents)
        contents_size = len(serialized_contents)
        data_slices = [serialized_contents[i:i + self.block_size] for i in range(0, contents_size, self.block_size)]

        # Find empty blocks
        blocks_index = list()
        blocks_needed = len(data_slices)
        for fat_section_index in range(address_fat, address_root):
            fat_section = self.read_block(fat_section_index)
            for i, entry in enumerate(fat_section):
                if len(blocks_index) == blocks_needed:
                    break
                if entry == -2:
                    blocks_index.append(i + ((fat_section_index - 1) * fat_section_size))
            if len(blocks_index) == blocks_needed:
                break
        if len(blocks_index) != blocks_needed:
            raise Exception(f"Não há espaço suficiente para salvar o arquivo '{file_path}'")

        # Update FAT
        fat_section_index = int()
        fat_section = list()
        for i, block_index in enumerate(blocks_index):
            if fat_section_index != address_fat + (block_index // fat_section_size):
                fat_section_index = address_fat + (block_index // fat_section_size)
                fat_section = self.read_block(fat_section_index)
            try:
                fat_section[block_index % fat_section_size] = blocks_index[i + 1]
            except IndexError:
                fat_section[block_index % fat_section_size] = -1
            update_sheet[address_fat + (block_index // fat_section_size)] = pickle.dumps(fat_section)

        # Update data
        for i, data_slice in enumerate(data_slices):
            update_sheet[blocks_index[i] + address_data] = data_slice

        # Update root
        root_section = dict()
        root_section_index = int()
        for root_section_index in range(address_root, address_data):
            root_section = self.read_block(root_section_index)
            root_section_limit = (self.blocks_total - self.header_size_blocks - address_root - address_fat) // (
                    address_data - address_root)
            if len(root_section) < root_section_limit:
                break
        root_section[file_path] = blocks_index[0]
        update_sheet[root_section_index] = pickle.dumps(root_section)

        self.update_fs(update_sheet)

    def copy_from_fs(self, file_name: str) -> None:
        header = self.read_block(0)
        address_fat = header[3]
        address_root = header[4]
        address_data = header[5]
        fat_section_size = len(self.read_block(address_fat))

        # Find file in the system
        first_block = -1
        for root_section_index in range(address_root, address_data):
            root_section = self.read_block(root_section_index)
            if file_name in root_section:
                first_block = root_section[file_name]
                break
        if first_block == -1:
            raise Exception(f"O arquivo '{file_name}' não existe.")

        # Find the file blocks and join them
        serialized_contents = b""
        current_block = first_block
        fat_section = self.read_block(address_fat + first_block // fat_section_size)
        while current_block != -1:
            data_slice = self.fs[current_block + address_data]
            serialized_contents += data_slice
            current_block = fat_section[current_block]

        # Write contents to a file
        file_contents = pickle.loads(serialized_contents)
        with open(file_name, 'w') as text_file:
            text_file.write(str(file_contents))

    def rename(self, old_name: str, new_name: str) -> None:
        update_sheet = dict()
        header = self.read_block(0)
        address_root = header[4]
        address_data = header[5]

        # Find file in the system
        root_section_index = -1
        root_section = dict()
        found = False
        for root_section_index in range(address_root, address_data):
            root_section = self.read_block(root_section_index)
            if old_name in root_section:
                found = True
                root_section[new_name] = root_section.pop(old_name)
                break
        if not found:
            raise Exception(f"O arquivo '{old_name}' não existe.")

        update_sheet[root_section_index] = pickle.dumps(root_section)
        self.update_fs(update_sheet)

    def remove(self, file_name: str) -> None:
        update_sheet = dict()
        header = self.read_block(0)
        address_fat = header[3]
        address_root = header[4]
        address_data = header[5]
        fat_section_size = len(self.read_block(address_fat))

        # Find file in the system and clean root entry
        root_section_index = -1
        root_section = dict()
        first_block = -1
        for root_section_index in range(address_root, address_data):
            root_section = self.read_block(root_section_index)
            if file_name in root_section:
                first_block = root_section[file_name]
                del root_section[file_name]
                break
        if first_block == -1:
            raise Exception(f"O arquivo '{file_name}' não existe.")
        update_sheet[root_section_index] = pickle.dumps(root_section)

        # Clean FAT entries
        current_block = first_block
        fat_section_index = address_fat + (current_block // fat_section_size)
        fat_section = self.read_block(fat_section_index)
        while current_block != -1:
            if fat_section_index != address_fat + (current_block // fat_section_size):
                update_sheet[fat_section_index] = pickle.dumps(fat_section)
                fat_section_index = address_fat + current_block // fat_section_size
                fat_section = self.read_block(fat_section_index)
            next_block = fat_section[current_block % fat_section_size]
            fat_section[current_block % fat_section_size] = -2
            current_block = next_block
        update_sheet[fat_section_index] = pickle.dumps(fat_section)

        self.update_fs(update_sheet)

    def list_files(self) -> tuple:
        header = self.read_block(0)
        address_root = header[4]
        address_data = header[5]

        # Iterate over root
        files = list()
        for root_section_index in range(address_root, address_data):
            root_section = self.read_block(root_section_index)
            for file_name in root_section.keys():
                files.append(file_name)

        print("\n")
        print(f"Total de arquivos: {len(files)}")
        for f in files:
            print(f)

        return tuple(files)

    def usage_info(self) -> tuple:
        header = self.read_block(0)
        address_fat = header[3]
        address_root = header[4]

        blocks_in_usage = int()

        for fat_section_index in range(address_fat, address_root):
            fat_section = self.read_block(fat_section_index)
            for entry in fat_section:
                if entry != -2:
                    blocks_in_usage += 1

        space_used = (blocks_in_usage * self.block_size) / 1048576
        space_total = self.space / 1048576
        space_free = space_total - space_used

        print("\n")
        if space_total >= 1:
            print(f"{space_free:.1f}MB livres de {space_total:.1f}MB")
        else:
            print(f"{space_free * 1024:.1f}KB livres de {space_total * 1024:.1f}KB")
        print(f"{(space_used / space_total) * 100:.1f}% do espaço ocupado")

        return space_used, space_free


if __name__ == '__main__':
    fs: FileSystem
    # fs = FileSystem(200)
    # 200MB ADDRESSES - Header: 0 | FAT: 1 | Root: 102 | Data: 572
