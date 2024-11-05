# prompts/concept_definer.py

concept_definer_prompt = """
## Task Summary

Your goal is to synthesize given sources about [TARGET_TERM] into a concise definition.
You should include only highly relevant information about [TARGET_TERM]. Consider a definition this way:

What you are given is all the facts that an expert on [TARGET_TERM] would know. The definition contains only the
information one would need in order to gain a _functional_ understanding of what [TARGET_TERM] is, not to
become an expert on it. To liken it to an API, the sources you are given are the implementation details,
and the definition you are creating is the public interface.
In other words, someone can read the definition you provide and understand what [TARGET_TERM] is at a high level,
without necessarily learning all the details. The details are the sources you are given.
As such, your definition should not typically be longer than 1-2 sentences.

You can use terminology found in the provided information if it is relevant to the definition, and you do not
need to explain it as part of the definition; assume complete understanding of any required terminology.

Please ensure that your definition _describes [TARGET_TERM]_. Typically, this means that the term
is the subject of the sentence. The subject of the definition should not be any other term or concept.

It may be the case that you already know [TARGET_TERM]. Resist responding with a definition based on your
prior knowledge. The goal of the definition is that it is exclusively based on the provided context.

## Example

Given the following information about "machine learning":
- Machine learning is a type of artificial intelligence (AI) that provides computers with the ability to learn
    without being explicitly programmed.
- Machine learning focuses on the development of computer programs that can access data and use it to learn.
- The process of learning begins with observations or data, such as examples, direct experience, or instruction,
    to look for patterns in data and make better decisions in the future based on the examples that we provide.

You might synthesize this information into the following definition:
"Machine learning is a type of artificial intelligence that enables computers to learn from data and make
decisions without being explicitly programmed."

## Context

The information you are working with is below. It is surrounded in triple backticks. Each source is separated
by a horizontal rule.

```
{context}
```

## Target Term

[TARGET_TERM] is: "{term}"
"""
