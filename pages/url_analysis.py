import streamlit as st
from datetime import datetime

from model import analyze_article
from utils import fetch_article_from_url
import database


def render():
    st.title("🔗 URL Analyzer")
    st.write(
        "Enter a news article URL and TruthLens AI will extract the article "
        "and analyze it for fake-news probability."
    )

    st.divider()

    # ==========================================================
    # URL INPUT
    # ==========================================================

    url = st.text_input(
        "🔗 News Article URL",
        placeholder="https://example.com/news/article",
    )

    analyze_button = st.button(
        "🔍 Analyze URL",
        type="primary",
        use_container_width=True,
    )

    if not analyze_button:
        return

    # ==========================================================
    # CHECK URL
    # ==========================================================

    if not url.strip():
        st.warning("⚠️ Please enter a news article URL.")
        return

    # ==========================================================
    # STEP 1: EXTRACT ARTICLE
    # ==========================================================

    with st.spinner("🌐 Fetching and extracting article..."):

        try:
            article_data = fetch_article_from_url(url.strip())

        except Exception as e:
            st.error(
                f"❌ Could not extract the article from this URL.\n\n"
                f"Error: {str(e)}"
            )
            return

    if not article_data:
        st.error("❌ No article data could be extracted from this URL.")
        return

    # ==========================================================
    # GET EXTRACTED DATA
    # ==========================================================

    article_title = article_data.get("title", "").strip()
    article_text = article_data.get("text", "").strip()
    source_domain = article_data.get("source_domain", "")

    if not article_title:
        st.warning(
            "⚠️ The article title could not be extracted. "
            "The model will analyze the article text only."
        )

    if not article_text:
        st.error(
            "❌ No article text could be extracted from this URL."
        )
        return

    # ==========================================================
    # STEP 2: SHOW EXTRACTED ARTICLE
    # ==========================================================

    st.success("✅ Article extracted successfully!")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### 📰 Article Title")
        st.write(
            article_title
            if article_title
            else "Not available"
        )

    with col2:
        st.write("### 🌐 Source")
        st.write(
            source_domain
            if source_domain
            else "Unknown"
        )

    # ==========================================================
    # STEP 3: AI ANALYSIS
    # ==========================================================

    with st.spinner("🤖 Analyzing article with AI..."):

        try:
            # IMPORTANT:
            # Send BOTH title and article content.
            result = analyze_article(
                text=article_text,
                headline=article_title,
            )

        except Exception as e:
            st.error(
                f"❌ Error while analyzing the article.\n\n"
                f"Error: {str(e)}"
            )
            return

    # ==========================================================
    # STEP 4: DISPLAY RESULT
    # ==========================================================

    _render_result(
        result=result,
        headline=article_title,
        source=source_domain,
        source_url=url.strip(),
        analysis_type="url",
        original_text=article_text,
    )


def _render_result(
    result,
    headline="",
    source="",
    source_url="",
    analysis_type="url",
    original_text="",
):
    """
    Display the fake-news prediction and analysis results.
    """

    st.divider()

    st.subheader("🤖 AI Analysis Result")

    # ==========================================================
    # GET PREDICTION
    # ==========================================================

    prediction = result.get(
        "prediction",
        "Unknown"
    )

    # ==========================================================
    # GET CONFIDENCE
    #
    # model.py returns confidence between 0 and 1.
    # Example:
    # 0.9987 -> 99.87%
    # ==========================================================

    confidence_decimal = result.get(
        "confidence",
        0.0
    )

    try:
        confidence_decimal = float(
            confidence_decimal
        )
    except (ValueError, TypeError):
        confidence_decimal = 0.0

    confidence_percent = confidence_decimal * 100

    # ==========================================================
    # GET PROBABILITIES
    #
    # model.py returns:
    #
    # "probabilities": {
    #     "Real": 0.9987,
    #     "Fake": 0.0013
    # }
    # ==========================================================

    probabilities = result.get(
        "probabilities",
        {}
    )

    try:
        fake_probability_decimal = float(
            probabilities.get("Fake", 0.0)
        )
    except (ValueError, TypeError):
        fake_probability_decimal = 0.0

    try:
        real_probability_decimal = float(
            probabilities.get("Real", 0.0)
        )
    except (ValueError, TypeError):
        real_probability_decimal = 0.0

    # Convert decimal -> percentage

    fake_probability = fake_probability_decimal * 100
    real_probability = real_probability_decimal * 100

    # ==========================================================
    # PREDICTION BOX
    # ==========================================================

    if str(prediction).lower() == "fake":

        st.error(
            f"🚨 **Prediction: FAKE NEWS**\n\n"
            f"Confidence: **{confidence_percent:.2f}%**"
        )

    elif str(prediction).lower() == "real":

        st.success(
            f"✅ **Prediction: REAL NEWS**\n\n"
            f"Confidence: **{confidence_percent:.2f}%**"
        )

    else:

        st.warning(
            f"⚠️ **Prediction: {prediction}**\n\n"
            f"Confidence: **{confidence_percent:.2f}%**"
        )

    # ==========================================================
    # PROBABILITY METRICS
    # ==========================================================

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "🚨 Fake Probability",
            f"{fake_probability:.2f}%"
        )

    with col2:
        st.metric(
            "✅ Real Probability",
            f"{real_probability:.2f}%"
        )

    # ==========================================================
    # MODEL PROBABILITIES
    # ==========================================================

    st.write("### 📊 Model Probabilities")

    st.write(
        f"Fake: **{fake_probability:.2f}%**"
    )

    st.progress(
        min(
            max(
                fake_probability_decimal,
                0.0
            ),
            1.0
        )
    )

    st.write(
        f"Real: **{real_probability:.2f}%**"
    )

    st.progress(
        min(
            max(
                real_probability_decimal,
                0.0
            ),
            1.0
        )
    )

    # ==========================================================
    # CERTAINTY
    # ==========================================================

    certainty = result.get(
        "certainty"
    )

    confidence_level = result.get(
        "confidence_level"
    )

    if certainty or confidence_level:

        st.write("### 🎯 Confidence Information")

        info_col1, info_col2 = st.columns(2)

        with info_col1:

            if confidence_level:
                st.write(
                    f"**Confidence Level:** "
                    f"{confidence_level}"
                )

        with info_col2:

            if certainty:
                st.write(
                    f"**Certainty:** "
                    f"{certainty}"
                )

    # ==========================================================
    # POLITICAL BIAS
    # ==========================================================

    bias = result.get("bias")

    if bias:

        st.divider()

        st.subheader("🧭 Political Bias")

        st.write(
            f"**Bias:** {bias}"
        )

        bias_confidence = result.get(
            "bias_confidence"
        )

        if bias_confidence is not None:

            try:

                bias_confidence_percent = (
                    float(bias_confidence) * 100
                )

                st.write(
                    f"**Bias Confidence:** "
                    f"{bias_confidence_percent:.2f}%"
                )

            except (ValueError, TypeError):
                pass

    # ==========================================================
    # EXPLANATION
    # ==========================================================

    explanation = result.get(
        "explanation"
    )

    if explanation:

        st.divider()

        st.subheader("💡 Explanation")

        if isinstance(explanation, dict):

            summary = explanation.get(
                "summary"
            )

            if summary:
                st.write(summary)

            positive = explanation.get(
                "positive_indicators",
                []
            )

            negative = explanation.get(
                "negative_indicators",
                []
            )

            if positive:

                st.write(
                    "**Credible-style indicators:**"
                )

                for item in positive:
                    st.write(f"• {item}")

            if negative:

                st.write(
                    "**Sensational-style indicators:**"
                )

                for item in negative:
                    st.write(f"• {item}")

        elif isinstance(explanation, list):

            for item in explanation:
                st.write(f"• {item}")

        else:

            st.write(explanation)

    # ==========================================================
    # ARTICLE INFORMATION
    # ==========================================================

    st.divider()

    st.subheader("📰 Article Information")

    info_col1, info_col2 = st.columns(2)

    with info_col1:

        st.write("**Title:**")

        if headline:
            st.write(headline)
        else:
            st.write("Not available")

    with info_col2:

        st.write("**Source:**")

        if source:
            st.write(source)
        else:
            st.write("Unknown")

    if source_url:

        st.write("**URL:**")

        st.write(source_url)

    # ==========================================================
    # EXTRACTED ARTICLE TEXT
    # ==========================================================

    with st.expander(
        "📄 View extracted article text"
    ):

        if original_text:

            st.text_area(
                "Extracted content",
                original_text,
                height=400,
                disabled=True,
                label_visibility="collapsed",
            )

        else:

            st.info(
                "No extracted text available."
            )

    # ==========================================================
    # SAVE TO DATABASE
    # ==========================================================

    try:

        database.save_analysis(
            headline=headline,
            source=source,
            prediction=prediction,
            confidence=confidence_percent,
            bias=bias or "",
            analysis_type=analysis_type,
            source_url=source_url,
            article_text=original_text,
            created_at=datetime.now(),
        )

    except TypeError:

        # Fallback for older database function
        try:

            database.save_analysis(
                headline,
                source,
                prediction,
                confidence_percent,
                source_url,
                original_text,
            )

        except Exception:
            pass

    except Exception:
        # Database failure should not prevent
        # the AI result from being displayed.
        pass