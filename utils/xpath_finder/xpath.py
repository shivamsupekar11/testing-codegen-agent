"""XPath generation logic using JavaScript evaluation."""

from playwright.async_api import Page

# JavaScript to extract robust XPath from an element (same as original find_xpath.py)
_GET_ELEMENT_INFO_JS = """
(el) => {
    /**
     * Escape text for XPath single quotes
     */
    function escapeXPathText(text) {
        if (!text) return '""';
        if (text.indexOf("'") !== -1) {
            return "concat('" + text.replace(/'/g, "', \\\"'\\\", '") + "')";
        }
        return `'${text}'`;
    }

    /**
     * Count elements matching an XPath
     */
    function countXPath(xpath) {
        try {
            const result = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            return result.snapshotLength;
        } catch (e) {
            return 0;
        }
    }

    /**
     * Generate robust XPath by combining attributes until unique
     */
    function getRobustXPath(element) {
        const tag = element.tagName.toLowerCase();
        
        // Collection of XPath parts (predicates)
        const predicates = [];
        
        // 1. ID (usually unique, but check)
        if (element.id && !element.id.match(/^[0-9]|:/)) {
             const xpath = `//${tag}[@id='${element.id}']`;
             if (countXPath(xpath) === 1) return {xpath, count: 1};
             predicates.push(`@id='${element.id}'`);
        }
        
        // 2. data-testid
        const testId = element.getAttribute('data-testid');
        if (testId) {
            predicates.push(`@data-testid='${testId}'`);
        }

        // 3. Name
        const name = element.getAttribute('name');
        if (name) {
            predicates.push(`@name='${name}'`);
        }
        
        // 4. Input specific attributes
        if (tag === 'input') {
            const type = element.getAttribute('type');
            if (type) predicates.push(`@type='${type}'`);
            
            const value = element.getAttribute('value');
            if (value && value.length < 20) predicates.push(`@value='${value}'`);
            
            const placeholder = element.getAttribute('placeholder');
            if (placeholder) predicates.push(`@placeholder='${placeholder}'`);
        }

        // 5. Text content (for certain tags)
        const textContent = element.innerText?.trim();
        if (textContent && textContent.length > 0 && textContent.length < 50) {
             if (['button', 'a', 'label', 'span', 'h1', 'h2', 'h3', 'h4', 'p', 'div', 'li'].includes(tag)) {
                 const escaped = escapeXPathText(textContent);
                 predicates.push(`contains(normalize-space(.), ${escaped})`);
             }
        }
        
        // 6. Meaningful Classes
        if (element.className && typeof element.className === 'string') {
            const classes = element.className.split(' ').filter(c => 
                c && c.length > 2 && 
                !c.match(/^(btn|col-|row|container|wrapper|active|disabled|hidden|show|flex|grid|mt-|mb-|pt-|pb-|px-|py-|mx-|my-|[0-9])/)
            );
            classes.slice(0, 2).forEach(c => {
                predicates.push(`contains(@class, '${c}')`);
            });
        }
        
        // 7. Aria label
        const ariaLabel = element.getAttribute('aria-label');
        if (ariaLabel) predicates.push(`@aria-label='${ariaLabel}'`);
        
        // --- Strategy: Combine predicates to find unique match ---
        
        // Try single best predicate
        for (const pred of predicates) {
            const xpath = `//${tag}[${pred}]`;
            const count = countXPath(xpath);
            if (count === 1) return {xpath, count};
        }
        
        // Try combining best predicates (e.g. tag[attr1 and attr2])
        if (predicates.length > 1) {
            const combined = predicates.slice(0, 3).join(' and ');
            const xpath = `//${tag}[${combined}]`;
            const count = countXPath(xpath);
            if (count === 1) return {xpath, count};
            
            // If count > 1 but reasonable, return it
            if (count < 5) return {xpath, count};
        }

        // --- Strategy: Add Parent Context ---
        let parent = element.parentElement;
        if (parent) {
            let parentXPath = "";
            if (parent.id) parentXPath = `//*[@id='${parent.id}']`;
            else if (parent.getAttribute('data-testid')) parentXPath = `//*[@data-testid='${parent.getAttribute('data-testid')}']`;
            else if (parent.className) {
                const pClass = parent.className.split(' ')[0];
                if (pClass) parentXPath = `//*[contains(@class, '${pClass}')]`;
            }
            
            if (parentXPath) {
                const childPred = predicates.length > 0 ? `[${predicates.slice(0,2).join(' and ')}]` : '';
                const xpath = `${parentXPath}//${tag}${childPred}`;
                const count = countXPath(xpath);
                if (count === 1) return {xpath, count};
            }
        }
        
        // --- Fallback: Indexing ---
        let baseXPath = `//${tag}`;
        if (predicates.length > 0) {
            baseXPath += `[${predicates.slice(0, 2).join(' and ')}]`;
        }
        
        const siblings = document.evaluate(baseXPath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0; i < siblings.snapshotLength; i++) {
            if (siblings.snapshotItem(i) === element) {
                return {xpath: `(${baseXPath})[${i+1}]`, count: 1};
            }
        }

        return {xpath: baseXPath, count: siblings.snapshotLength};
    }
    
    const xpathInfo = getRobustXPath(el);
    
    const attrs = {};
    for (const attr of el.attributes) {
        attrs[attr.name] = attr.value;
    }
    
    let css = el.tagName.toLowerCase();
    if (el.id) css = `#${el.id}`;
    else if (el.className && typeof el.className === 'string') {
         const firstClass = el.className.split(' ')[0];
         if (firstClass) css += `.${firstClass}`;
    }
    
    return {
        xpath: xpathInfo.xpath,
        match_count: xpathInfo.count,
        css: css,
        tag: el.tagName.toLowerCase(),
        text: el.innerText?.trim().substring(0, 200) || '',
        attributes: attrs
    };
}
"""


async def get_element_info(page: Page, element) -> dict:
    """Extract xpath and metadata from a Playwright element."""
    try:
        handle = await element.element_handle()
        return await page.evaluate(_GET_ELEMENT_INFO_JS, handle)
    except:
        return {"xpath": "", "match_count": 0, "css": "", "tag": "", "text": "", "attributes": {}}
