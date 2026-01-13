from generator.gen import generate_imgs, dataset_to_hf
        

if __name__ == "__main__":
    while True:
        user_input = input("How many images per font would you like to generate?: ")
        if not user_input.isdigit() or int(user_input) <= 0:
            print("\nPlease enter a positive integer.")
            continue
        else:
            break
    generate_imgs(int(user_input))

    dataset_to_hf()
