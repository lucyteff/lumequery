
from src.ai.gemini_client import generate_text


def main():
    response = generate_text(
        "Explain in one sentence what a data analyst does."
    )

    print("GEMINI CONNECTION SUCCESSFUL")
    print(response)


if __name__ == "__main__":
    main()
