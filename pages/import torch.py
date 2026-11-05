import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)


MODEL_NAME = "hamzab/roberta-fake-news-classification"


print("Loading model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME
)

model.eval()


def predict_fake(title, text):

    # EXACT FORMAT FROM THE MODEL'S DOCUMENTATION
    input_str = (
        "<title>"
        + title
        + "<content>"
        + text
        + "<end>"
    )

    inputs = tokenizer.encode_plus(
        input_str,
        max_length=512,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )

    with torch.no_grad():

        output = model(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"]
        )

    probabilities = torch.softmax(
        output.logits,
        dim=-1
    )[0]

    fake_probability = probabilities[0].item()
    real_probability = probabilities[1].item()

    print("\n==============================")
    print("MODEL TEST")
    print("==============================")

    print("Fake probability:",
          round(fake_probability * 100, 2), "%")

    print("Real probability:",
          round(real_probability * 100, 2), "%")

    if fake_probability > real_probability:
        print("FINAL: FAKE")
    else:
        print("FINAL: REAL")

    print("==============================")


# ----------------------------------------------------------
# TEST 1
# ----------------------------------------------------------

title = "Scientists Discover a New Planet Where It Rains Gold Every Night"

text = """
A team of scientists has reportedly discovered a new planet
located outside our solar system where gold particles fall
from the sky every night. Researchers claim that the planet
has an atmosphere rich in precious metals, making it unlike
anything previously observed. The discovery has allegedly
attracted the attention of governments and private companies
interested in future space exploration. Scientists are now
said to be planning a mission to collect samples from the
planet.
"""


predict_fake(title, text)