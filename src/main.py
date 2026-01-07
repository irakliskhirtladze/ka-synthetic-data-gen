from generator.gen import generate_imgs
from generator.dictionaries.ka_dictionary_builder import build_ka_dict


def main():
    while True:
        mode = input("type [1] and enter to choose generate mode or [2] to choose train mode: ")
        if mode == "1":
            print("Generate mode is selected")
            generate_imgs()
            return
        elif mode == "2":
            print("Training mode is selected")
            return
        else:
            print("Not supported mode. Retrying...")
            continue
        

if __name__ == "__main__":
    main()
