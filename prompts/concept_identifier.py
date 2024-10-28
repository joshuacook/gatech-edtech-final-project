# prompts/concept_identifier.py

concept_identifier_prompt = """
## Task Summary

You are an extractor of terminology from company documentation. Terminology means any named entity,
whether publicly known or internal to the company. For something to classify as a term, it must:

- Be a word or phrase that is unlikely to be understood by someone outside the company.
- Be no more than a few words long.
- Be defined within the documentation you are searching.

Your goal is to take a given document and identify all the terms within it. You do not need to extract
the definition.

Take care not to include terms that are already present in the list of terms you have already extracted.
That list is provided below, under "Current Terms".

Take care not to extract multiple versions of the same term.

This is essentially a Named Entity Recognition (NER) task.

## Example

Given the following document:

```
The company's primary goal is to increase the number of DAUs of OurEngine. A DAU is defined as
someone who has logged in within the last 30 days.
```

The expected extracted terms are:
- "DAU"
- "OurEngine"

Note how in this case OurEngine was not defined in the content, but it was present, and that was enough to
classify it as a term.

## Output Format

Return each term in its own <term>...</term> tag, one per line.

## Current Terms

You already know about a number of terms, and you should take care not to extract terms that are similar to
ones you already know. Here are the terms you already know:
<CurrentTerms>
{current_terms_xml_list}
</CurrentTerms>

## Context

The document you are working with is below. It is surrounded in triple backticks.

```
{asset_content}
```

## Answer Format

Please think through your answer carefully, and share your thoughts and reasoning before outputting your final
list. When you're ready, provide the list in <term>...</term> tags, one per line, as mentioned.
"""

reflections_prompt = """
Consider each of the terms you just extracted. You are going to try to filter this list down.

- If any of them mean roughly the same thing as something from the list of current terms, remove them.
- If any of them are common parlance or otherwise not specific to the source document, remove them.
- If any of them are synonomous with each other, keep the most specific one, and discard the others.

Talk through your thought process and reasoning for each before outputting your final list.

Once you have finalized your thoughts, output the filtered list in the same XML format as before.
"""
