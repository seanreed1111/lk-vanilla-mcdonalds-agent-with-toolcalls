"""Tests for keyword interception LLM wrapper.

This test suite verifies that the KeywordInterceptLLM correctly intercepts
user input containing fruit-related keywords and returns a fixed response,
while delegating non-keyword input to the wrapped LLM.
"""

import pytest
from livekit.agents import AgentSession

from app import Assistant
from keyword_intercept_llm import KeywordInterceptLLM
from mock_llm import SimpleMockLLM


@pytest.mark.asyncio
async def test_intercepts_cherries_keyword() -> None:
    """Test that 'cherries' keyword triggers fixed response."""
    base_llm = SimpleMockLLM(response_text="I would talk about cherries normally")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["cherries"],
        response_text="I don't like fruit",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())
        result = await session.run(user_input="I love cherries")

        # Verify exact response
        event = result.expect.next_event().is_message(role="assistant")
        # Get the actual content from the event
        actual_content = event._event.item.text_content  # type: ignore
        assert actual_content == "I don't like fruit"


@pytest.mark.asyncio
async def test_intercepts_cherry_keyword() -> None:
    """Test that 'cherry' keyword triggers fixed response."""
    base_llm = SimpleMockLLM(response_text="Cherry is delicious")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["cherry"],
        response_text="I don't like fruit",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())
        result = await session.run(user_input="What about cherry pie?")

        event = result.expect.next_event().is_message(role="assistant")
        actual_content = event._event.item.text_content  # type: ignore
        assert actual_content == "I don't like fruit"


@pytest.mark.asyncio
async def test_intercepts_banana_keyword() -> None:
    """Test that 'banana' keyword triggers fixed response."""
    base_llm = SimpleMockLLM(response_text="Bananas are nutritious")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["banana"],
        response_text="I don't like fruit",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())
        result = await session.run(user_input="Do you like bananas?")

        event = result.expect.next_event().is_message(role="assistant")
        actual_content = event._event.item.text_content  # type: ignore
        assert actual_content == "I don't like fruit"


@pytest.mark.asyncio
async def test_intercepts_apple_keyword() -> None:
    """Test that 'apple' keyword triggers fixed response."""
    base_llm = SimpleMockLLM(response_text="Apples are healthy")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["apple"],
        response_text="I don't like fruit",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())
        result = await session.run(user_input="Can you tell me about apples?")

        event = result.expect.next_event().is_message(role="assistant")
        actual_content = event._event.item.text_content  # type: ignore
        assert actual_content == "I don't like fruit"


@pytest.mark.asyncio
async def test_intercepts_fruit_keyword() -> None:
    """Test that 'fruit' keyword triggers fixed response."""
    base_llm = SimpleMockLLM(response_text="Fruit is good for you")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["fruit"],
        response_text="I don't like fruit",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())
        result = await session.run(user_input="What's your favorite fruit?")

        event = result.expect.next_event().is_message(role="assistant")
        actual_content = event._event.item.text_content  # type: ignore
        assert actual_content == "I don't like fruit"


@pytest.mark.asyncio
async def test_case_insensitive_matching() -> None:
    """Test that keyword matching is case-insensitive."""
    base_llm = SimpleMockLLM(response_text="Normal response")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["apple"],
        response_text="I don't like fruit",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())

        # Test uppercase
        result = await session.run(user_input="I love APPLE pie")
        event = result.expect.next_event().is_message(role="assistant")
        actual_content = event._event.item.text_content  # type: ignore
        assert actual_content == "I don't like fruit"


@pytest.mark.asyncio
async def test_delegates_non_keyword_input() -> None:
    """Test that non-keyword input is delegated to wrapped LLM."""
    base_llm = SimpleMockLLM(
        response_text="You knew the job was dangerous when you took it, Fred."
    )
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["fruit", "apple", "banana"],
        response_text="I don't like fruit",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())
        result = await session.run(user_input="What's the weather like?")

        event = result.expect.next_event().is_message(role="assistant")
        actual_content = event._event.item.text_content  # type: ignore
        assert (
            actual_content == "You knew the job was dangerous when you took it, Fred."
        )


@pytest.mark.asyncio
async def test_all_default_keywords() -> None:
    """Test that all default fruit keywords are intercepted correctly."""
    base_llm = SimpleMockLLM(response_text="Normal LLM response")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        # Using default keywords
        response_text="I don't like fruit",
    )

    test_inputs = [
        "I love cherries",
        "What about cherry?",
        "Banana bread is great",
        "Do you like apples?",
        "What's your favorite fruit?",
    ]

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())

        for user_input in test_inputs:
            result = await session.run(user_input=user_input)
            event = result.expect.next_event().is_message(role="assistant")
            actual_content = event._event.item.text_content  # type: ignore
            assert actual_content == "I don't like fruit", (
                f"Failed for input: {user_input}"
            )


@pytest.mark.asyncio
async def test_keyword_in_sentence() -> None:
    """Test that keywords embedded in sentences are detected."""
    base_llm = SimpleMockLLM(response_text="Normal response")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["cherry"],
        response_text="I don't like fruit",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())

        # Test keyword embedded in a longer sentence
        result = await session.run(
            user_input="Yesterday I went to the store and bought some cherry tomatoes"
        )

        event = result.expect.next_event().is_message(role="assistant")
        actual_content = event._event.item.text_content  # type: ignore
        assert actual_content == "I don't like fruit"


@pytest.mark.asyncio
async def test_custom_keywords_and_response() -> None:
    """Test that custom keywords and response text work correctly."""
    base_llm = SimpleMockLLM(response_text="Normal response")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["pizza", "pasta"],
        response_text="I prefer healthy food",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())

        # Test custom keyword
        result = await session.run(user_input="Do you like pizza?")
        event = result.expect.next_event().is_message(role="assistant")
        actual_content = event._event.item.text_content  # type: ignore
        assert actual_content == "I prefer healthy food"

        # Test non-keyword still delegates
        result = await session.run(user_input="What about salad?")
        event = result.expect.next_event().is_message(role="assistant")
        actual_content = event._event.item.text_content  # type: ignore
        assert actual_content == "Normal response"


@pytest.mark.asyncio
async def test_no_more_events_after_interception() -> None:
    """Test that there are no additional events after keyword interception."""
    base_llm = SimpleMockLLM(response_text="Normal response")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["apple"],
        response_text="I don't like fruit",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())
        result = await session.run(user_input="I love apples")

        result.expect.next_event().is_message(role="assistant")
        result.expect.no_more_events()
