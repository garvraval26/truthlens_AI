# model.py
# ==============================================================
# AI Model Layer
# Fake News Detection + Media Bias Analysis
# ==============================================================

import re
import logging

import numpy as np
import streamlit as st
import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline,
)

from config import (
    PRIMARY_MODEL_NAME,
    FALLBACK_MODEL_NAME,
    BIAS_MODEL_NAME,
    MAX_SEQUENCE_LENGTH,
    MODEL_CACHE_DIR,
)


# ==============================================================
# LOGGING
# ==============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DEVICE = 0 if torch.cuda.is_available() else -1


# ==============================================================
# EXCEPTIONS
# ==============================================================

class ModelLoadError(Exception):
    """Raised when no valid fake-news model can be loaded."""
    pass


# ==============================================================
# LABEL NORMALIZATION
# ==============================================================

def normalize_label(label):
    """
    Converts model labels into our standard labels:
        Fake
        Real

    This prevents accidental dependence on LABEL_0/LABEL_1 ordering.
    """

    label = str(label).strip().lower()

    if "fake" in label:
        return "Fake"

    if "real" in label:
        return "Real"

    if "false" in label:
        return "Fake"

    if "true" in label:
        return "Real"

    return None


def get_label_mapping(model):
    """
    Reads the label mapping from the actual Hugging Face model.
    """

    id2label = model.config.id2label

    mapping = {}

    for index, raw_label in id2label.items():
        normalized = normalize_label(raw_label)

        if normalized is not None:
            mapping[int(index)] = normalized

    # Some models may not have useful id2label metadata.
    # For the known fake-news models, use the documented mapping.
    if len(mapping) < 2:
        mapping = {
            0: "Fake",
            1: "Real",
        }

    # Make sure we actually have both classes.
    labels = set(mapping.values())

    if "Fake" not in labels or "Real" not in labels:
        raise ModelLoadError(
            f"Could not identify Fake/Real labels from model: {id2label}"
        )

    logger.info(f"Using model label mapping: {mapping}")

    return mapping


# ==============================================================
# LOAD FAKE NEWS MODEL
# ==============================================================

@st.cache_resource(show_spinner=False)
def load_fake_news_model():
    """
    Loads an actual fine-tuned fake-news classifier.

    IMPORTANT:
    We DO NOT fall back to a generic DistilBERT/BERT model.
    A generic language model is NOT a fake-news classifier.
    """

    candidates = [
        PRIMARY_MODEL_NAME,
        FALLBACK_MODEL_NAME,
    ]

    last_error = None

    for model_name in candidates:

        if not model_name:
            continue

        try:

            logger.info(
                f"Loading fake-news model: {model_name}"
            )

            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=MODEL_CACHE_DIR,
            )

            model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                cache_dir=MODEL_CACHE_DIR,
            )

            model.eval()

            label_mapping = get_label_mapping(model)

            logger.info(
                f"Successfully loaded fake-news model: {model_name}"
            )

            return (
                tokenizer,
                model,
                model_name,
                label_mapping,
            )

        except Exception as e:

            logger.exception(
                f"Could not load model {model_name}"
            )

            last_error = e

    raise ModelLoadError(
        "Could not load a valid fake-news classification model. "
        f"Last error: {last_error}"
    )


# ==============================================================
# LOAD BIAS MODEL
# ==============================================================

@st.cache_resource(show_spinner=False)
def load_bias_pipeline():

    try:

        logger.info(
            f"Loading bias model: {BIAS_MODEL_NAME}"
        )

        bias_pipe = pipeline(
            "zero-shot-classification",
            model=BIAS_MODEL_NAME,
            device=DEVICE,
        )

        return bias_pipe

    except Exception as e:

        logger.warning(
            f"Bias model failed to load: {e}"
        )

        return None


# ==============================================================
# BUILD MODEL INPUT
# ==============================================================

def build_model_input(headline, text):
    """
    Builds the input in the format expected by the
    hamzab RoBERTa fake-news classifier.

    Title + content are both used.
    """

    headline = (headline or "").strip()
    text = (text or "").strip()

    if not text:
        raise ValueError(
            "Article content cannot be empty."
        )

    if headline:

        return (
            f"<title> {headline} "
            f"<content> {text} <end>"
        )

    return (
        f"<title> "
        f"<content> {text} <end>"
    )


# ==============================================================
# FAKE NEWS PREDICTION
# ==============================================================

def predict_fake_news(
    text: str,
    headline: str = "",
) -> dict:

    if not text or not text.strip():

        raise ValueError(
            "Input article text is empty."
        )

    tokenizer, model, model_name, label_mapping = (
        load_fake_news_model()
    )

    # ----------------------------------------------------------
    # IMPORTANT:
    # Use BOTH headline and article content.
    # ----------------------------------------------------------

    model_input = build_model_input(
        headline,
        text,
    )

    inputs = tokenizer(
        model_input,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=MAX_SEQUENCE_LENGTH,
    )

    # Put tensors on same device as model.
    model_device = next(
        model.parameters()
    ).device

    inputs = {
        key: value.to(model_device)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model(**inputs)

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1,
        )[0]

    probabilities = probabilities.detach().cpu().numpy()

    # ----------------------------------------------------------
    # Convert model outputs to Fake / Real probabilities.
    # ----------------------------------------------------------

    fake_probability = 0.0
    real_probability = 0.0

    for index, probability in enumerate(probabilities):

        label = label_mapping.get(index)

        if label == "Fake":

            fake_probability = float(probability)

        elif label == "Real":

            real_probability = float(probability)

    # ----------------------------------------------------------
    # Safety check
    # ----------------------------------------------------------

    total = fake_probability + real_probability

    if total <= 0:

        raise ModelLoadError(
            "The model did not return valid Fake/Real probabilities."
        )

    # Normalize so the two probabilities add up to 1.
    fake_probability /= total
    real_probability /= total

    # ----------------------------------------------------------
    # Prediction
    # ----------------------------------------------------------

    if real_probability >= fake_probability:

        prediction = "Real"
        confidence = real_probability

    else:

        prediction = "Fake"
        confidence = fake_probability

    # ----------------------------------------------------------
    # Confidence category
    # ----------------------------------------------------------

    if confidence >= 0.80:

        confidence_level = "High"

    elif confidence >= 0.60:

        confidence_level = "Medium"

    else:

        confidence_level = "Low"

    # Difference between the two classes.
    margin = abs(
        real_probability - fake_probability
    )

    # ----------------------------------------------------------
    # Uncertainty
    #
    # IMPORTANT:
    # A close 51/49 prediction should not be presented as
    # a highly reliable result.
    # ----------------------------------------------------------

    if margin < 0.10:

        certainty = "Uncertain"

    elif margin < 0.25:

        certainty = "Moderate"

    else:

        certainty = "Strong"

    return {

        "prediction": prediction,

        "confidence": round(
            float(confidence),
            4,
        ),

        "confidence_level": confidence_level,

        "certainty": certainty,

        "margin": round(
            float(margin),
            4,
        ),

        "probabilities": {

            "Real": round(
                float(real_probability),
                4,
            ),

            "Fake": round(
                float(fake_probability),
                4,
            ),
        },

        "model_used": model_name,
    }


# ==============================================================
# BIAS DETECTION
# ==============================================================

def predict_bias(text: str) -> dict:

    if not text or not text.strip():

        return {
            "bias": "Unknown",
            "confidence": 0.0,
            "scores": {},
        }

    bias_pipe = load_bias_pipeline()

    if bias_pipe is None:

        return {
            "bias": "Unavailable",
            "confidence": 0.0,
            "scores": {},
        }

    labels = [
        "left leaning",
        "central",
        "right leaning",
    ]

    try:

        # Limit input because zero-shot models can become
        # unnecessarily expensive on huge articles.
        analysis_text = text[:6000]

        result = bias_pipe(
            analysis_text,
            candidate_labels=labels,
            multi_label=False,
        )

        result_labels = result["labels"]
        result_scores = result["scores"]

        scores = {}

        for label, score in zip(
            result_labels,
            result_scores,
        ):

            scores[label] = round(
                float(score),
                4,
            )

        top_label = result_labels[0]
        top_score = float(result_scores[0])

        if top_label == "left leaning":

            bias = "Left Leaning"

        elif top_label == "right leaning":

            bias = "Right Leaning"

        else:

            bias = "Central"

        return {
            "bias": bias,
            "confidence": round(
                top_score,
                4,
            ),
            "scores": scores,
        }

    except Exception as e:

        logger.warning(
            f"Bias prediction failed: {e}"
        )

        return {
            "bias": "Unavailable",
            "confidence": 0.0,
            "scores": {},
        }


# ==============================================================
# EXPLAINABILITY
# ==============================================================

SENSATIONAL_WORDS = {
    "shocking",
    "unbelievable",
    "secret",
    "exposed",
    "miracle",
    "conspiracy",
    "outrage",
    "slams",
    "destroys",
    "bombshell",
    "breaking",
    "urgent",
    "hoax",
    "cover-up",
    "scandal",
    "explosive",
    "insane",
    "terrifying",
    "warning",
    "banned",
    "leaked",
}


CREDIBLE_WORDS = {
    "according to",
    "study",
    "research",
    "reported",
    "data",
    "official",
    "confirmed",
    "statement",
    "spokesperson",
    "analysis",
    "evidence",
    "investigation",
    "sources say",
    "verified",
    "peer-reviewed",
    "survey",
}


def explain_prediction(
    text: str,
    prediction: str,
) -> dict:

    if not text:

        return {
            "positive_indicators": [],
            "negative_indicators": [],
            "highlighted_words": [],
            "summary": "",
        }

    lower_text = text.lower()

    found_sensational = [
        word
        for word in SENSATIONAL_WORDS
        if word in lower_text
    ]

    found_credible = [
        word
        for word in CREDIBLE_WORDS
        if word in lower_text
    ]

    highlighted_words = []

    # Sort longer phrases first so that phrases such as
    # "according to" are checked before individual words.
    all_terms = sorted(
        SENSATIONAL_WORDS | CREDIBLE_WORDS,
        key=len,
        reverse=True,
    )

    for term in all_terms:

        if term in lower_text:

            if term in SENSATIONAL_WORDS:

                highlighted_words.append({
                    "word": term,
                    "type": "negative",
                })

            else:

                highlighted_words.append({
                    "word": term,
                    "type": "positive",
                })

    # ----------------------------------------------------------
    # IMPORTANT:
    # Clearly state that this is heuristic information.
    # It is NOT the reason the neural network made its decision.
    # ----------------------------------------------------------

    if prediction == "Fake" and found_sensational:

        summary = (
            "The article contains language commonly associated "
            "with sensational or misleading reporting. These "
            "are heuristic indicators and are not direct evidence "
            "that the article is false."
        )

    elif prediction == "Real" and found_credible:

        summary = (
            "The article contains references commonly associated "
            "with formal reporting, sources, research, or evidence. "
            "These are heuristic indicators and do not independently "
            "verify that the claims are true."
        )

    else:

        summary = (
            "The neural classifier primarily uses learned language "
            "patterns. The highlighted terms are heuristic indicators "
            "and should not be interpreted as the model's direct "
            "reasoning."
        )

    return {

        "positive_indicators": found_credible,

        "negative_indicators": found_sensational,

        "highlighted_words": highlighted_words[:30],

        "summary": summary,
    }


# ==============================================================
# COMPLETE ARTICLE ANALYSIS
# ==============================================================

def analyze_article(
    text: str,
    headline: str = "",
) -> dict:

    if not text or not text.strip():

        raise ValueError(
            "Article content cannot be empty."
        )

    # Fake-news prediction uses headline + content.
    fake_news_result = predict_fake_news(
        text=text,
        headline=headline,
    )

    # Bias prediction uses article content.
    bias_result = predict_bias(text)

    explanation = explain_prediction(
        text,
        fake_news_result["prediction"],
    )

    return {

        **fake_news_result,

        "bias": bias_result["bias"],

        "bias_confidence": bias_result["confidence"],

        "bias_scores": bias_result["scores"],

        "explanation": explanation,
    }