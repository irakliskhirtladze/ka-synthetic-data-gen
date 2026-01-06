# from generator.gen import generate_imgs
from generator.ka_dictionary_builder import build_ka_dict
from utils import BASE_DIR


def main():
    while True:
        mode = input("type [1] and enter to choose generate mode or [2] to choose train mode: ")
        if mode == "1":
            print("Generate mode is selected")
            build_ka_dict(BASE_DIR / "generator" / "ka-dict.txt")
            # generate_imgs()
            return
        elif mode == "2":
            print("Training mode is selected")
            return
        else:
            print("Not supported mode. Retrying...")
            continue
        

if __name__ == "__main__":
    main()
