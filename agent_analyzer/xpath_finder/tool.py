"""
XPath Finder Tool for Google ADK Agents

The main tool function that can be passed to any ADK agent.
Matches the output quality of the original find_xpath.py.
"""

import re
from .browser import get_page
from .xpath import get_element_info
from .matching import similarity, id_similarity


# Attributes to check for matching (same as original)
MATCHABLE_ATTRIBUTES = ['id', 'name', 'class', 'data-testid', 'aria-label', 
                        'placeholder', 'title', 'value', 'alt']


def _parse_hint(hint: str) -> str:
    """
    Extract the search text from a hint string.
    Handles formats like: "text='Login'", "label='Email'", or just "Login"
    """
    patterns = [
        r"text=['\"]([^'\"]+)['\"]",
        r"label=['\"]([^'\"]+)['\"]",
        r"placeholder=['\"]([^'\"]+)['\"]",
        r"aria-label=['\"]([^'\"]+)['\"]",
        r"^['\"]([^'\"]+)['\"]$",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, hint, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return hint.strip()


async def find_xpath(url: str, hint: str, element_type: str = "*", top_n: int = 5) -> list[dict]:
    """Find XPath locators for a web element using fuzzy text matching.

    This tool searches for a single element on a webpage using multiple strategies:
    1. Playwright native locators (text, role, label, placeholder)
    2. Fuzzy text matching (difflib-based scoring)
    3. Normalized attribute matching (id, name, class, data-testid, aria-label, etc.)

    It returns a ranked list of XPath candidates, sorted by confidence score.

    Args:
        url: The full URL of the webpage to search (e.g., "https://example.com/login").
        hint: Text hint to identify the element. Can be a label, placeholder, button text, or partial text.
              Examples: "Login", "Submit Button", "Enter email", "text='Let's Start'".
        element_type: Optional HTML tag to filter results. Defaults to "*" (all tags).
                      Common values: "button", "input", "a", "div".
        top_n: Number of top-ranked candidates to return. Defaults to 5.

    Returns:
        List of dictionaries, where each dictionary represents a candidate locator:
        [
            {
                "xpath": "//button[text()='Login']",  # The XPath expression
                "confidence": 0.95,                   # Match confidence (0.0 to 1.0)
                "tag": "button",                      # Element tag name
                "text": "Login",                      # Element inner text
                "match_count": 1,                     # Number of elements matching this XPath
                "attributes": {"id": "btn-login"},    # Element attributes
                "strategy": "playwright_native",      # Matching strategy used
                "css": "#btn-login"                   # CSS selector
            },
            ...
        ]
    """
    page = await get_page(url)
    search_text = _parse_hint(hint)
    candidates = []
    
    # Strategy 1: Playwright native locators
    await _find_via_playwright(page, search_text, element_type, candidates)
    
    # Strategy 2: Fuzzy text matching
    await _find_via_fuzzy_text(page, search_text, element_type, candidates)
    
    # Strategy 3: Attribute matching
    await _find_via_attributes(page, search_text, element_type, candidates)
    
    # Deduplicate, sort, return top N
    return _rank_candidates(candidates, top_n)


async def find_multiple_xpath(url: str, hints: list[str], top_n: int = 3) -> dict[str, list[dict]]:
    """Find XPath locators for multiple elements on the same page efficiently.

    This tool is optimized for batch processing. It loads the webpage once and then
    performs element discovery for each hint in the provided list.

    Args:
        url: The full URL of the webpage to search.
        hints: A list of text hints to search for.
               Example: ["Username input", "Password field", "Sign in button"]
        top_n: Number of candidates to return per hint. Defaults to 3.

    Returns:
        A dictionary mapping each hint to its list of locator candidates.
        {
            "Username input": [
                {"xpath": "//input[@name='user']", "confidence": 0.9, ...},
                ...
            ],
            "Password field": [ ... ]
        }
    """
    page = await get_page(url)
    results = {}
    
    for hint in hints:
        search_text = _parse_hint(hint)
        candidates = []
        
        await _find_via_playwright(page, search_text, "*", candidates)
        await _find_via_fuzzy_text(page, search_text, "*", candidates)
        await _find_via_attributes(page, search_text, "*", candidates)
        
        results[hint] = _rank_candidates(candidates, top_n)
        
    return results


async def _find_via_playwright(page, search_text: str, element_type: str, candidates: list):
    """Strategy 1: Use Playwright's built-in locators."""
    
    locator_attempts = [
        # Exact text match (case-insensitive)
        (lambda: page.get_by_text(search_text, exact=False), 0.95, "playwright_text"),
        # Label
        (lambda: page.get_by_label(re.compile(search_text, re.I)), 0.88, "playwright_label"),
        # Placeholder
        (lambda: page.get_by_placeholder(re.compile(search_text, re.I)), 0.85, "playwright_placeholder"),
    ]
    
    # Add role-based locator if element_type is specified
    if element_type != "*":
        locator_attempts.insert(1, (
            lambda: page.get_by_role(element_type, name=re.compile(search_text, re.I)),
            0.90,
            "playwright_role"
        ))
    
    for locator_fn, base_confidence, strategy in locator_attempts:
        try:
            locator = locator_fn()
            count = await locator.count()
            if count > 0:
                info = await get_element_info(page, locator.first)
                
                # Adjust confidence based on match quality
                if info.get("text"):
                    sim = similarity(search_text, info["text"])
                    confidence = base_confidence * (0.5 + 0.5 * sim)
                else:
                    confidence = base_confidence * 0.8
                
                # Penalize if multiple matches
                if count > 1:
                    confidence *= 0.85
                
                candidates.append({
                    **info,
                    "confidence": round(confidence, 3),
                    "strategy": strategy
                })
        except:
            pass


async def _find_via_fuzzy_text(page, search_text: str, element_type: str, candidates: list):
    """Strategy 2: Fuzzy text matching using difflib."""
    selector = element_type if element_type != "*" else "button, a, input, label, span, div, h1, h2, h3, p, li"
    
    try:
        elements = await page.locator(selector).all()
        for el in elements[:100]:  # Limit to prevent slowdown
            try:
                text = await el.inner_text(timeout=1000)
                if not text or len(text) > 200:
                    continue
                
                sim = similarity(search_text, text)
                
                if sim >= 0.5:
                    info = await get_element_info(page, el)
                    # Maps 0.5-1.0 to 0.6-1.0
                    confidence = 0.6 + (sim - 0.5) * 0.8
                    
                    candidates.append({
                        **info,
                        "confidence": round(confidence, 3),
                        "strategy": "fuzzy_text_match"
                    })
            except:
                pass
    except:
        pass


async def _find_via_attributes(page, search_text: str, element_type: str, candidates: list):
    """Strategy 3: Match against element attributes (id, name, class, etc.)."""
    tag = element_type if element_type != "*" else "*"
    
    for attr in MATCHABLE_ATTRIBUTES:
        try:
            elements = await page.locator(f"{tag}[{attr}]").all()
            for el in elements[:50]:
                try:
                    attr_value = await el.get_attribute(attr, timeout=1000)
                    if not attr_value:
                        continue
                    
                    # Calculate ID-style similarity
                    sim = id_similarity(search_text, attr_value)
                    
                    if sim >= 0.6:
                        info = await get_element_info(page, el)
                        
                        # Confidence based on attribute type and similarity
                        base_conf = 0.85 if attr in ['id', 'data-testid'] else 0.75
                        confidence = base_conf * sim
                        
                        candidates.append({
                            **info,
                            "confidence": round(confidence, 3),
                            "strategy": f"attribute_match_{attr}"
                        })
                except:
                    pass
        except:
            pass


def _rank_candidates(candidates: list, top_n: int) -> list:
    """Deduplicate by xpath, sort by confidence, add rank."""
    seen = {}
    for c in candidates:
        key = (c.get("xpath", ""), c.get("tag", ""))
        if key[0] and (key not in seen or seen[key]["confidence"] < c["confidence"]):
            seen[key] = c
    
    result = sorted(seen.values(), key=lambda x: x["confidence"], reverse=True)[:top_n]
    for i, c in enumerate(result, 1):
        c["rank"] = i
    return result
